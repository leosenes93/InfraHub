# k3s — InfraHub

O núcleo da aplicação também roda em [k3s](https://k3s.io/) — a distribuição leve de Kubernetes da Rancher/SUSE, empacotada como um binário único. Reaproveita o mesmo chart Helm da Fase 6 (`k8s/infrahub/`), sem nenhum ajuste de manifest — só um `values-k3s.yaml` por fora.

## Por que k3s, além do OpenShift Local

Depois de validar o OpenShift Local (`docs/openshift.md`), a pegada de recursos dele (VM de 12GB RAM / 60GB disco fixo, só pra rodar o control plane completo + dezenas de operators) mostrou ser pesada demais pro disco NVMe de entrada da máquina (Kingston NV2, QLC, sem DRAM própria — degrada bastante sob escrita sustentada). k3s ataca o mesmo problema pela raiz: em vez de otimizar *como* o disco é usado, reduz *quanto* precisa ser usado — é um único binário, sem o ecossistema completo de operators do OpenShift, cabendo confortavelmente numa VM de 2GB RAM / 20GB disco.

## Topologia

VM `sjo-k3s-01` (Ubuntu Server 24.04 LTS, Gen2, Secure Boot ligado), single-node, IP estático `192.168.2.53` na mesma rede das DCs — diferente do OpenShift Local, que só é alcançável via túnel em `127.0.0.1` no host Windows, essa VM tem IP real na LAN, então não precisa de nenhum truque de rede (`netsh portproxy`, NodePort, etc.) para ser alcançada.

## Instalação

```bash
curl -sfL https://get.k3s.io | sh -
```

Um único comando instala o binário, registra o serviço systemd (`k3s.service`) e sobe um cluster funcional (control plane + `local-path-provisioner` para PVCs + `Traefik` como Ingress Controller + `CoreDNS` + `metrics-server`) em menos de um minuto — bem mais rápido que o CRC.

## Bugs reais encontrados e corrigidos

### 1. VM Ubuntu falha o boot com "Start PXE over IPv4" em vez de carregar o instalador

A VM (Generation 2, Secure Boot ligado) pulava direto pro boot de rede, ignorando o DVD com o ISO do Ubuntu. Causa: o **template de Secure Boot** padrão do Hyper-V (`MicrosoftWindows`) só confia no bootloader assinado da Microsoft — distros Linux usam um `shim` assinado por um certificado diferente (`MicrosoftUEFICertificateAuthority`), que não é confiável sob o template padrão. Sem esse template certo, o firmware rejeita silenciosamente o boot do DVD e cai pro próximo item da ordem de boot.

**Fix**:
```powershell
Set-VMFirmware -VMName "sjo-k3s-01" -SecureBootTemplate MicrosoftUEFICertificateAuthority
```

### 2. Partição raiz usava metade do disco alocado

`df -h /` mostrava só 9,8GB, mesmo com um VHDX de 20GB — o instalador do Ubuntu (particionamento guiado com LVM) não aloca 100% do disco pro volume lógico raiz por padrão, deixando espaço livre não usado no volume group. Isso causou pressão de disco (`ephemeral-storage`) rapidinho, derrubando pods em produção normal (Docker + build cache + imagens).

**Fix**:
```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```
Depois de redimensionar, o kubelet ainda mostrou `DiskPressure: True` por um tempo (parece cachear a condição) — um `sudo systemctl restart k3s` forçou reavaliação imediata.

**Efeito colateral da pressão de disco**: o garbage collector de imagens do containerd apagou as imagens do InfraHub importadas manualmente (`k3s ctr images import`) enquanto elas não estavam referenciadas por nenhum Pod rodando — precisou reimportar depois de resolver o espaço.

### 3. Senha do Postgres com caracteres especiais quebrava a URL de conexão — duas vezes

O chart monta `DATABASE_URL` como `postgresql+psycopg://user:senha@host/db`. Duas rodadas de senha geradas aleatoriamente (`GeneratePassword` do .NET) quebraram esse parsing de formas diferentes:
1. Um `@` dentro da senha foi interpretado como o separador usuário:senha**@**host, fazendo o SQLAlchemy tentar resolver um host inválido tipo `c0[@infrahub-postgres`.
2. Depois de corrigir isso, um `+` na segunda senha gerada também quebrou — sendo tratado como espaço em algum ponto do parsing da URL (comportamento de `application/x-www-form-urlencoded`, que alguns parsers aplicam de forma ampla demais).

Confirmado isolando a causa: `psql` direto com a senha exata (via `PGPASSWORD`, sem passar por URL) autenticava normalmente; só a versão em URL falhava.

**Fix definitivo**: gerar segredos usados em DSN/URL restritos ao conjunto "unreserved" da RFC 3986 (alfanuméricos + `. _ ~ -`), garantido seguro em qualquer posição de uma URI:
```powershell
do {
  $pw = [System.Web.Security.Membership]::GeneratePassword(24, 0)
} while ($pw -match '[^a-zA-Z0-9._~-]')
```

## Build e deploy do InfraHub

Sem Docker Desktop disponível (removido do host junto com o WSL2), as imagens são construídas **dentro da própria VM**, que já é uma máquina Linux de verdade:

```bash
# na VM sjo-k3s-01
sudo apt-get install -y docker.io docker-buildx git
git clone https://github.com/leosenes93/InfraHub.git
cd InfraHub
sudo DOCKER_BUILDKIT=1 docker build --target prod -t infrahub-backend:prod ./backend
sudo DOCKER_BUILDKIT=1 docker build -f infra/nginx/Dockerfile.prod -t infrahub-web:prod .

# importa direto pro containerd do k3s, sem precisar de registry
sudo sh -c "docker save infrahub-backend:prod | k3s ctr images import -"
sudo sh -c "docker save infrahub-web:prod | k3s ctr images import -"
```

O pacote `docker.io` do Ubuntu não inclui o plugin `buildx` por padrão — precisa do pacote `docker-buildx` separado pra habilitar o `DOCKER_BUILDKIT=1` (usado pelos `--mount=type=cache` do Dockerfile).

```bash
helm install infrahub k8s/infrahub -f k8s/infrahub/values-k3s.yaml
```

Sem SCC, sem `anyuid`, sem ajuste de permissão pro Postgres — o modelo de segurança padrão do k3s é bem menos restritivo que o do OpenShift.

### Ingress

`ingress.className: traefik` — o Traefik já vem embutido no k3s por padrão, sem precisar instalar nada.

## Observabilidade (Prometheus + Grafana) e Zabbix

Mesmo padrão de manifests simples (sem Helm) em `k8s/monitoring/` e `k8s/zabbix/`, aplicados direto com `kubectl apply -f`:

- **Prometheus** faz *service discovery* nativo do Kubernetes: coleta métricas de container/node via o endpoint cAdvisor embutido no kubelet (`kubernetes-nodes-cadvisor`), e de qualquer Pod anotado com `prometheus.io/scrape: "true"` (ex.: o backend do InfraHub, que já expõe `/metrics`).
- **Grafana** com o datasource do Prometheus provisionado como código (`ConfigMap` montado em `/etc/grafana/provisioning/datasources`) — sem clicar em nada na UI pra configurar.
- **Zabbix**: os mesmos manifests criados para o OpenShift (Fase 8), só trocando a `Route` por um `Ingress` do Traefik. Os agentes das VMs `sjo-dc-01`/`sjo-dc-02` foram reconfigurados (`Server`/`ServerActive` no `zabbix_agent2.conf`) para reportar pro novo servidor em `192.168.2.53:31051` (NodePort do trapper) — sem precisar de `netsh portproxy`, já que a VM tem IP real na LAN.

### Bug real: variáveis `VITE_*` não chegavam no frontend

Depois de subir Grafana/Zabbix, os atalhos "Monitoramento"/"Zabbix" no InfraHub continuavam não aparecendo. Causa: `infra/nginx/Dockerfile.prod` não declarava `ARG`/`ENV` para `VITE_GRAFANA_URL`/`VITE_ZABBIX_URL` — o Vite embute essas variáveis no bundle estático **durante o build**, não em runtime, então passá-las como variável de ambiente do container (como o `values-k3s.yaml` fazia) nunca teria efeito nenhum. Corrigido declarando `ARG` com valor padrão e promovendo para `ENV` antes do `RUN npm run build`, permitindo configurar via `--build-arg` no momento certo:
```bash
docker build -f infra/nginx/Dockerfile.prod \
  --build-arg VITE_GRAFANA_URL=http://grafana.k3s.local \
  --build-arg VITE_ZABBIX_URL=http://zabbix.k3s.local \
  -t infrahub-web:prod .
```

## Painel do cluster (Headlamp)

O [Kubernetes Dashboard](https://github.com/kubernetes/dashboard) oficial está **arquivado** (sem manutenção) — o próprio projeto recomenda o [Headlamp](https://headlamp.dev/), mantido pelo sig-ui do Kubernetes, como substituto:
```bash
helm repo add headlamp https://kubernetes-sigs.github.io/headlamp/
helm install headlamp headlamp/headlamp --namespace kube-system
kubectl create token headlamp --namespace kube-system --duration=8760h
```
O chart já cria a ServiceAccount `headlamp`; um `ClusterRoleBinding` pra `cluster-admin` (`k8s/monitoring/06-headlamp-ingress.yaml`) permite login completo com o token gerado.

## Acesso

- InfraHub: `http://infrahub.k3s.local`
- Grafana: `http://grafana.k3s.local` (usuário `admin`, senha em `k8s/monitoring/05-secret.yaml`, não versionado)
- Zabbix: `http://zabbix.k3s.local` (login inicial `Admin`/`zabbix` — trocar antes de expor além da rede local)
- Painel do cluster (Headlamp): `http://dashboard.k3s.local` (login via token de ServiceAccount, `kubectl create token headlamp -n kube-system`)

Todos os hosts apontam direto pro IP real da VM (`192.168.2.53`), sem túnel — diferente do CRC/OpenShift Local.

## Verificação feita

Cluster validado de ponta a ponta: todos os Pods (`backend`, `web`, `postgres`, `redis`, `zabbix-*`, `prometheus`, `grafana`, `headlamp`) saudáveis, migração do banco aplicada no start do backend, login real via `POST /api/v1/auth/login` retornando um token JWT válido através do Traefik, Prometheus com scrape targets saudáveis (nó real do cluster), Grafana autenticando e consultando o datasource, e os dois agentes Zabbix das DCs reportando dados reais (CPU, uptime, ping) para os hosts recriados no novo servidor.
