$soundFilePath = "main.wav"

# Check if the sound file exists
if (Test-Path $soundFilePath -PathType Leaf) {
    # Create a SoundPlayer object
    $soundPlayer = New-Object System.Media.SoundPlayer

    # Set the sound file path
    $soundPlayer.SoundLocation = $soundFilePath

    try {
        # Load the sound file
        $soundPlayer.Load()
        
        # Play the sound
        $soundPlayer.PlaySync() # PlaySync to ensure the script waits until the sound is finished
        Write-Host "Sound is playing..."
        
        # Remove the sound file after playing
        Remove-Item $soundFilePath -ErrorAction Stop
        Write-Host "Sound file deleted."
    } catch {
        Write-Host "Error: $_"
    }
} else {
    Write-Host "Sound file not found."
}
