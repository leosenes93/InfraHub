# pfSense — segmentação de rede do lab

O lab (DCs + cluster k3s) deixou de ficar direto na LAN de casa e passou a viver atrás de um firewall/roteador [pfSense](https://www.pfsense.org/) (Community Edition), numa rede interna dedicada — a mesma ideia de uma rede corporativa isolada atrás de um firewall de borda, só que em miniatura.

## Por quê

Até aqui, `sjo-dc-01`, `sjo-dc-02` e `sjo-k3s-01` ficavam todas no mesmo vSwitch `External-Ethernet` (ligado à placa física, mesma rede do roteador de casa) — sem nenhuma segmentação entre o "lab" e o resto da rede doméstica, e sem experiência prática de NAT/roteamento real. O pfSense resolve isso: cria uma rede interna nova, roteada por ele, e permite testar o padrão "acesso externo → NAT → serviço interno" de verdade, usando a própria rede de casa como se fosse a internet.

## Topologia

```
                    ┌──────────────────────┐
   Rede de casa     │   pfSense-01 (VM)    │      Rede interna do lab
 192.168.2.0/24      │  WAN         LAN     │       10.1.1.0/24
 (papel de "WAN")────┤ .200         .1      ├──────┬─────────────────
                    └──────────────────────┘      │
                                                    ├── sjo-dc-01   .101
                                                    ├── sjo-dc-02   .102
                                                    └── sjo-k3s-01  .103
```

- **WAN** (`External-Ethernet`, vSwitch já existente): IP estático `192.168.2.200/24`, gateway `192.168.2.1` (o roteador de casa) — faz o papel de "internet" nesta simulação.
- **LAN** (`Internal-LabNet`, vSwitch novo, tipo **Internal** — dá IP também ao host físico, não só às VMs): `10.1.1.1/24`, DHCP `10.1.1.10`-`10.1.1.100` para clientes eventuais; as VMs do lab usam estático fora desse range (`.101`-`.103`) para não colidir com o pool.
- A máquina física continua do lado "WAN" (mesma rede do roteador) — todo acesso aos serviços internos passa por NAT no pfSense, simulando um cliente externo de verdade.

## Instalação

VM Gen1 (evita de propósito a mesma armadilha de Secure Boot/shim já resolvida com Linux na Fase 9 — Gen1 dispensa esse problema inteiramente), 2 vCPU, 2GB RAM, 20GB disco, 2 NICs.

A ISO da Community Edition não tem link direto de download — precisa passar pelo fluxo de carrinho/checkout gratuito da Netgate Store (`pfsense.org/download` → "AMD64 ISO IPMI/Virtual Machines"), sem custo mas sem automação possível.

```powershell
New-VMSwitch -Name "Internal-LabNet" -SwitchType Internal
New-VM -Name "pfSense-01" -Generation 1 -MemoryStartupBytes 2GB `
  -NewVHDPath "E:\VMs\pfSense-01\pfSense-01.vhdx" -NewVHDSizeBytes 20GB `
  -SwitchName "External-Ethernet"
Add-VMNetworkAdapter -VMName "pfSense-01" -Name "LAN" -SwitchName "Internal-LabNet"
```

## Bugs reais encontrados e corrigidos

### 1. Boot volta pro instalador depois de instalar

Comportamento clássico de VM Gen1: o drive de DVD continua com a ISO montada e primeiro na ordem de boot, então todo reboot pós-instalação volta a bootar o instalador em vez do sistema já instalado.

**Fix**: ejetar a ISO e priorizar o disco na ordem de boot.
```powershell
Set-VMDvdDrive -VMName "pfSense-01" -Path $null
Set-VMBios -VMName "pfSense-01" -StartupOrder @("IDE","CD","LegacyNetworkAdapter","Floppy")
```

### 2. GUI do pfSense inacessível pela LAN a partir do host físico

O `Internal-LabNet` foi criado inicialmente como switch **Private** (isolamento total, nem o host físico alcança) — combinava com o modelo "acesso só via NAT simulando externo", mas tornava inviável administrar o GUI do pfSense sem subir uma VM de salto toda vez. Trocado para **Internal** (dá uma placa de rede virtual ao host também), aceitando esse pequeno desvio do isolamento total em troca de conveniência administrativa — o teste de "acesso externo" da Fase 5 continua válido, pois ele testa os *serviços* via NAT pela WAN, não o GUI do firewall em si.

```powershell
Set-VMSwitch -Name "Internal-LabNet" -SwitchType Internal
```

### 3. pfSense bloqueia a própria "WAN" por padrão (Block private networks)

Com "acesso externo" HTTP 200 pro Ingress funcionando, RDP nas DCs configurado, e o WAN devidamente com IP estático — mesmo assim nada respondia pela WAN, nem ping. Causa: o pfSense, por padrão, assume que a WAN é a internet real e **bloqueia origens de faixas RFC1918** (`Block private networks and loopback addresses`) e bogons na interface WAN — proteção correta contra spoofing num cenário real, mas que aqui bloqueia justamente a rede de casa (`192.168.2.0/24`), que é privada e faz o papel de "WAN" nesta simulação.

**Fix**: desmarcar as duas opções em Interfaces → WAN.

### 4. RDP não respondia mesmo com a regra de NAT correta

A regra de NAT/port-forward pro RDP (`3389`/`3390` → `10.1.1.101`/`10.1.1.102`) estava certa, mas a conexão TCP nunca completava. Causa raiz: a regra de firewall do Remote Desktop nas duas DCs estava **desabilitada** (`Enabled: False`) — RDP nunca tinha sido de fato habilitado nessas VMs, independente da rede.

**Fix**: habilitar o RDP de verdade (registro + firewall), não só a regra de NAT.
```powershell
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
```

### 5. Reconstrução do k3s apagou os dados das aplicações, não só a infraestrutura

Migrar a `sjo-k3s-01` pra rede nova exigiu reinstalar o k3s do zero (o IP do node fica cravado nos certificados TLS internos do cluster, gerados na primeira instalação — reconfigurar no lugar arrisca quebrar a comunicação interna). O `k3s-uninstall.sh` limpa `/var/lib/rancher/k3s` por completo, incluindo o storage do `local-path-provisioner` — ou seja, os volumes persistentes do Postgres do InfraHub e do Zabbix (histórico, hosts cadastrados, senha trocada do Admin) também somem, não só o control plane. A infraestrutura (chart Helm, manifests) é toda IaC e reaplica em minutos; os *dados* dentro dela não sobrevivem a menos que haja backup separado do volume.

**Mitigação aplicada**: antes de desinstalar, os segredos (`values-k3s.yaml`, secrets do Zabbix/Grafana) foram extraídos direto dos objetos `Secret` do cluster ainda rodando (`kubectl get secret ... -o yaml` + decode base64) — como esses arquivos eram gitignored e nunca tinham sido versionados, essa foi a única cópia restante depois de uma formatação do host que também os apagou localmente.

### 6. Agente Zabbix na própria `sjo-k3s-01` rejeitava o pinger do Zabbix

Depois de recriar os hosts no Zabbix, `sjo-dc-01`/`sjo-dc-02` ficaram disponíveis rápido, mas `sjo-k3s-01` (que roda o próprio servidor Zabbix) ficava com erro "Connection reset by peer". Causa: o pod do `zabbix-server`, ao falar com o agente rodando no *mesmo node* onde ele está hospedado, não passa pelo SNAT normal de tráfego entre nodes — a conexão chega ao agente com o IP do pod (`10.42.0.x`, faixa interna do CNI) em vez do IP do node (`10.1.1.103`), e o `Server=` do agente só permitia esse último.

**Fix**: ampliar o allowlist do agente pra aceitar também a faixa de pods do cluster.
```bash
sed -i 's/^Server=10.1.1.103$/Server=10.1.1.103,10.42.0.0\/16/' /etc/zabbix/zabbix_agent2.conf
systemctl restart zabbix-agent2
```

### 7. `systemd-resolved` não conseguia resolver o domínio AD mesmo com os DNS certos configurados

Com os servidores DNS corretos (as duas DCs) configurados via netplan, consultas a `infrahub.local` ainda voltavam `SERVFAIL` — inclusive para os registros SRV que o `realm discover` precisa (`_ldap._tcp.infrahub.local`). Consultar as DCs diretamente (`nslookup infrahub.local 10.1.1.101`) funcionava normalmente, isolando o problema no `systemd-resolved` local: sem um *routing domain* explícito, ele não sabia que consultas para `infrahub.local` deveriam ir para os DNS configurados em `eth0`.

**Fix**: declarar `infrahub.local` como *search domain* do adaptador, tanto ao vivo quanto persistido no netplan.
```bash
resolvectl domain eth0 infrahub.local   # teste ao vivo
# e no netplan:
#   nameservers:
#     addresses: [10.1.1.101, 10.1.1.102]
#     search: [infrahub.local]
```

## Entrando a sjo-k3s-01 no domínio

Com o DNS resolvendo corretamente, o join usa o fluxo padrão do `realmd`/`sssd` em Ubuntu:

```bash
apt-get install -y realmd sssd sssd-tools adcli krb5-user packagekit
realm join infrahub.local -U Administrator
```

Validado com `realm list` (`configured: kerberos-member`) e `id administrator@infrahub.local` resolvendo corretamente via SSSD, com todos os grupos AD (Domain Admins, Enterprise Admins etc.).

## NAT / acesso externo simulado

Regras de Port Forward em Firewall → NAT, WAN → interno:

| WAN (porta) | Destino | Serviço |
| --- | --- | --- |
| 80 | `10.1.1.103:80` | Ingress do InfraHub (Traefik) |
| 3389 | `10.1.1.101:3389` | RDP `sjo-dc-01` |
| 3390 | `10.1.1.102:3389` | RDP `sjo-dc-02` |

Validado a partir da máquina física (do lado "WAN"/rede do roteador): `curl http://192.168.2.200/ -H "Host: infrahub.k3s.local"` retornando HTTP 200, e `Test-NetConnection 192.168.2.200 -Port 3389`/`3390` com `TcpTestSucceeded: True`.

## Verificação feita

Cluster e domínio validados de ponta a ponta pós-migração: replicação AD com `repadmin /syncall /AeD` (0 falhas nas duas direções), login JWT do InfraHub através do Ingress novo, os 3 hosts do inventário com `available: true` no Zabbix reconstruído, `sjo-k3s-01` como membro do domínio (`realm list`), e acesso "externo" real via NAT tanto para o InfraHub quanto para RDP nas duas DCs.
