param(
    [string]$PullDate = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$BIWeeklyDir = 'C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Workload Lens Incoming ticket bi drop',
    [string]$OutDir,
    [string]$Label,
    [switch]$SkipMsgExtraction
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$defaultOutDir = Join-Path $repoRoot '04 - Workload Lens\Phase II\output\ticket_prep'
$extractorPath = Join-Path $PSScriptRoot 'Extract-Outlook-Msg-Attachments.ps1'
$inboxExtractorPath = Join-Path $PSScriptRoot 'Extract-Outlook-Inbox-BI-Attachments.ps1'
$runnerPath = Join-Path $PSScriptRoot 'run_ticket_folder_drop.py'

if (-not $OutDir) {
    $OutDir = $defaultOutDir
}

$arguments = @(
    $runnerPath,
    '--bi-weekly-dir', $BIWeeklyDir,
    '--pull-date', $PullDate,
    '--out-dir', $OutDir
)

if ($Label) {
    $arguments += @('--label', $Label)
}

Write-Host "Running ticket folder-drop prep from: $BIWeeklyDir"
Write-Host "Writing outputs to: $OutDir"

if (-not $SkipMsgExtraction) {
    Write-Host "Extracting CSV/XLSX attachments from any .msg files in: $BIWeeklyDir"
    & $extractorPath -MailDropDir $BIWeeklyDir -AttachmentDir $BIWeeklyDir -MoveProcessed
    if (-not $?) {
        exit 1
    }

    Write-Host "Extracting CSV/XLSX attachments from the default Outlook Inbox into: $BIWeeklyDir"
    & $inboxExtractorPath -AttachmentDir $BIWeeklyDir
    if (-not $?) {
        exit 1
    }
}

& python @arguments
exit $LASTEXITCODE
