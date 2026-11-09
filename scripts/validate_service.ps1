param(
  [Parameter(Mandatory=$true)][string]$BaseUrl,
  [Parameter(Mandatory=$true)][string]$Phase,
  [Parameter(Mandatory=$true)][string]$LogPath,
  [int]$Requests = 3
)

$ErrorActionPreference = 'Continue'
$records = @(
  @{ day = '2026-11-01'; sleep = 7.5; exercise = 1.0; stress = 3; water = 2.0 },
  @{ day = '2026-11-02'; sleep = 6.5; exercise = 0.4; stress = 7; water = 1.2 },
  @{ day = '2026-11-03'; sleep = 8.0; exercise = 1.5; stress = 2; water = 2.5 }
)
$encoding = New-Object System.Text.UTF8Encoding($false)
if (-not (Test-Path $LogPath)) { [System.IO.File]::WriteAllText($LogPath, '', $encoding) }

function Write-Event($event) {
  $line = $event | ConvertTo-Json -Compress
  [System.IO.File]::AppendAllText($LogPath, $line + [Environment]::NewLine, $encoding)
  Write-Host $line
}

function Request-Event($kind, $uri, $method, $body) {
  $start = [DateTimeOffset]::UtcNow
  $status = 'error'; $score = $null; $insight = $false; $version = 'unknown'; $errorText = $null
  try {
    $params = @{ Uri=$uri; Method=$method; TimeoutSec=8; UseBasicParsing=$true }
    if ($body) { $params.Body = ($body | ConvertTo-Json -Compress); $params.ContentType = 'application/json' }
    $response = Invoke-WebRequest @params
    $status = [int]$response.StatusCode
    $json = $response.Content | ConvertFrom-Json
    if ($json.score -ne $null) { $score = $json.score }
    if ($json.insight -ne $null) { $insight = $true }
    if ($json.app_version -ne $null) { $version = $json.app_version }
    if ($json.model_id -ne $null) { $version = $json.model_id }
  } catch { $errorText = $_.Exception.Message }
  $end = [DateTimeOffset]::UtcNow
  $event = [ordered]@{ phase=$Phase; kind=$kind; start_utc=$start.ToString('o'); end_utc=$end.ToString('o'); response_ms=($end-$start).TotalMilliseconds; status=$status; score=$score; insight_success=$insight; deployment_version=$version; error=$errorText }
  Write-Event $event
}

for ($i = 0; $i -lt [Math]::Min($Requests, $records.Count); $i++) {
  $r = $records[$i]
  Request-Event 'record' "$BaseUrl/api/records/$($r.day)" 'Put' $r
  Start-Sleep -Seconds 1
}
Request-Event 'insight' "$BaseUrl/api/insight/2026-11-03" 'Get' $null
