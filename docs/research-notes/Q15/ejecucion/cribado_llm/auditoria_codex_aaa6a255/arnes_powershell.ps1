$ErrorActionPreference = 'Stop'
$auditRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$auditTemp = Join-Path ([IO.Path]::GetTempPath()) ('q15_ps_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $auditTemp | Out-Null
foreach ($n in @('cribado_llm.py','cribado_llm_azure.ps1','PROMPT_CRIBADO_LLM.md')) {
    Copy-Item -LiteralPath (Join-Path $auditRoot $n) -Destination (Join-Path $auditTemp $n)
}
$auditDatos = Join-Path $auditTemp 'datos'
New-Item -ItemType Directory -Path $auditDatos | Out-Null
[IO.File]::WriteAllText((Join-Path $auditDatos 'entrada_seleccion.jsonl'), '{"obra_id":"S","titulo":"Synthetic","resumenes":["Invented"]}' + "`n")
$auditHash = (Get-FileHash (Join-Path $auditDatos 'entrada_seleccion.jsonl')).Hash.ToLower()
@{sha256=@{'entrada_seleccion.jsonl'=$auditHash}} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $auditTemp 'particion.json')
@{validas=@('C1','C2')} | ConvertTo-Json | Set-Content (Join-Path $auditDatos 'probar.json')
$global:q15AuditCalls = [Collections.Generic.List[string]]::new()
$global:q15AuditFailAz = $false
$global:q15AuditSession = $false
$global:q15AuditRemoteCmd = ''
function global:az {
    $global:q15AuditCalls.Add('az '+($args -join ' '))
    $global:LASTEXITCODE = $(if ($global:q15AuditFailAz) {9} else {0})
    if (($args -join ' ') -match 'vm show') { '192.0.2.1' }
}
function global:ssh {
    $auditCmd = [string]$args[-1]
    $global:q15AuditCalls.Add('ssh '+$auditCmd)
    $global:LASTEXITCODE=0
    if ($auditCmd -match '^tmux has-session') { if ($global:q15AuditSession) {'SI'} else {'NO'} }
    elseif ($auditCmd -match '^tmux new') { $global:q15AuditRemoteCmd=$auditCmd }
    elseif ($auditCmd -match '^cd .*sha256sum') { ('0'*64)+'  salida_seleccion_C1.jsonl' }
}
function global:scp {
    $global:q15AuditCalls.Add('scp '+($args -join ' '))
    $global:LASTEXITCODE=0
    if (($args -join ' ') -match ':~/q15/correr.sh') {
        $global:q15AuditCorrer = [IO.File]::ReadAllText([string]$args[0])
    }
    if (($args -join ' ') -match 'salida_seleccion_\*') {
        [IO.File]::WriteAllText((Join-Path $args[-1] 'salida_seleccion_C1.jsonl'), 'synthetic download')
    }
}
$auditResults=[ordered]@{}
$auditScript=Join-Path $auditTemp 'cribado_llm_azure.ps1'
$global:q15AuditFailAz=$true
try { & $auditScript -Fase cuota -Datos $auditDatos; $auditResults.native_failure='MISSED' } catch { $auditResults.native_failure=$_.Exception.Message }
$global:q15AuditFailAz=$false
& $auditScript -Fase lanzar -Datos $auditDatos
$auditResults.remote_command=$global:q15AuditRemoteCmd
$auditResults.correr=$global:q15AuditCorrer
[IO.File]::WriteAllText((Join-Path $auditRoot 'correr_generado.sh'),$global:q15AuditCorrer)
$auditResults.uploads=@($global:q15AuditCalls | Where-Object {$_ -like 'scp *'})
$global:q15AuditSession=$true
try { & $auditScript -Fase lanzar -Datos $auditDatos; $auditResults.active_session='MISSED' } catch { $auditResults.active_session=$_.Exception.Message }
$global:q15AuditSession=$false
@{inicio_utc='2000-01-01T00:00:00Z';limite_utc='2000-01-02T00:00:00Z';horas=24} | ConvertTo-Json | Set-Content (Join-Path $auditDatos 'presupuesto.json')
try { & $auditScript -Fase lanzar -Datos $auditDatos; $auditResults.expired='MISSED' } catch { $auditResults.expired=$_.Exception.Message }
try { & $auditScript -Fase bajar -Datos $auditDatos; $auditResults.bad_hash='MISSED' } catch { $auditResults.bad_hash=$_.Exception.Message }
$auditResults | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $auditRoot 'resultados_powershell.json')
$auditResults | ConvertTo-Json -Depth 8
