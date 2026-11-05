# cribado_llm_azure.ps1 - Q15: piloto de cribado con modelos abiertos en Azure spot (Standard_NC24ads_A100_v4)
# Adaptado de experimentos-aislados/E001 nube/etiquetar_azure.ps1.
#
# Fases, en orden:
#   cuota     revisa la cuota spot (24 vCPU "Low-priority") en la region
#   crear     grupo de recursos + VM spot; SSH solo a tu IP; tope de precio y apagado automatico
#   preparar  instala drivers NVIDIA y reinicia la VM
#   instalar  instala Ollama (misma version que la local), baja los tres modelos e imprime sus IDs
#   lanzar    sube script, prompt y UNA entrada (sin etiquetas de referencia) y etiqueta en tmux (reanudable)
#   estado    progreso y temperatura de la GPU
#   bajar     trae las salidas y el registro del entorno a tu disco D:
#   borrar    elimina todo el grupo de recursos (deja de cobrar)
#
# Si Azure desaloja la VM: vuelve a correr -Fase lanzar con los mismos argumentos; sigue donde iba.

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("cuota", "crear", "preparar", "instalar", "lanzar", "estado", "bajar", "borrar")]
    [string]$Fase,
    [string]$OllamaVersion = "",
    [string]$Region = "eastus",
    [string]$Datos = "D:\RIPG_DATA\Q15_CRIBADO_LLM",
    [ValidateSet("seleccion", "validacion")]
    [string]$Mitad = "seleccion",
    [string[]]$Configs = @("C1", "C2", "C3", "C4"),
    [double]$PrecioMaxHora = 1.00,
    [int]$HorasMax = 6
)

$ErrorActionPreference = "Stop"
$RG = "rg-q15-cribado"
$VM = "vm-q15-cribado"
$Size = "Standard_NC24ads_A100_v4"
$User = "azureuser"
$Modelos = @("qwen3.8:27b", "gemma4:31b", "gpt-oss:120b")
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $Aqui "cribado_llm.py"
$Prompt = Join-Path $Aqui "PROMPT_CRIBADO_LLM.md"

function Get-Ip { (az vm show -d -g $RG -n $VM --query publicIps -o tsv).Trim() }

function Invoke-Remoto([string]$cmd) {
    ssh -o StrictHostKeyChecking=accept-new "$User@$(Get-Ip)" $cmd
    if ($LASTEXITCODE -ne 0) { throw "Fallo el comando remoto: $cmd" }
}

switch ($Fase) {

    "cuota" {
        az vm list-usage --location $Region -o table | Select-String -Pattern "Low-priority|NCADS_A100"
        Write-Host "`nNecesitas al menos 24 vCPU libres en 'Total Regional Low-priority vCPUs'."
    }

    "crear" {
        $miIp = (Invoke-RestMethod -Uri "https://api.ipify.org").Trim()
        az group create -n $RG -l $Region -o none
        az vm create -g $RG -n $VM --size $Size `
            --image "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest" `
            --priority Spot --eviction-policy Deallocate --max-price $PrecioMaxHora `
            --admin-username $User --generate-ssh-keys --os-disk-size-gb 256 `
            --public-ip-sku Standard --nsg-rule NONE -o table
        az network nsg rule create -g $RG --nsg-name "${VM}NSG" -n ssh-solo-mi-ip `
            --priority 1000 --source-address-prefixes "$miIp/32" --destination-port-ranges 22 `
            --access Allow --protocol Tcp -o none
        $apagado = (Get-Date).ToUniversalTime().AddHours($HorasMax).ToString("HHmm")
        az vm auto-shutdown -g $RG -n $VM --time $apagado -o none
        Write-Host "`nVM creada. SSH solo para $miIp. Topes: $PrecioMaxHora USD/h y apagado a las $HorasMax h ($apagado UTC)."
        Write-Host "Siguiente: -Fase preparar"
    }

    "preparar" {
        Invoke-Remoto ("sudo apt-get update -y && " +
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ubuntu-drivers-common tmux python3 && " +
            "sudo ubuntu-drivers install --gpgpu && " +
            "V=`$(dpkg -l | grep -oP 'libnvidia-compute-\K[0-9]+-server' | head -n1) && " +
            "echo Driver: `$V && " +
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nvidia-utils-`$V linux-modules-nvidia-`$V-azure")
        az vm restart -g $RG -n $VM -o none
        Invoke-Remoto "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv"
        Write-Host "`nGPU lista. Siguiente: -Fase instalar -OllamaVersion <version>"
    }

    "instalar" {
        if (-not $OllamaVersion) { throw "Pasa -OllamaVersion, p. ej. -OllamaVersion 0.40.14" }
        Invoke-Remoto "curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=$OllamaVersion sh"
        foreach ($m in $Modelos) { Invoke-Remoto "ollama pull $m" }
        Invoke-Remoto "ollama --version; ollama list"
        foreach ($m in $Modelos) { Invoke-Remoto "ollama show $m | head -n 20" }
        Write-Host "`nRegistra la version, los IDs y la cuantizacion de arriba en el registro de ejecucion ANTES de lanzar."
    }

    "lanzar" {
        $entrada = Join-Path $Datos "entrada_$Mitad.jsonl"
        if (-not (Test-Path $entrada)) { throw "No existe $entrada. Corre antes 'preparar' en tu PC." }
        az vm start -g $RG -n $VM -o none
        $ip = Get-Ip
        Invoke-Remoto "mkdir -p ~/q15/datos"
        scp $Script $Prompt "${User}@${ip}:~/q15/"
        scp $entrada "${User}@${ip}:~/q15/datos/"
        $cadena = ($Configs | ForEach-Object {
            "python3 -I ~/q15/cribado_llm.py etiquetar --entrada ~/q15/datos/entrada_$Mitad.jsonl --config $_ --datos ~/q15/datos"
        }) -join " && "
        Invoke-Remoto ("tmux has-session -t q15 2>/dev/null || tmux new -d -s q15 " +
            "'($cadena) 2>&1 | tee -a ~/q15/etiquetar.log'")
        Write-Host "`nEtiquetado de '$Mitad' con $($Configs -join ', ') corriendo. Revisa con: -Fase estado"
    }

    "estado" {
        Invoke-Remoto ("tail -n 3 ~/q15/etiquetar.log; " +
            "for f in ~/q15/datos/salida_*.jsonl; do [ -f `"`$f`" ] && echo `"`$(basename `$f): `$(wc -l < `$f)`"; done; " +
            "nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used --format=csv,noheader")
    }

    "bajar" {
        $ip = Get-Ip
        scp "${User}@${ip}:~/q15/datos/salida_*.jsonl" $Datos
        scp "${User}@${ip}:~/q15/etiquetar.log" (Join-Path $Datos "etiquetar_$Mitad.log")
        $info = Join-Path $Datos "nube_info_$Mitad.txt"
        ssh "$User@$ip" "date -u; ollama --version; ollama list; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv; sha256sum ~/q15/cribado_llm.py ~/q15/PROMPT_CRIBADO_LLM.md ~/q15/datos/*.jsonl" | Set-Content $info
        Write-Host "`nSalidas en $Datos. Entorno y hashes en $info."
    }

    "borrar" {
        az group delete -n $RG --yes --no-wait
        Write-Host "Borrando $RG. Confirma en unos minutos con: az group exists -n $RG"
    }
}
