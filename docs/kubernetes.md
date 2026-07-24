# Kubernetes — InfraHub

O núcleo da aplicação (backend, web/Nginx, Postgres, Redis) roda em Kubernetes via um chart Helm em [`k8s/infrahub/`](../k8s/infrahub/). O Docker Compose continua sendo o ambiente de desenvolvimento — este chart existe para demonstrar o caminho de produção em um cluster real, reaproveitando exatamente as mesmas imagens de produção já usadas em `docker-compose.prod.yml`.

## Mapeamento Compose → Kubernetes

| Docker Compose | Kubernetes | Observação |
| --- | --- | --- |
| `postgres` | `StatefulSet` (1 réplica) + `Service` headless + PVC (`volumeClaimTemplates`) | mesma imagem `postgres:16-alpine` |
| `redis` | `Deployment` + `Service` | cache, sem PVC |
| `backend` | `Deployment` + `Service` (nome fixo `backend`) | usa a imagem `prod` do `backend/Dockerfile` sem alterações — o próprio `ENTRYPOINT` da imagem roda `alembic upgrade head` antes de subir o Uvicorn, igual ao Compose |
| `nginx` (prod, com o frontend embutido) | `Deployment` + `Service` + `Ingress` | mesma imagem `infra/nginx/Dockerfile.prod`, mas com a configuração do Nginx sobrescrita via ConfigMap (ver abaixo) |
| `storage/uploads` (bind mount) | `PersistentVolumeClaim` (`ReadWriteOnce`) | ver limitação abaixo |
| `.env` | `ConfigMap` (não sensível) + `Secret` (senha do Postgres, `JWT_SECRET_KEY`, senha do admin inicial) | |
| `healthcheck` | `livenessProbe`/`readinessProbe` em `/api/v1/health` e `/api/v1/health/ready` (backend), `/healthz` (web) | reaproveita os mesmos endpoints |

A stack de observabilidade (Prometheus/Grafana/Loki/Portainer/Uptime Kuma) **não** ganhou manifests próprios — em um cluster real o caminho padrão de mercado é usar um chart pronto (ex.: [`kube-prometheus-stack`](https://github.com/prometheus-community/helm-charts)), não reescrever essas ferramentas à mão.

## Por que a configuração do Nginx é diferente da usada no Compose

A imagem `infra/nginx/Dockerfile.prod` embute `infra/nginx/conf.d/default.prod.conf`, que usa `resolver 127.0.0.11` (o DNS interno do Docker) para reresolver o hostname do backend a cada requisição — necessário porque, no Compose, um container recriado troca de IP e o Nginx cacheava o IP antigo (bug real encontrado e corrigido na Fase 3).

Em Kubernetes esse resolver **não existe** (127.0.0.11 não é roteável de dentro de um Pod) — e também não é necessário: o `Service` do backend tem um `ClusterIP` estável durante toda a vida do release, independente de quais Pods estejam por trás dele. Por isso o chart monta uma configuração alternativa (`k8s/infrahub/files/nginx-default.conf`, sem o resolver dinâmico) via `ConfigMap`, sobrescrevendo `/etc/nginx/conf.d/default.conf` na imagem — sem precisar gerar uma imagem nova.

## Pré-requisitos

- Um cluster Kubernetes com um **Ingress controller** instalado (ex.: `ingress-nginx`) se for usar o `Ingress` do chart (`ingress.enabled: true`, padrão).
- Para testar localmente: [`kind`](https://kind.sigs.k8s.io/) (usado para validar este chart) ou o Kubernetes embutido do Docker Desktop.
- `helm` e `kubectl` instalados.
- As imagens de produção construídas e disponíveis para o cluster:
  ```bash
  docker build --target prod -t infrahub-backend:prod ./backend
  docker build -f infra/nginx/Dockerfile.prod -t infrahub-web:prod .
  # com kind:
  kind load docker-image infrahub-backend:prod --name <cluster>
  kind load docker-image infrahub-web:prod --name <cluster>
  # em um cluster real: publique as imagens em um registry e ajuste
  # image.backend.repository / image.web.repository no values.yaml
  ```

## Instalação

```bash
helm install infrahub k8s/infrahub \
  --set postgres.password=<senha-forte> \
  --set secrets.jwtSecretKey=<chave-longa-aleatoria> \
  --set secrets.initialAdminPassword=<senha-forte>
```

Sem Ingress (ex.: cluster de teste sem controller instalado):

```bash
helm install infrahub k8s/infrahub --set ingress.enabled=false
kubectl port-forward svc/infrahub-web 8080:80
# http://localhost:8080
```

O `NOTES.txt` pós-instalação mostra a URL e lembra de trocar as credenciais padrão.

## Limitações conhecidas (deliberadamente fora do escopo desta fase)

- **Upload com múltiplas réplicas do backend**: o PVC de `storage/uploads` é `ReadWriteOnce` — funciona com `replicaCount.backend: 1` (padrão). Múltiplas réplicas exigiriam um volume `ReadWriteMany` (ex.: NFS) ou migrar para armazenamento de objeto (S3/MinIO).
- **Migração do banco com múltiplas réplicas**: como o backend roda `alembic upgrade head` no próprio start (mesmo comportamento do Compose), múltiplas réplicas subindo ao mesmo tempo rodam a migração em paralelo — `alembic upgrade head` é idempotente e seguro nesse cenário, mas o padrão mais robusto para produção com várias réplicas é migrar via um `Job` dedicado rodado antes do rollout (tentamos essa abordagem com hooks do Helm durante o desenvolvimento deste chart e encontramos um problema real de ordenação — hooks `pre-install` do Helm rodam **antes** de qualquer recurso normal existir no cluster, então um Job de migração não consegue depender do Postgres estar de pé só ajustando pesos de hook. A solução correta exigiria também tornar o Postgres um hook, o que tem implicações desagradáveis em `helm upgrade`. Optamos pela abordagem mais simples e correta para o escopo atual).
- **Sem TLS/cert-manager**: o `Ingress` é HTTP simples; adicionar TLS é um próximo passo natural.
- **Dois releases no mesmo namespace colidem**: o `Service` do backend tem nome fixo (`backend`, sem prefixo do release) porque a imagem do Nginx espera esse hostname — instalar dois releases deste chart no mesmo namespace exigiria mudar isso.

## Verificação feita durante o desenvolvimento deste chart

`helm lint` e `helm template` (validação estática) e, além disso, uma instalação real em um cluster `kind` descartável: build das imagens `prod`, `kind load docker-image`, `helm install --wait`, e testes via `kubectl port-forward` — login, `/api/v1/health/ready` e a página inicial do frontend respondendo corretamente através do `Service` do Nginx. Essa validação encontrou e corrigiu dois bugs reais:
1. `ConfigMap`/`Secret` referenciados pelo Job de migração ainda não existiam durante o hook `pre-install` (ver limitação acima) — motivou remover o Job e voltar a migrar no start do backend.
2. Condição de corrida no seed do usuário administrador inicial: com `--workers 4`, os processos do Uvicorn tentavam criar o mesmo admin simultaneamente, e o primeiro a commitar fazia os outros derrubarem o container inteiro com uma violação de unicidade. Esse bug já existia desde a Fase 1 no `docker-compose.prod.yml` (mesma flag `--workers 4`), só nunca tinha se manifestado de forma determinística nos testes anteriores. Corrigido em `UserService.ensure_initial_admin`, que agora trata essa corrida como não-erro.
