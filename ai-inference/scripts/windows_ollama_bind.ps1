<#
.SYNOPSIS
    Jericho Suite: Inference Server Network Binding
.DESCRIPTION
    Configures Ollama on the Windows node to accept incoming inference requests 
    from the Parrot OS Controller on the local network.
#>

Write-Host "[*] Reconfiguring Ollama API Bind Address..." -ForegroundColor Cyan

# Set Ollama to listen on all interfaces
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0", "Machine")

# Punch a hole in the Windows Firewall for the API
Write-Host "[*] Configuring Inbound Firewall Rule for port 11434..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "Jericho Ollama API" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue

Write-Host "[+] Success. Please restart the Ollama application for changes to take effect." -ForegroundColor Green
