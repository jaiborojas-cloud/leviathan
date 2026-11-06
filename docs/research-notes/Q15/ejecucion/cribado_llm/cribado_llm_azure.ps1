# cribado_llm_azure.ps1 - Q15: piloto de cribado con modelos abiertos en Azure spot (Standard_NC24ads_A100_v4)
# Adaptado de experimentos-aislados/E001 nube/etiquetar_azure.ps1. Enmienda 3.
#
# Fases, en orden:
#   cuota     revisa la cuota spot (24 vCPU "Low-priority") en la region
#   crear     grupo de recursos + VM spot; SSH solo a tu IP; tope de precio y apagado diario de seguridad
#   preparar  instala drivers NVIDIA y reinicia la VM
#   instalar  instala Ollama (misma version que la local), baja los tres modelos e imprime sus IDs
#   probar    sube script y prompt, revisa el formato de cada modelo con una obra inventada y baja probar.json
#   lanzar    sube script, prompt y UNA entrada (sin etiquetas de referencia) y etiqueta en tmux (reanudable)
#             seleccion: las configuraciones que pasaron "probar"; validacion: solo la de eleccion.json
#             el primer 'lanzar' fija el presupuesto: 24 h de reloj; despues ya no se lanza nada
#   estado    progreso, codigo de salida y GPU
#   bajar     trae las salidas de la mitad indicada, verifica sus hashes y registra el entorno
#   borrar    elimina todo el grupo de recursos (deja de cobrar)
#
# Si Azure desaloja la VM o el registro dice "Sin conexion con Ollama": repite -Fase lanzar con los mismos argumentos.

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("cuota", "crear", "preparar", "instalar", "probar", "lanzar", "estado", "bajar", "borrar")]
    [string]$Fase,
    [string]$OllamaVersion = "",
    [string]$Region = "eastus",
    [string]$Datos = "D:\RIPG_DATA\Q15_CRIBADO_LLM",
    [ValidateSet("seleccion", "validacion")]
    [string]$Mitad = "seleccion",
    [double]$PrecioMaxHora = 1.00
)

$ErrorActionPreference = "Stop"
$RG = "rg-q15-cribado"
$VM = "vm-q15-cribado"
$Size = "Standard_NC24ads_A100_v4"
$User = "azureuser"
$Modelos = @("qwen3.8:27b", "gemma4:31b", "gpt-oss:120b")
$HorasPresupuesto = 24
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $Aqui "cribado_llm.py"
$Prompt = Join-Path $Aqui "PROMPT_CRIBADO_LLM.md"
$Particion = Join-Path $Aqui "particion.json"
$Presupuesto = Join-Path $Datos "presupuesto.json"
# hashes congelados (PREREGISTRO_CRIBADO_LLM.md); si tu copia difiere, no se sube nada
$ShaScript = "a2825a37f2aae5897cfcf74d120844d26dff1e5ca8c3bb05dbf34195ab090afa"
$ShaPrompt = "0d102764a522b0d09cbfd60fbc0d1fff375a99c40d254b52dafa9592a9d593f0"

# Todo comando nativo pasa por aqui: un codigo distinto de cero detiene el script (PowerShell no lo hace solo).
function Invoke-Nativo([string]$exe, [string[]]$argumentos) {
    $salida = & $exe @argumentos
    if ($LASTEXITCODE -ne 0) { throw "Fallo ($LASTEXITCODE): $exe $($argumentos -join ' ')" }
    return $salida
}
function Invoke-Az([string[]]$argumentos) { Invoke-Nativo "az" $argumentos }

function Get-Ip {
    $ip = Invoke-Az @("vm", "show", "-d", "-g", $RG, "-n", $VM, "--query", "publicIps", "-o", "tsv")
    $ip = "$ip".Trim()
    if (-not $ip) { throw "La VM no tiene IP publica (esta apagada o no existe)." }
    return $ip
}

function Invoke-Remoto([string]$cmd) { Invoke-Nativo "ssh" @("-o", "StrictHostKeyChecking=accept-new", "$User@$(Get-Ip)", $cmd) }
function Copiar([string[]]$origen, [string]$destino) { Invoke-Nativo "scp" (@($origen) + @($destino)) | Out-Null }

function Test-Sha([string]$ruta, [string]$esperado) {
    $real = (Get-FileHash $ruta -Algorithm SHA256).Hash.ToLower()
    if ($real -ne $esperado) { throw "SHA-256 distinto en $ruta`n  esperado $esperado`n  real     $real" }
}

function Subir-Codigo([string]$ip) {
    Test-Sha $Script $ShaScript
    Test-Sha $Prompt $ShaPrompt
    Invoke-Remoto "mkdir -p ~/q15/datos" | Out-Null
    Copiar @($Script, $Prompt, $Particion) "${User}@${ip}:~/q15/"
}

