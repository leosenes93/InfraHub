# OpenShift Local — InfraHub

O núcleo da aplicação também roda em [OpenShift Local](https://developers.redhat.com/products/openshift-local) (CRC — Code Ready Containers), a distribuição single-node gratuita do OpenShift para desenvolvimento e testes. O objetivo aqui é demonstrar orquestração em uma distribuição enterprise de Kubernetes (usada amplamente no mercado), reaproveitando o mesmo chart Helm da Fase 6 (`k8s/infrahub/`) com os ajustes que o OpenShift exige.

> OpenShift Local é explicitamente **para desenvolvimento/teste**, não produção (o próprio console web exibe esse aviso). As decisões abaixo (como liberar a SCC `anyuid`) refletem esse contexto — não são recomendadas para um cluster OpenShift real.

## Por que OpenShift Local, e não só o Kubernetes puro da Fase 6

O chart da Fase 6 já roda em qualquer Kubernetes (validado com `kind`). OpenShift adiciona uma camada de políticas de segurança mais restritiva por padrão (Security Context Constraints) e substitui/complementa `Ingress` por `Route` — rodar o mesmo chart aqui é o que realmente exercita essas diferenças, além de ser uma habilidade de mercado distinta (muita infraestrutura corporativa roda OpenShift, não Kubernetes vanilla).

## Recursos e memória estática

CRC **não suporta Memória Dinâmica** do Hyper-V — é uma limitação documentada da Red Hat, não uma escolha: o node único (etcd + kube-apiserver) fica instável se a memória for redimensionada em tempo real. A VM precisa de alocação fixa.

Configuração usada (`crc config set memory/cpus`): **12GB RAM / 4 vCPU** — abaixo dos 16GB "ideais" recomendados pela Red Hat, ajustado para caber no orçamento de RAM da máquina (32GB total, dividido com outras VMs). 9GB é o mínimo tecnicamente suportado.

## Bugs reais encontrados e corrigidos

Dois problemas genuínos apareceram validando isso de verdade neste host (Windows 11 + Kaspersky) — nenhum dos dois é specific de configuração exótica, então documentando para não repetir o diagnóstico:

### 1. `crc start` falha sempre em "Configuring shared directories" com "host file not writable"

O CRC tenta reescrever automaticamente o `hosts` do Windows a cada start (para os domínios `*.crc.testing`), mas **recusa rodar com privilégio de administrador** (bloqueio explícito no próprio binário) — e a escrita nesse arquivo exige elevação, que o mecanismo de ajuda dele (`crcAdminHelper`, serviço Windows rodando como `LocalSystem`) deveria prover automaticamente, mas não funcionou nesse ambiente. Nem ajustar a ACL do arquivo/pasta resolve por completo (a pasta `C:\Windows\System32\drivers\etc` é protegida pelo TrustedInstaller — nem uma sessão de Administrador comum consegue alterar a ACL dela sem tomar posse, o que é invasivo demais para fazer só por causa disso).

**Fix aplicado**: desligar a gestão automática e assumir a escrita manualmente.
```powershell
crc config set modify-hosts-file false
```
E adicionar manualmente ao `hosts` (como o Windows não suporta wildcard, cada hostname precisa de uma entrada literal; o IP é sempre `127.0.0.1` no driver Hyper-V do CRC, que usa tunelamento local):
```
127.0.0.1 api.crc.testing
127.0.0.1 canary-openshift-ingress-canary.apps-crc.testing
127.0.0.1 console-openshift-console.apps-crc.testing
127.0.0.1 default-route-openshift-image-registry.apps-crc.testing
127.0.0.1 downloads-openshift-console.apps-crc.testing
127.0.0.1 oauth-openshift.apps-crc.testing
```
Qualquer Route/hostname customizado (ex.: `infrahub.apps-crc.testing`) precisa da mesma entrada manual quando criado.

### 2. Startup extremamente lento, com fila de disco alta mesmo em NVMe

Um `crc stop` + `crc start` completo (necessário sempre que a VM é totalmente parada — os operators do OpenShift precisam reinicializar do zero) levou mais de 15 minutos na primeira tentativa "limpa", com `Current Disk Queue Length` de 7 e `% Disk Time` de 690% no drive NVMe (`Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk`). Causa: o antivírus de terceiros ativo na máquina (Kaspersky — o Windows Defender fica em modo passivo quando outro AV assume) escaneando em tempo real cada escrita das VMs no disco.

**Fix**: excluir manualmente as pastas das VMs no antivírus de terceiros (não dá pra automatizar como o `Add-MpPreference` do Defender — cada produto tem sua própria interface):
- `C:\VMs` (VMs do domínio, fora do escopo deste chart)
- `C:\Users\<usuario>\.crc` (VM do OpenShift Local)

## Build e deploy do InfraHub

Sem depender do Docker Desktop (que fica de fora dessa configuração): o OpenShift builda as imagens **dentro do próprio cluster**, via `BuildConfig` com estratégia Docker e upload binário do código local.

```bash
oc new-project infrahub
oc adm policy add-scc-to-user anyuid -z default -n infrahub   # ver nota abaixo

oc new-build --name=infrahub-backend --binary --strategy=docker -n infrahub
oc new-build --name=infrahub-web --binary --strategy=docker -n infrahub
oc patch bc/infrahub-web -n infrahub --type=json \
  -p '[{"op":"add","path":"/spec/strategy/dockerStrategy/dockerfilePath","value":"infra/nginx/Dockerfile.prod"}]'

cd backend && oc start-build infrahub-backend -n infrahub --from-dir=. --follow
cd .. && oc start-build infrahub-web -n infrahub --from-dir=. --follow
```

### Por que a SCC `anyuid`

O Postgres oficial (`postgres:16-alpine`) espera rodar com o UID que a própria imagem define (dono do diretório de dados). A SCC padrão do OpenShift (`restricted-v2`) força um UID arbitrário por Pod, incompatível com isso — o Postgres falharia ao iniciar por permissão no `/var/lib/postgresql/data`. Duas soluções possíveis: trocar a imagem por uma "OpenShift-friendly" (ex.: `registry.redhat.io/rhel8/postgresql-16`, que suporta UID arbitrário via grupo `0`), ou liberar `anyuid` para o service account do namespace. Optei pela segunda para não divergir da imagem já usada no Docker Compose/Kubernetes — aceitável aqui por ser um cluster de laboratório.

### Bugs reais corrigidos no build da imagem web (`infra/nginx/Dockerfile.prod`)

Builds do OpenShift rodam via Buildah **sem privilégio** (rootless) por padrão — isso expôs dois problemas que builds normais do Docker Desktop nunca pegam:

1. **Bit de execução perdido em `node_modules/.bin/*`**: `npm install` seguido de `npm run build` falhava com `tsc: Permission denied`. Corrigido com `RUN chmod -R +x node_modules/.bin` logo após o `npm install` (no-op em builds normais).
2. **`node_modules` do host vazando pro build**: o contexto de build da imagem web é a raiz do repositório, mas só existia um `.dockerignore` dentro de `frontend/` (que só se aplica quando o contexto é `frontend/`). Sem um `.dockerignore` na raiz, `COPY frontend/ .` sobrescrevia o `node_modules` recém-instalado (com permissões corretas) pelo `node_modules` local do Windows (sem bit de execução Unix) — mesmo sintoma do problema 1, causa diferente. Corrigido com um `.dockerignore` na raiz do repositório.

Essas duas correções também beneficiam qualquer outro pipeline de build rootless (ex.: GitHub Actions com Buildah/Kaniko), não são específicas do CRC.

### Ingress → Route

O chart usa um `Ingress` padrão (`ingressClassName`). No OpenShift, o controller `openshift-default` (`openshift.io/ingress-to-route`) traduz isso automaticamente em uma `Route` nativa — não precisa de manifests separados. Basta apontar `ingress.className: openshift-default` no `values` (ver `values-crc.yaml`, não versionado por conter segredos — veja `k8s/infrahub/values.yaml` para a lista de campos a sobrescrever).

## Acesso

- Console web do cluster: `https://console-openshift-console.apps-crc.testing` (login `kubeadmin`, senha gerada por `crc start`)
- InfraHub: `http://infrahub.apps-crc.testing` (ou o host configurado em `values-crc.yaml`)

## Limitações conhecidas / próximos passos

- **Builds via upload binário** (`--from-dir`): funciona, mas reenvia todo o contexto a cada build. Migrar para uma `BuildConfig` com `git` strategy (o repositório já é público) é uma melhoria natural — dispensa reenvio manual e se aproxima de um pipeline CI/CD real.
- **`anyuid`** é uma concessão de conveniência para este laboratório — um cluster OpenShift real usaria uma imagem de Postgres compatível com UID arbitrário em vez de relaxar a SCC.
- Sem TLS configurado nas Routes (HTTP simples, mesmo espírito da limitação já registrada em `docs/kubernetes.md` para o Ingress do Kubernetes puro).

## Verificação feita

Cluster validado de ponta a ponta, não só `helm template`: builds reais dentro do cluster, `helm install` com o chart da Fase 6, rollout de todos os Pods (`backend`, `web`, `postgres`, `redis`) saudáveis, migração do banco (`alembic upgrade head`, incluindo a migration `0006` da Fase 7) aplicada com sucesso no start do backend, e login real via `POST /api/v1/auth/login` retornando um token JWT válido através da Route.
