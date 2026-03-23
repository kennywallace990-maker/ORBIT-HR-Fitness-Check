param(
    [Parameter(Mandatory = $true)]
    [string]$MailDropDir,
    [string]$AttachmentDir,
    [string]$ProcessedDir,
    [switch]$MoveProcessed,
    [switch]$UseMailboxFallback,
    [string]$MailboxName,
    [string]$MailboxFolderPath = 'Inbox',
    [string]$SenderContains = 'ServiceDesk@chewy.com',
    [string[]]$SubjectContains = @(
        'WBR Previous Week Open Cases',
        'WBR Previous Week Resolved Cases'
    ),
    [int]$LookbackDays = 21,
    [string]$ProcessedMailboxStatePath
)

$ErrorActionPreference = 'Stop'

function Release-ComObject {
    param(
        $ComObject
    )

    if ($null -ne $ComObject) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ComObject)
    }
}

function Get-UniquePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Directory,
        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    $candidate = Join-Path $Directory $FileName
    if (-not (Test-Path -LiteralPath $candidate)) {
        return $candidate
    }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
    $extension = [System.IO.Path]::GetExtension($FileName)
    $counter = 1
    while ($true) {
        $nextName = '{0}_{1}{2}' -f $baseName, $counter, $extension
        $candidate = Join-Path $Directory $nextName
        if (-not (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
        $counter++
    }
}

function ConvertTo-SafeFileName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $invalidChars = [System.IO.Path]::GetInvalidFileNameChars()
    $safe = $Value
    foreach ($char in $invalidChars) {
        $safe = $safe.Replace($char, '_')
    }
    return $safe.Trim()
}

function Get-ReportTag {
    param(
        [string]$Value
    )

    if (-not $Value) {
        return $null
    }

    $normalized = ($Value.ToLowerInvariant() -replace '[^a-z0-9]+', ' ').Trim()
    if (-not $normalized) {
        return $null
    }

    $resolvedTokens = @(
        'wbr previous week resolved cases',
        'resolved cases',
        'cases closed',
        'closed last week',
        'closed',
        'resolved',
        'resolve'
    )
    $openTokens = @(
        'wbr previous week open cases',
        'open cases',
        'cases opened',
        'opened last week',
        'opened',
        'open last week',
        'open'
    )

    foreach ($token in $resolvedTokens) {
        if ($normalized.Contains($token)) {
            return 'resolved_cases'
        }
    }
    foreach ($token in $openTokens) {
        if ($normalized.Contains($token)) {
            return 'open_cases'
        }
    }
    return $null
}

function Get-PreferredAttachmentName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$AttachmentName,
        [string]$MailSubject
    )

    $safeName = ConvertTo-SafeFileName -Value $AttachmentName
    $reportTag = Get-ReportTag -Value $MailSubject
    if (-not $reportTag) {
        $reportTag = Get-ReportTag -Value $safeName
    }
    if (-not $reportTag) {
        return $safeName
    }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($safeName)
    $extension = [System.IO.Path]::GetExtension($safeName)
    if ($baseName.ToLowerInvariant().StartsWith($reportTag + '_')) {
        return $safeName
    }
    return '{0}_{1}{2}' -f $reportTag, $baseName, $extension
}

function Initialize-OutlookSession {
    try {
        $outlook = New-Object -ComObject Outlook.Application
        $namespace = $outlook.GetNamespace('MAPI')
    } catch {
        throw "Could not initialize Outlook COM automation. Outlook desktop must be installed and available."
    }

    return @{
        outlook = $outlook
        namespace = $namespace
    }
}

function Get-OutlookMailboxRoot {
    param(
        [Parameter(Mandatory = $true)]
        $Namespace,
        [string]$MailboxName
    )

    if ($MailboxName) {
        $matchedRoot = @($Namespace.Folders) | Where-Object { $_.Name -eq $MailboxName } | Select-Object -First 1
        if (-not $matchedRoot) {
            throw "Could not find Outlook mailbox root '$MailboxName'."
        }
        return $matchedRoot
    }

    $defaultInbox = $Namespace.GetDefaultFolder(6)
    try {
        return $defaultInbox.Parent
    } finally {
        Release-ComObject -ComObject $defaultInbox
    }
}

