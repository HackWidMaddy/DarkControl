# Get the list of Wi-Fi profiles
$wifiProfiles = netsh wlan show profiles | Select-String -Pattern "All User Profile" | ForEach-Object {
    $_ -replace ".*: ", ""
}

# Function to save profiles and passwords to a file
function Save-ProfilesToFile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        [Parameter(ValueFromPipeline=$true)]
        [string]$Profile,
        [Parameter(ValueFromPipeline=$true)]
        [string]$Password
    )

    process {
        # Write profile and password to the file, overwriting if it already exists
        Add-Content -Path $FilePath -Value "Profile: $Profile" -Force
        Add-Content -Path $FilePath -Value "Password: $Password" -Force
        Add-Content -Path $FilePath -Value "" -Force
    }
}

# Get the temporary directory
$tempDirectory = [System.IO.Path]::GetTempPath()

# Define the file path for saving profiles
$filePath = Join-Path -Path $tempDirectory -ChildPath "profiles.txt"

# Iterate through each profile and retrieve the key
foreach ($profile in $wifiProfiles) {
    # Write-Host "`nProfile: $profile"
    $profileInfo = netsh wlan show profile name="$profile" key=clear

    # Extract the key
    $key = $profileInfo | Select-String -Pattern "Key Content" | ForEach-Object {
        $_ -replace ".*: ", ""
    }

    if ($key) {
        # Write-Host "Key: $key"
        # Save profile and password to the file
        $profile | Save-ProfilesToFile -FilePath $filePath -Password $key
    } else {
        # Write-Host "Key: Not found or not set"
    }
}

Write-Host "Profiles and passwords saved to: $filePath"
