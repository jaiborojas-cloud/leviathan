# cribado_llm_azure.ps1 - Q15: piloto de cribado con modelos abiertos en Azure spot (Standard_NC24ads_A100_v4)
# Adaptado de experimentos-aislados/E001 nube/etiquetar_azure.ps1.
#
# Fases, en orden:
#   cuota     revisa la cuota spot (24 vCPU "Low-priority") en la region
#   crear     grupo de recursos + VM spot; SSH solo a tu IP; tope de precio y apagado automatico
#   preparar  instala drivers NVIDIA y reinicia la VM
#   instalar  instala Ollama (misma version que la local), baja los tres modelos e imprime sus IDs
#   probar    sube script y prompt, revisa el formato de cada modelo con una obra inventada y baja probar.json
#   lanzar    sube script, prompt y UNA entrada (sin etiquetas de referencia) y etiqueta en tmux (reanudable)
#             seleccion: las configuraciones que pasaron "probar"; validacion: solo la de eleccion.json
#   estado    progreso y temperatura de la GPU
#   bajar     trae las salidas y el registro del entorno a tu disco D:
#   borrar    elimina todo el grupo de recursos (deja de cobrar)
#
# Si Azure desaloja la VM: vuelve a correr -Fase lanzar con los mismos argumentos; sigue donde iba.

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("cuota", "crear", "preparar", "instalar", "probar", "lanzar", "estado", "bajar", "borrar")]
    [string]$Fase,
    [string]$OllamaVersion = "",
    [string]$Region = "eastus",
    [string]$Datos = "D:\RIPG_DATA\Q15_CRIBADO_LLM",
    [ValidateSet("seleccion", "validacion")]
    [string]$Mitad = "seleccion",
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
$Particion = Join-Path $Aqui "particion.json"
# hashes congelados (PREREGISTRO_CRIBADO_LLM.md); si tu copia difiere, no se sube nada
$ShaScript = "a7d9a718af41966587cdd04944d5b5fa0e751c1eb3a53bf7833c66edd047fb40"
$ShaPrompt = "0d102764a522b0d09cbfd60fbc0d1fff375a99c40d254b52dafa9592a9d593f0"

function Get-Ip { (az vm show -d -g $RG -n $VM --query publicIps -o tsv).Trim() }

function Invoke-Remoto([string]$cmd) {
    ssh -o StrictHostKeyChecking=accept-new "$User@$(Get-Ip)" $cmd
    if ($LASTEXITCODE -ne 0) { throw "Fallo el comando remoto: $cmd" }
}

function Copiar([string[]]$origen, [string]$destino) {
    scp @origen $destino
    if ($LASTEXITCODE -ne 0) { throw "Fallo la copia: $($origen -join ', ') -> $destino" }
}

function Test-Sha([string]$ruta, [string]$esperado) {
    $real = (Get-FileHash $ruta -Algorithm SHA256).Hash.ToLower()
    if ($real -ne $esperado) { throw "SHA-256 distinto en $ruta`n  esperado $esperado`n  real     $real" }
}

function Subir-Codigo([string]$ip) {
    Test-Sha $Script $ShaScript
    Test-Sha $Prompt $ShaPrompt
    Invoke-Remoto "mkdir -p ~/q15/datos"
    Copiar @($Script, $Prompt) "${User}@${ip}:~/q15/"
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

    "probar" {
        az vm start -g $RG -n $VM -o none
        $ip = Get-Ip
        Subir-Codigo $ip
        Invoke-Remoto "python3 -I ~/q15/cribado_llm.py probar --datos ~/q15/datos"
        Copiar @("${User}@${ip}:~/q15/datos/probar.json") $Datos
        $validas = (Get-Content (Join-Path $Datos "probar.json") -Raw | ConvertFrom-Json).validas
        Write-Host "`nPasan la prueba de formato: $($validas -join ', '). Las demas quedan NO_EVALUADAS."
        Write-Host "Siguiente: -Fase lanzar -Mitad seleccion"
    }

    "lanzar" {
        $entrada = Join-Path $Datos "entrada_$Mitad.jsonl"
        if (-not (Test-Path $entrada)) { throw "No existe $entrada. Corre antes 'preparar' en tu PC." }
        $congelada = (Get-Content $Particion -Raw | ConvertFrom-Json).sha256."entrada_$Mitad.jsonl"
        Test-Sha $entrada $congelada
        if ($Mitad -eq "seleccion") {
            $pj = Join-Path $Datos "probar.json"
            if (-not (Test-Path $pj)) { throw "Falta $pj. Corre antes -Fase probar." }
            $Configs = @((Get-Content $pj -Raw | ConvertFrom-Json).validas)
        } else {
            $ej = Join-Path $Datos "eleccion.json"
            if (-not (Test-Path $ej)) { throw "Falta $ej. Corre antes 'elegir' en tu PC." }
            $el = (Get-Content $ej -Raw | ConvertFrom-Json).elegida
            if (-not $el) { throw "eleccion.json no tiene configuracion elegida: el piloto es NO_APTO y no hay validacion." }
            $Configs = @($el)
        }
        if ($Configs.Count -eq 0) { throw "Ninguna configuracion paso la prueba de formato." }
        az vm start -g $RG -n $VM -o none
        $ip = Get-Ip
        Subir-Codigo $ip
        Copiar @($entrada) "${User}@${ip}:~/q15/datos/"
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
        Copiar @("${User}@${ip}:~/q15/datos/salida_$($Mitad)_*.jsonl") $Datos
        Copiar @("${User}@${ip}:~/q15/etiquetar.log") (Join-Path $Datos "etiquetar_$Mitad.log")
        $info = Join-Path $Datos "nube_info_$Mitad.txt"
        ssh "$User@$ip" "date -u; ollama --version; ollama list; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv; sha256sum ~/q15/cribado_llm.py ~/q15/PROMPT_CRIBADO_LLM.md ~/q15/datos/*.jsonl" | Set-Content $info
        Write-Host "`nSalidas en $Datos. Entorno y hashes en $info."
    }

    "borrar" {
        az group delete -n $RG --yes --no-wait
        Write-Host "Borrando $RG. Confirma en unos minutos con: az group exists -n $RG"
    }
}
