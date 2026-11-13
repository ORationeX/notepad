$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
$stamp = Join-Path $env:LOCALAPPDATA "roadmap-year-port.txt"
$low = 8765
$high = 8864
$here = [System.IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\').ToLowerInvariant()

function Test-Roadmap([int]$port) {
  try {
    $h = Invoke-WebRequest -Uri "http://127.0.0.1:$port/api/health" -UseBasicParsing -TimeoutSec 1
    $info = $h.Content | ConvertFrom-Json
    if ($info -and $info.ok -and $info.root) {
      $srvRoot = [System.IO.Path]::GetFullPath([string]$info.root).TrimEnd('\').ToLowerInvariant()
      return $srvRoot -eq $here
    }
  } catch {}
  return $false
}

function Get-Listening {
  $found = @{}
  netstat -ano | Select-String "LISTENING" | ForEach-Object {
    if ($_.Line -match "^\s*TCP\s+\S+:(\d+)\s") {
      $p = [int]$Matches[1]
      if ($p -ge $low -and $p -le $high) { $found[$p] = $true }
    }
  }
  return $found
}

function Emit([int]$port, [string]$mode) {
  Set-Content -Path $stamp -Value $port -Encoding ascii
  Write-Output "$port $mode"
  exit 0
}

$preferred = 0
if (Test-Path $stamp) {
  $raw = (Get-Content $stamp -Raw).Trim()
  if ($raw -match "^\d+$") { $preferred = [int]$raw }
}

if ($preferred -ge $low -and $preferred -le $high -and (Test-Roadmap $preferred)) {
  Emit $preferred "open"
}

$busy = Get-Listening
foreach ($p in ($busy.Keys | Sort-Object)) {
  if ($p -eq $preferred) { continue }
  if (Test-Roadmap $p) { Emit $p "open" }
}

if ($preferred -ge $low -and $preferred -le $high -and -not $busy.ContainsKey($preferred)) {
  Emit $preferred "start"
}

for ($p = $low; $p -le $high; $p++) {
  if (-not $busy.ContainsKey($p)) { Emit $p "start" }
}

Write-Error "no free port between $low and $high"
exit 1
