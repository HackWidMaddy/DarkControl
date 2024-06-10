# Define the user data directories for Chrome, Edge, and Firefox
$chromeUserDataDir = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$edgeUserDataDir = "$env:LOCALAPPDATA\Microsoft\Edge\User Data"
$firefoxUserDataDir = "$env:APPDATA\Mozilla\Firefox\Profiles"

# Function to check if a directory contains browsing history
function CheckBrowserHistory {
    param (
        [string]$userDataDir,
        [string]$browserName
    )
    $historyFile = Join-Path -Path $userDataDir -ChildPath "Default\History"

    # Check if the History file exists
    if (Test-Path $historyFile -PathType Leaf) {
        Write-Output "$browserName browsing history found at: $historyFile"
    } else {
        Write-Output "No browsing history found for $browserName"
    }
}

# Create an empty string to accumulate output
$output = ""

# Check Chrome
if (Test-Path $chromeUserDataDir -PathType Container) {
    $output += CheckBrowserHistory -userDataDir $chromeUserDataDir -browserName "Google Chrome" + "`r`n"
} else {
    $output += "Google Chrome user data directory not found." + "`r`n"
}

# Check Edge
if (Test-Path $edgeUserDataDir -PathType Container) {
    $output += CheckBrowserHistory -userDataDir $edgeUserDataDir -browserName "Microsoft Edge" + "`r`n"
} else {
    $output += "Microsoft Edge user data directory not found." + "`r`n"
}

# Check Firefox
$firefoxProfiles = Get-ChildItem -Path $firefoxUserDataDir -Directory
if ($firefoxProfiles) {
    foreach ($profile in $firefoxProfiles) {
        $historyFile = Join-Path -Path $profile.FullName -ChildPath "places.sqlite"
        if (Test-Path $historyFile -PathType Leaf) {
            $output += "Mozilla Firefox browsing history found at: $historyFile" + "`r`n"
        } else {
            # $output += "No browsing history found for Mozilla Firefox profile $($profile.Name)" + "`r`n"
        }
    }
} else {
    # $output += "No Mozilla Firefox profiles found." + "`r`n"
}

# Define the file path for the output file
$outputFilePath = Join-Path -Path $env:TEMP -ChildPath "browser.txt"

# Write the output to the file
$output | Out-File -FilePath $outputFilePath -Encoding utf8

# Output success message
Write-Host "Browser activity information saved to: $outputFilePath"