function Resolve-OutlookFolder {
    param(
        [Parameter(Mandatory = $true)]
        $RootFolder,
        [Parameter(Mandatory = $true)]
        [string]$FolderPath
    )

    $segments = @($FolderPath -split '[\\/]' | Where-Object { $_ -and $_.Trim() })
    if (-not $segments -or $segments.Count -eq 0) {
        return $RootFolder
    }

    if ($segments[0] -eq $RootFolder.Name) {
        if ($segments.Count -eq 1) {
            return $RootFolder
        }
        $segments = $segments[1..($segments.Count - 1)]
    }

    $current = $RootFolder
    foreach ($segment in $segments) {
        $next = @($current.Folders) | Where-Object { $_.Name -eq $segment } | Select-Object -First 1
        if (-not $next) {
            throw "Could not find Outlook folder segment '$segment' under '$($current.FolderPath)'."
        }
        $current = $next
    }

    return $current
}

function Read-ProcessedMailboxState {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $entryIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $entryIds
    }

    try {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding utf8
        if (-not $raw) {
            return $entryIds
        }
        $state = $raw | ConvertFrom-Json
        foreach ($entryId in @($state.processed_entry_ids)) {
            if ($entryId) {
                [void]$entryIds.Add([string]$entryId)
            }
        }
    } catch {
        return $entryIds
    }

    return $entryIds
}

function Write-ProcessedMailboxState {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [System.Collections.Generic.HashSet[string]]$EntryIds,
        [string]$MailboxName,
        [string]$MailboxFolderPath,
        [int]$LookbackDays
    )

    $serializedEntryIds = @()
    if ($EntryIds) {
        foreach ($entryId in $EntryIds.GetEnumerator()) {
            if ($entryId) {
                $serializedEntryIds += [string]$entryId
            }
        }
    }

    $payload = @{
        mailbox_name = $MailboxName
        mailbox_folder_path = $MailboxFolderPath
        lookback_days = $LookbackDays
        updated_at_utc = [DateTime]::UtcNow.ToString('o')
        processed_entry_ids = $serializedEntryIds
    }
    $payload | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Process-MailItemAttachments {
    param(
        [Parameter(Mandatory = $true)]
        $MailItem,
        [Parameter(Mandatory = $true)]
        [string]$TargetDirectory,
        [Parameter(Mandatory = $true)]
        [string[]]$AllowedExtensions,
        [System.Collections.Generic.List[string]]$ExtractedFiles
    )

    if ($null -eq $MailItem.Attachments -or $MailItem.Attachments.Count -eq 0) {
        return 0
    }

    $savedCount = 0
    for ($index = 1; $index -le $MailItem.Attachments.Count; $index++) {
        $attachment = $null
        try {
            $attachment = $MailItem.Attachments.Item($index)
            $originalName = Get-PreferredAttachmentName -AttachmentName $attachment.FileName -MailSubject $MailItem.Subject
            $extension = [System.IO.Path]::GetExtension($originalName).ToLowerInvariant()
            if ($AllowedExtensions -notcontains $extension) {
                continue
            }
            $targetPath = Get-UniquePath -Directory $TargetDirectory -FileName $originalName
            $attachment.SaveAsFile($targetPath)
            $ExtractedFiles.Add($targetPath)
            $savedCount++
        } finally {
            Release-ComObject -ComObject $attachment
        }
    }

    return $savedCount
}

