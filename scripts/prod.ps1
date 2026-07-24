# Sobe o ambiente de producao do InfraHub (imagens otimizadas, sem hot-reload).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".env")) {
    Write-Error "Arquivo .env nao encontrado. Copie .env.example para .env e ajuste os segredos antes de continuar."
    exit 1
}

docker compose -f docker-compose.prod.yml up --build -d @args
