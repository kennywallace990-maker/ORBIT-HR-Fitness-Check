param(
    [Parameter(Mandatory = $true)]
    [string]$AttachmentDir,
    [int]$LookbackDays = 21
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

function Get-PreferredAttachmentName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$AttachmentName,
        [Parameter(Mandatory = $true)]
        [string]$MailSubject,
        [Parameter(Mandatory = $true)]
        [datetime]$ReceivedDate
    )

    $safeName = ConvertTo-SafeFileName -Value $AttachmentName
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($safeName)
    $extension = [System.IO.Path]::GetExtension($safeName)
    $dateStamp = $ReceivedDate.ToString('yyyy-MM-dd')

    if ($MailSubject -like '*Resolved Cases*') {
        $prefix = 'resolved_cases'
    } elseif ($MailSubject -like '*Open Cases*') {
        $prefix = 'open_cases'
    } else {
        return $safeName
    }

    if ($baseName.ToLowerInvariant().StartsWith($prefix + '_')) {
        return $safeName
    }

    return '{0}_{1}_{2}{3}' -f $prefix, $dateStamp, $baseName, $extension
}

if (-not (Test-Path -LiteralPath $AttachmentDir)) {
    New-Item -ItemType Directory -Path $AttachmentDir | Out-Null
}
$attachmentDirResolved = (Resolve-Path -LiteralPath $AttachmentDir).Path

$allowedExtensions = @('.csv', '.xlsx', '.xlsm')
$extractedFiles = [System.Collections.Generic.List[string]]::new()
$matchedMessages = 0
$processedMessages = 0
$receivedAfter = (Get-Date).Date.AddDays(-1 * $LookbackDays)

$outlook = $null
$namespace = $null
$inbox = $null
$items = $null

try {
    $outlook = New-Object -ComObject Outlook.Application
    $namespace = $outlook.GetNamespace('MAPI')
    $inbox = $namespace.GetDefaultFolder(6)
    $items = $inbox.Items
    $items.Sort('[ReceivedTime]', $true)

    foreach ($item in @($items)) {
        try {
            if ($item.Class -ne 43) {
                continue
            }

            $received = [datetime]$item.ReceivedTime
            if ($received -lt $receivedAfter) {
                break
            }

            $subject = [string]$item.Subject
            $sender = [string]$item.SenderEmailAddress
            if (($subject -like '*WBR Previous Week Open Cases*' -or $subject -like '*WBR Previous Week Resolved Cases*') -and ($sender -like '*ServiceDesk@chewy.com*')) {
                $matchedMessages++
                if ($item.Attachments -ne $null -and $item.Attachments.Count -gt 0) {
                    for ($index = 1; $index -le $item.Attachments.Count; $index++) {
                        $attachment = $null
                        try {
                            $attachment = $item.Attachments.Item($index)
                            $preferredName = Get-PreferredAttachmentName -AttachmentName $attachment.FileName -MailSubject $subject -ReceivedDate $received
                            $extension = [System.IO.Path]::GetExtension($preferredName).ToLowerInvariant()
                            if ($allowedExtensions -notcontains $extension) {
                                continue
                            }

                            $targetPath = Join-Path $attachmentDirResolved $preferredName
                            if (-not (Test-Path -LiteralPath $targetPath)) {
                                $attachment.SaveAsFile($targetPath)
                                $extractedFiles.Add($targetPath)
                            }
                        } finally {
                            Release-ComObject -ComObject $attachment
                        }
                    }
                }
                $processedMessages++
            }
        } catch {
            continue
        }
    }
} finally {
    Release-ComObject -ComObject $items
    Release-ComObject -ComObject $inbox
    Release-ComObject -ComObject $namespace
    Release-ComObject -ComObject $outlook
    [gc]::Collect()
    [gc]::WaitForPendingFinalizers()
}

@{
    pass = $true
    attachment_dir = $attachmentDirResolved
    mailbox_folder_path = 'Inbox'
    lookback_days = $LookbackDays
    matched_outlook_messages = $matchedMessages
    processed_outlook_messages = $processedMessages
    extracted_attachment_count = $extractedFiles.Count
    extracted_files = @($extractedFiles)
    note = if ($matchedMessages -eq 0) { 'No matching Outlook Inbox messages were found.' } else { $null }
} | ConvertTo-Json -Depth 5
