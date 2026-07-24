# Sobe o ambiente de desenvolvimento do InfraHub (hot-reload em backend e frontend).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".env")) {
    Write-Host "Arquivo .env nao encontrado. Copiando .env.example -> .env"
    Copy-Item ".env.example" ".env"
}

docker compose up --build @args