function Process-OutlookMailboxFallback {
    param(
        [Parameter(Mandatory = $true)]
        $Namespace,
        [string]$MailboxName,
        [Parameter(Mandatory = $true)]
        [string]$MailboxFolderPath,
        [string]$SenderContains,
        [Parameter(Mandatory = $true)]
        [string[]]$SubjectContains,
        [Parameter(Mandatory = $true)]
        [datetime]$ReceivedAfter,
        [Parameter(Mandatory = $true)]
        [string]$TargetDirectory,
        [Parameter(Mandatory = $true)]
        [string[]]$AllowedExtensions,
        [System.Collections.Generic.List[string]]$ExtractedFiles,
        [System.Collections.Generic.HashSet[string]]$ProcessedEntryIds,
        [Parameter(Mandatory = $true)]
        [hashtable]$Summary
    )

    $rootFolder = $null
    $sourceFolder = $null
    $foldersToScan = [System.Collections.Generic.Stack[object]]::new()

    try {
        if ((-not $MailboxName) -and ($MailboxFolderPath -eq 'Inbox')) {
            $sourceFolder = $Namespace.GetDefaultFolder(6)
            $rootFolder = $sourceFolder.Parent
        } else {
            $rootFolder = Get-OutlookMailboxRoot -Namespace $Namespace -MailboxName $MailboxName
            $sourceFolder = Resolve-OutlookFolder -RootFolder $rootFolder -FolderPath $MailboxFolderPath
        }

        $foldersToScan.Push($sourceFolder)
        while ($foldersToScan.Count -gt 0) {
            $folder = $foldersToScan.Pop()
            foreach ($subFolder in @($folder.Folders)) {
                $foldersToScan.Push($subFolder)
            }

            $items = $null
            try {
                $items = $folder.Items
                $items.Sort('[ReceivedTime]', $true)
                foreach ($item in @($items)) {
                    try {
                        if ($item.Class -ne 43) {
                            continue
                        }

                        $receivedTime = $null
                        try {
                            $receivedTime = [datetime]$item.ReceivedTime
                        } catch {
                            $receivedTime = $null
                        }
                        if ($receivedTime -and $receivedTime -lt $ReceivedAfter) {
                            break
                        }

                        $subject = [string]$item.Subject
                        if (-not $subject) {
                            continue
                        }

                        $subjectMatched = $false
                        foreach ($subjectToken in $SubjectContains) {
                            if ($subject -like "*$subjectToken*") {
                                $subjectMatched = $true
                                break
                            }
                        }
                        if (-not $subjectMatched) {
                            continue
                        }

                        $sender = [string]$item.SenderEmailAddress
                        if ($SenderContains -and (($sender -as [string]) -notlike "*$SenderContains*")) {
                            continue
                        }

                        $entryId = $null
                        try {
                            $entryId = [string]$item.EntryID
                        } catch {
                            $entryId = $null
                        }
                        if ($entryId -and $ProcessedEntryIds.Contains($entryId)) {
                            continue
                        }

                        $Summary.matched_outlook_messages++
                        [void](Process-MailItemAttachments -MailItem $item -TargetDirectory $TargetDirectory -AllowedExtensions $AllowedExtensions -ExtractedFiles $ExtractedFiles)
                        if ($entryId) {
                            [void]$ProcessedEntryIds.Add($entryId)
                        }
                        $Summary.processed_outlook_messages++
                    } catch {
                        continue
                    }
                }
            } finally {
                Release-ComObject -ComObject $items
                if ($folder -and $folder -ne $sourceFolder) {
                    Release-ComObject -ComObject $folder
                }
            }
        }
    } finally {
        if ($sourceFolder) {
            Release-ComObject -ComObject $sourceFolder
        }
        if ($rootFolder) {
            Release-ComObject -ComObject $rootFolder
        }
    }
}

$mailDropDirResolved = (Resolve-Path -LiteralPath $MailDropDir).Path
if (-not $AttachmentDir) {
    $AttachmentDir = $mailDropDirResolved
}
if (-not (Test-Path -LiteralPath $AttachmentDir)) {
    New-Item -ItemType Directory -Path $AttachmentDir | Out-Null
}
if ($MoveProcessed -and -not $ProcessedDir) {
    $ProcessedDir = Join-Path $mailDropDirResolved '_processed_msg'
}
if ($MoveProcessed -and -not (Test-Path -LiteralPath $ProcessedDir)) {
    New-Item -ItemType Directory -Path $ProcessedDir | Out-Null
}

$processedMailboxStatePathResolved = $null
if ($UseMailboxFallback) {
    if (-not $ProcessedMailboxStatePath) {
        $ProcessedMailboxStatePath = Join-Path $mailDropDirResolved '_processed_outlook_ids.json'
    }
    $processedMailboxStatePathResolved = $ProcessedMailboxStatePath
}

$msgFiles = Get-ChildItem -LiteralPath $mailDropDirResolved -Filter *.msg -File | Sort-Object LastWriteTime, Name
$allowedExtensions = @('.csv', '.xlsx', '.xlsm')
$extractedFiles = [System.Collections.Generic.List[string]]::new()
$processedEmails = @()
$summary = @{
    msg_file_count = @($msgFiles).Count
    matched_outlook_messages = 0
    processed_outlook_messages = 0
    mailbox_fallback_used = $false
}
$outlook = $null
$namespace = $null

if ($msgFiles -or $UseMailboxFallback) {
    $session = Initialize-OutlookSession
    $outlook = $session.outlook
    $namespace = $session.namespace
}

foreach ($msgFile in $msgFiles) {
    $mailItem = $null
    $moveTargetPath = $null
    try {
        $mailItem = $namespace.OpenSharedItem($msgFile.FullName)
        if ($null -eq $mailItem.Attachments -or $mailItem.Attachments.Count -eq 0) {
            if ($MoveProcessed) {
                $moveTargetPath = Get-UniquePath -Directory $ProcessedDir -FileName $msgFile.Name
            }
        } else {
            [void](Process-MailItemAttachments -MailItem $mailItem -TargetDirectory $AttachmentDir -AllowedExtensions $allowedExtensions -ExtractedFiles $extractedFiles)

            if ($MoveProcessed) {
                $moveTargetPath = Get-UniquePath -Directory $ProcessedDir -FileName $msgFile.Name
            }
        }
    } finally {
        Release-ComObject -ComObject $mailItem
    }

    if ($moveTargetPath) {
        [gc]::Collect()
        [gc]::WaitForPendingFinalizers()
        Move-Item -LiteralPath $msgFile.FullName -Destination $moveTargetPath
        $processedEmails += $moveTargetPath
    }
}