switch ($Fase) {

    "cuota" {
        Invoke-Az @("vm", "list-usage", "--location", $Region, "-o", "table") | Select-String -Pattern "Low-priority|NCADS_A100"
        Write-Host "`nNecesitas al menos 24 vCPU libres en 'Total Regional Low-priority vCPUs'."
    }

    "crear" {
        $miIp = (Invoke-RestMethod -Uri "https://api.ipify.org").Trim()
        Invoke-Az @("group", "create", "-n", $RG, "-l", $Region, "-o", "none") | Out-Null
        Invoke-Az @("vm", "create", "-g", $RG, "-n", $VM, "--size", $Size,
            "--image", "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest",
            "--priority", "Spot", "--eviction-policy", "Deallocate", "--max-price", "$PrecioMaxHora",
            "--admin-username", $User, "--generate-ssh-keys", "--os-disk-size-gb", "256",
            "--public-ip-sku", "Standard", "--nsg-rule", "NONE", "-o", "table")
        Invoke-Az @("network", "nsg", "rule", "create", "-g", $RG, "--nsg-name", "${VM}NSG", "-n", "ssh-solo-mi-ip",
            "--priority", "1000", "--source-address-prefixes", "$miIp/32", "--destination-port-ranges", "22",
            "--access", "Allow", "--protocol", "Tcp", "-o", "none") | Out-Null
        # apagado DIARIO de seguridad (es una hora del dia, no un tope acumulado; el tope es el presupuesto de 'lanzar')
        $apagado = (Get-Date).ToUniversalTime().AddHours(6).ToString("HHmm")
        Invoke-Az @("vm", "auto-shutdown", "-g", $RG, "-n", $VM, "--time", $apagado, "-o", "none") | Out-Null
        Write-Host "`nVM creada. SSH solo para $miIp. Tope $PrecioMaxHora USD/h; apagado diario de seguridad a las $apagado UTC."
        Write-Host "Siguiente: -Fase preparar"
    }

    "preparar" {
        Invoke-Remoto ("sudo apt-get update -y && " +
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ubuntu-drivers-common tmux python3 && " +
            "sudo ubuntu-drivers install --gpgpu && " +
            "V=`$(dpkg -l | grep -oP 'libnvidia-compute-\K[0-9]+-server' | head -n1) && " +
            "echo Driver: `$V && " +
            "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nvidia-utils-`$V linux-modules-nvidia-`$V-azure")
        Invoke-Az @("vm", "restart", "-g", $RG, "-n", $VM, "-o", "none") | Out-Null
        Invoke-Remoto "nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv"
        Write-Host "`nGPU lista. Siguiente: -Fase instalar -OllamaVersion <version>"
    }

    "instalar" {
        if (-not $OllamaVersion) { throw "Pasa -OllamaVersion, p. ej. -OllamaVersion 0.40.14" }
        # pipefail: si curl falla, el comando falla aunque 'sh' reciba una entrada vacia
        Invoke-Remoto "set -o pipefail; curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=$OllamaVersion sh"
        foreach ($m in $Modelos) { Invoke-Remoto "ollama pull $m" }
        Invoke-Remoto "ollama --version; ollama list"
        foreach ($m in $Modelos) { Invoke-Remoto "ollama show $m" }
        Write-Host "`nRegistra la version, los IDs y la cuantizacion de arriba en el registro de ejecucion ANTES de lanzar."
    }

    "probar" {
        Invoke-Az @("vm", "start", "-g", $RG, "-n", $VM, "-o", "none") | Out-Null
        $ip = Get-Ip
        Subir-Codigo $ip
        Invoke-Remoto "python3 -I ~/q15/cribado_llm.py probar --datos ~/q15/datos"
        New-Item -ItemType Directory -Force -Path $Datos | Out-Null
        Copiar @("${User}@${ip}:~/q15/datos/probar.json") $Datos
        $validas = @((Get-Content (Join-Path $Datos "probar.json") -Raw | ConvertFrom-Json).validas)
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
            $el = Get-Content $ej -Raw | ConvertFrom-Json
            if ($el.veredicto -ne "ELEGIDA" -or $el.prueba) { throw "eleccion.json no tiene configuracion elegida (veredicto $($el.veredicto)); no hay validacion." }
            $Configs = @($el.elegida)
        }
        if ($Configs.Count -eq 0) { throw "Ninguna configuracion paso la prueba de formato: el piloto es NO_APTO." }

        # presupuesto: 24 h de reloj desde el primer 'lanzar'; se fija una vez y no se reinicia
        $ahora = (Get-Date).ToUniversalTime()
        if (-not (Test-Path $Presupuesto)) {
            [ordered]@{ inicio_utc = $ahora.ToString("yyyy-MM-ddTHH:mm:ssZ"); limite_utc = $ahora.AddHours($HorasPresupuesto).ToString("yyyy-MM-ddTHH:mm:ssZ"); horas = $HorasPresupuesto } |
                ConvertTo-Json | Set-Content -Path $Presupuesto -Encoding utf8
        }
        # se lee como texto: ConvertFrom-Json de PowerShell 7 convierte las fechas ISO a DateTime local
        $limiteTexto = [regex]::Match((Get-Content $Presupuesto -Raw), '"limite_utc"\s*:\s*"([^"]+)"').Groups[1].Value
        $limite = [datetime]::ParseExact($limiteTexto, "yyyy-MM-ddTHH:mm:ssZ", [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal)
        $restante = [int][math]::Floor(($limite - $ahora).TotalSeconds)
        if ($restante -le 60) { throw "Se agoto el presupuesto de $HorasPresupuesto h (limite $limiteTexto): el piloto queda INCONCLUSIVO si no termino." }

        Invoke-Az @("vm", "start", "-g", $RG, "-n", $VM, "-o", "none") | Out-Null
        $ip = Get-Ip
        $sesion = Invoke-Remoto "tmux has-session -t q15 2>/dev/null && echo SI || echo NO"
        if ("$sesion".Trim() -eq "SI") { throw "Ya hay una sesion q15 corriendo en la VM; espera a que termine (-Fase estado) antes de lanzar otra." }
        Subir-Codigo $ip
        Copiar @($entrada) "${User}@${ip}:~/q15/datos/"
        # correr.sh: el limite viaja como hora ABSOLUTA; el tiempo restante se calcula en la VM al arrancar,
        # 'timeout' corta en el limite y 'etiquetar --hasta' no empieza obras despues de el
        $epoch = [DateTimeOffset]::new($limite).ToUnixTimeSeconds()
        $cadena = ($Configs | ForEach-Object {
            "python3 -I ~/q15/cribado_llm.py etiquetar --entrada ~/q15/datos/entrada_$Mitad.jsonl --config $_ --datos ~/q15/datos --hasta $limiteTexto"
        }) -join " && "
        $lineas = @(
            '#!/bin/bash',
            "# generado por cribado_llm_azure.ps1 (lanzar $Mitad); limite $limiteTexto",
            'set -o pipefail',
            "LIMITE=$epoch",
            'LOG=~/q15/etiquetar.log',
            'restante=$(( LIMITE - $(date +%s) ))',
            ('if [ "$restante" -le 60 ]; then echo "FIN ' + $Mitad + ' codigo=SIN_TIEMPO" >> "$LOG"; exit 0; fi'),
            ("timeout `"`$restante`" bash -c '" + $cadena + "' 2>&1 | tee -a `"`$LOG`""),
            ('echo "FIN ' + $Mitad + ' codigo=$?" >> "$LOG"')
        )
        $correr = Join-Path ([IO.Path]::GetTempPath()) "q15_correr_$Mitad.sh"
        [IO.File]::WriteAllText($correr, (($lineas -join "`n") + "`n"))   # LF, sin BOM
        Copiar @($correr) "${User}@${ip}:~/q15/correr.sh"
        Invoke-Remoto "tmux new -d -s q15 'bash ~/q15/correr.sh'" | Out-Null
        Write-Host "`nEtiquetado de '$Mitad' con $($Configs -join ', ') corriendo, como maximo hasta $limiteTexto. Revisa con: -Fase estado"
    }

    "estado" {
        Invoke-Remoto ("tail -n 4 ~/q15/etiquetar.log; tmux has-session -t q15 2>/dev/null && echo SESION: corriendo || echo SESION: terminada; " +
            "for f in ~/q15/datos/salida_*.jsonl; do [ -f `"`$f`" ] && echo `"`$(basename `$f): `$(wc -l < `$f)`"; done; " +
            "nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used --format=csv,noheader")
    }

    "bajar" {
        $ip = Get-Ip
        New-Item -ItemType Directory -Force -Path $Datos | Out-Null
        Copiar @("${User}@${ip}:~/q15/datos/salida_$($Mitad)_*.jsonl") $Datos
        Copiar @("${User}@${ip}:~/q15/etiquetar.log") (Join-Path $Datos "etiquetar_$Mitad.log")
        # verifica que lo bajado sea identico a lo que hay en la VM
        $remotos = @(Invoke-Remoto "cd ~/q15/datos && sha256sum salida_$($Mitad)_*.jsonl")
        if ($remotos.Count -eq 0) { throw "La VM no devolvio hashes de las salidas." }
        foreach ($linea in $remotos) {
            $h, $n = ("$linea".Trim() -split "\s+", 2)
            Test-Sha (Join-Path $Datos $n.Trim()) $h
        }
        $info = Join-Path $Datos "nube_info_$Mitad.txt"
        Invoke-Remoto "date -u; ollama --version; ollama list; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv; sha256sum ~/q15/cribado_llm.py ~/q15/PROMPT_CRIBADO_LLM.md ~/q15/particion.json ~/q15/datos/*.jsonl; echo '--- correr.sh'; cat ~/q15/correr.sh" |
            Set-Content $info
        Write-Host "`nSalidas en $Datos, con hashes verificados contra la VM ($($remotos.Count) archivos). Entorno en $info."
    }

    "borrar" {
        Invoke-Az @("group", "delete", "-n", $RG, "--yes", "--no-wait") | Out-Null
        Write-Host "Borrando $RG. Confirma en unos minutos con: az group exists -n $RG"
    }
}
