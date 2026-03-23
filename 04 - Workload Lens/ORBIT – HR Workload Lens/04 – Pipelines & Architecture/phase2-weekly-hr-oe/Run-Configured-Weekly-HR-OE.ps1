param(
    [string]$PullDate = (Get-Date -Format 'yyyy-MM-dd'),
    [string]$BIWeeklyDir = 'C:\Users\kwallace12\OneDrive - Chewy.com, LLC\Workload Lens Incoming ticket bi drop',
    [string]$OutDir,
    [string]$Label,
    [switch]$AllowPartialPhase1
)

$ErrorActionPreference = 'Stop'

function Get-LatestCompletedSaturday {
    param([datetime]$Date)

    $offset = (([int]$Date.DayOfWeek - [int][System.DayOfWeek]::Saturday) + 7) % 7
    return $Date.Date.AddDays(-$offset)
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..')).Path
$phase2OutDir = if ($OutDir) { $OutDir } else { Join-Path $repoRoot '04 - Workload Lens\Phase II\output' }
$ticketPrepOutDir = Join-Path $phase2OutDir 'ticket_prep'
$ticketLauncherPath = Join-Path $PSScriptRoot 'Run-Configured-Ticket-Folder-Drop.ps1'
$fullLauncherPath = Join-Path $PSScriptRoot 'Run-Configured-HR-OE-BI.ps1'

if (-not $Label) {
    $Label = "ticket_bi_run_$PullDate"
}

New-Item -ItemType Directory -Force -Path $phase2OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $ticketPrepOutDir | Out-Null

$pullDateValue = [datetime]::ParseExact($PullDate, 'yyyy-MM-dd', [System.Globalization.CultureInfo]::InvariantCulture)
$week9End = Get-LatestCompletedSaturday -Date $pullDateValue
$week9Start = $week9End.AddDays(-6)
$ticketPrepLabel = "ticket_bi_drop_{0}_to_{1}" -f $week9Start.ToString('yyyy-MM-dd'), $week9End.ToString('yyyy-MM-dd')
$summaryPath = Join-Path $phase2OutDir ("weekly_hr_oe_orchestration_{0}.json" -f $PullDate)

$summary = [ordered]@{
    pass = $false
    pull_date = $PullDate
    bi_weekly_dir = $BIWeeklyDir
    allow_partial_phase1 = [bool]$AllowPartialPhase1
    ticket_prep = [ordered]@{
        label = $ticketPrepLabel
        out_dir = $ticketPrepOutDir
        state_file = (Join-Path $ticketPrepOutDir 'ticket_folder_drop_state.json')
        chat_handoff = (Join-Path (Join-Path $ticketPrepOutDir $ticketPrepLabel) 'ticket_prep_chat_handoff.md')
        exit_code = $null
    }
    full_pipeline = [ordered]@{
        label = $Label
        out_dir = $phase2OutDir
        run_summary = (Join-Path $phase2OutDir ("hr_oe_pipeline_run_{0}.json" -f $Label))
        answer_pack = (Join-Path $phase2OutDir ("hr_oe_answer_pack_{0}.md" -f $Label))
        metrics = (Join-Path $phase2OutDir ("hr_oe_metrics_{0}.json" -f $Label))
        chat_handoff = (Join-Path $phase2OutDir ("hr_oe_chat_handoff_{0}.md" -f $Label))
        exit_code = $null
    }
    summary_path = $summaryPath
    generated_at_utc = $null
}

Write-Host "Running weekly HR/OE workflow for pull date: $PullDate"
Write-Host "Step 1 of 2: Ticket prep from BI folder and Outlook sources"

& powershell -ExecutionPolicy Bypass -File $ticketLauncherPath `
    -PullDate $PullDate `
    -BIWeeklyDir $BIWeeklyDir `
    -OutDir $ticketPrepOutDir
$ticketExitCode = $LASTEXITCODE
$summary.ticket_prep.exit_code = $ticketExitCode

if ($ticketExitCode -ne 0) {
    $summary.failed_step = 'ticket_prep'
    $summary.generated_at_utc = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
    $summary | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 $summaryPath
    Write-Host "Ticket prep failed. Summary written to: $summaryPath"
    exit $ticketExitCode
}

Write-Host "Step 2 of 2: Full HR Operational Excellence pipeline"

$fullArgs = @(
    '-ExecutionPolicy', 'Bypass',
    '-File', $fullLauncherPath,
    '-PullDate', $PullDate,
    '-BIWeeklyDir', $BIWeeklyDir,
    '-OutDir', $phase2OutDir,
    '-Label', $Label,
    '-SkipMsgExtraction'
)

if ($AllowPartialPhase1) {
    $fullArgs += '-AllowPartialPhase1'
}

& powershell @fullArgs
$fullExitCode = $LASTEXITCODE
$summary.full_pipeline.exit_code = $fullExitCode
$summary.pass = ($fullExitCode -eq 0)

if (-not $summary.pass) {
    $summary.failed_step = 'full_pipeline'
}

$summary.generated_at_utc = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
$summary | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 $summaryPath

if ($summary.pass) {
    Write-Host "Weekly HR/OE workflow passed."
    Write-Host "Ticket prep handoff: $($summary.ticket_prep.chat_handoff)"
    Write-Host "Answer pack: $($summary.full_pipeline.answer_pack)"
    Write-Host "Summary: $summaryPath"
}
else {
    Write-Host "Full pipeline failed. Summary written to: $summaryPath"
}

exit $fullExitCode
