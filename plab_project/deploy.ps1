# PLAB — Windows server / local: run from project root (folder with manage.py).
#   .\deploy.ps1
# Requires: Python on PATH; gettext for compilemessages (install gettext or use Git Bash deploy.sh).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
}

Write-Host "==> pip install"
py -m pip install -r requirements.txt

Write-Host "==> migrate"
py manage.py migrate --noinput

Write-Host "==> collectstatic"
py manage.py collectstatic --noinput

Write-Host "==> compilemessages (Arabic)"
py manage.py compilemessages -l ar

Write-Host "==> Done."