if (-not $msgFiles -and $UseMailboxFallback) {
    $summary.mailbox_fallback_used = $true
    $processedEntryIds = Read-ProcessedMailboxState -Path $processedMailboxStatePathResolved
    $receivedAfter = (Get-Date).Date.AddDays(-1 * $LookbackDays)
    if ((-not $MailboxName) -and ($MailboxFolderPath -eq 'Inbox')) {
        $sourceFolder = $namespace.GetDefaultFolder(6)
        $items = $null
        try {
            $items = $sourceFolder.Items
            $items.Sort('[ReceivedTime]', $true)
            foreach ($item in @($items)) {
                try {
                    if ($item.Class -ne 43) {
                        continue
                    }

                    $receivedTime = [datetime]$item.ReceivedTime
                    if ($receivedTime -lt $receivedAfter) {
                        break
                    }

                    $subject = [string]$item.Subject
                    $sender = [string]$item.SenderEmailAddress
                    $subjectMatched = $false
                    foreach ($subjectToken in $SubjectContains) {
                        if ($subject -like "*$subjectToken*") {
                            $subjectMatched = $true
                            break
                        }
                    }
                    if (-not $subjectMatched) {
                        continue
                    }
                    if ($SenderContains -and ($sender -notlike "*$SenderContains*")) {
                        continue
                    }

                    $entryId = $null
                    try {
                        $entryId = [string]$item.EntryID
                    } catch {
                        $entryId = $null
                    }
                    if ($entryId -and $processedEntryIds.Contains($entryId)) {
                        continue
                    }

                    $summary.matched_outlook_messages++
                    [void](Process-MailItemAttachments -MailItem $item -TargetDirectory $AttachmentDir -AllowedExtensions $allowedExtensions -ExtractedFiles $extractedFiles)
                    if ($entryId) {
                        [void]$processedEntryIds.Add($entryId)
                    }
                    $summary.processed_outlook_messages++
                } catch {
                    continue
                }
            }
        } finally {
            Release-ComObject -ComObject $items
            Release-ComObject -ComObject $sourceFolder
        }
    } else {
        Process-OutlookMailboxFallback `
            -Namespace $namespace `
            -MailboxName $MailboxName `
            -MailboxFolderPath $MailboxFolderPath `
            -SenderContains $SenderContains `
            -SubjectContains $SubjectContains `
            -ReceivedAfter $receivedAfter `
            -TargetDirectory $AttachmentDir `
            -AllowedExtensions $allowedExtensions `
            -ExtractedFiles $extractedFiles `
            -ProcessedEntryIds $processedEntryIds `
            -Summary $summary
    }
    Write-ProcessedMailboxState `
        -Path $processedMailboxStatePathResolved `
        -EntryIds $processedEntryIds `
        -MailboxName $MailboxName `
        -MailboxFolderPath $MailboxFolderPath `
        -LookbackDays $LookbackDays
}

if ($namespace) {
    Release-ComObject -ComObject $namespace
}
if ($outlook) {
    Release-ComObject -ComObject $outlook
}
[gc]::Collect()
[gc]::WaitForPendingFinalizers()

if (-not $msgFiles -and -not $UseMailboxFallback) {
    $note = 'No .msg files found.'
} elseif (-not $msgFiles -and $UseMailboxFallback -and $summary.matched_outlook_messages -eq 0) {
    $note = 'No .msg files found and no matching Outlook mailbox messages were found.'
} else {
    $note = $null
}

@{
    pass = $true
    mail_drop_dir = $mailDropDirResolved
    attachment_dir = $AttachmentDir
    msg_file_count = $summary.msg_file_count
    mailbox_fallback_used = $summary.mailbox_fallback_used
    mailbox_name = $MailboxName
    mailbox_folder_path = if ($UseMailboxFallback) { $MailboxFolderPath } else { $null }
    matched_outlook_messages = $summary.matched_outlook_messages
    processed_outlook_messages = $summary.processed_outlook_messages
    processed_mailbox_state_path = $processedMailboxStatePathResolved
    extracted_attachment_count = $extractedFiles.Count
    extracted_files = @($extractedFiles)
    processed_emails = $processedEmails
    note = $note
} | ConvertTo-Json -Depth 5
