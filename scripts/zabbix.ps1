# Sobe a stack de monitoramento de infraestrutura externa via Zabbix,
# acoplada ao ambiente principal.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".env")) {
    Write-Host "Arquivo .env nao encontrado. Copiando .env.example -> .env"
    Copy-Item ".env.example" ".env"
}

docker compose -f docker-compose.yml -f docker-compose.zabbix.yml up --build -d @args
