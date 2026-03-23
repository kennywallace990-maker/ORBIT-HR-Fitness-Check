param(
    [string]$PullDate = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$BIWeeklyDir = 'C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Workload Lens Incoming ticket bi drop',
    [string]$OutDir,
    [string]$Label,
    [switch]$AllowPartialPhase1,
    [switch]$SkipMsgExtraction
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$phase1Dir = Join-Path $repoRoot '04 - Workload Lens\Phase I\Phase I CSV'
$defaultOutDir = Join-Path $repoRoot '04 - Workload Lens\Phase II\output'
$extractorPath = Join-Path $PSScriptRoot 'Extract-Outlook-Msg-Attachments.ps1'
$inboxExtractorPath = Join-Path $PSScriptRoot 'Extract-Outlook-Inbox-BI-Attachments.ps1'
$runnerPath = Join-Path $PSScriptRoot 'run_hr_oe_pipeline.py'

if (-not $OutDir) {
    $OutDir = $defaultOutDir
}

if (-not $Label) {
    $Label = "ticket_bi_run_$PullDate"
}

$arguments = @(
    $runnerPath,
    '--phase1-dir', $phase1Dir,
    '--phase2-bi-dir', $BIWeeklyDir,
    '--pull-date', $PullDate,
    '--out-dir', $OutDir,
    '--label', $Label
)

if ($AllowPartialPhase1) {
    $arguments += '--allow-partial-phase1'
}

Write-Host "Running full HR OE BI pipeline from: $BIWeeklyDir"
Write-Host "Using Phase I data from: $phase1Dir"
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
