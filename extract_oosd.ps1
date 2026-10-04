$content = [System.IO.File]::ReadAllText("$PSScriptRoot\assignments\OOSD_2026_All_Assignments_Interactive_Quiz_MCQ_MSQ.html")
$startIndex = $content.IndexOf("const questions = [")
if ($startIndex -ge 0) {
    $startIndex += "const questions = ".Length
    $endIndex = $content.IndexOf("];`nconst STORAGE_KEY", $startIndex)
    if ($endIndex -lt 0) {
        $endIndex = $content.IndexOf("];`r`nconst STORAGE_KEY", $startIndex)
    }
    if ($endIndex -lt 0) {
        $endIndex = $content.IndexOf("const STORAGE_KEY", $startIndex)
        $endIndex = $content.LastIndexOf("]", $endIndex) + 1
    } else {
        $endIndex += 1
    }
    
    $json = $content.Substring($startIndex, $endIndex - $startIndex)
    [System.IO.File]::WriteAllText("$PSScriptRoot\data_oosd_raw.json", $json, [System.Text.Encoding]::UTF8)
    Write-Host "Extracted OOSD JSON successfully. Length: $($json.Length)"
} else {
    Write-Host "Could not find questions marker"
}
