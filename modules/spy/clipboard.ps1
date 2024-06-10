# Add .NET assembly for accessing clipboard
Add-Type -AssemblyName System.Windows.Forms

# Get the clipboard text
$clipboardText = [System.Windows.Forms.Clipboard]::GetText()

# Define the file path for the output file
$outputFilePath = Join-Path -Path $env:TEMP -ChildPath "clip.txt"

# Try to save the clipboard content to the file
try {
    # Write the clipboard text to the output file
    $clipboardText | Out-File -FilePath $outputFilePath -Encoding utf8

    Write-Host "Clipboard content saved to: $outputFilePath"
} catch {
    # If there is an error, write the error message to the file
    $errorMessage = $_.Exception.Message
    $errorMessage | Out-File -FilePath $outputFilePath -Encoding utf8

    Write-Host "Error occurred. Details saved to: $outputFilePath"
}
