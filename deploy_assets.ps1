[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll") | Out-Null

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"

Compress-Archive -Path "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\assets" -DestinationPath "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\assets.zip" -Force

$keyboardAuth = New-Object Renci.SshNet.KeyboardInteractiveAuthenticationMethod($username)
$keyboardAuth.add_AuthenticationPrompt({
    param($sender, $e)
    foreach ($prompt in $e.Prompts) {
        if ($prompt.Request -match "Password:") {
            $prompt.Response = $password
        }
    }
})

$passwordAuth = New-Object Renci.SshNet.PasswordAuthenticationMethod($username, $password)
$connInfo = New-Object Renci.SshNet.ConnectionInfo($hostName, 22, $username, $passwordAuth, $keyboardAuth)
$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()

$localFile = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\assets.zip"
$bytes = [System.IO.File]::ReadAllBytes($localFile)
$base64 = [Convert]::ToBase64String($bytes)

$ssh.RunCommand("rm -f /root/movie-app/assets.b64") | Out-Null
$ssh.RunCommand("mkdir -p /root/movie-app/public/assets") | Out-Null

$chunkSize = 30000
for ($i = 0; $i -lt $base64.Length; $i += $chunkSize) {
    $length = [Math]::Min($chunkSize, $base64.Length - $i)
    $chunk = $base64.Substring($i, $length)
    $ssh.RunCommand("echo '$chunk' >> /root/movie-app/assets.b64") | Out-Null
}

$ssh.RunCommand("base64 -d /root/movie-app/assets.b64 > /root/movie-app/assets.zip") | Out-Null
$cmd = $ssh.RunCommand("unzip -o /root/movie-app/assets.zip -d /root/movie-app/public/ && rm /root/movie-app/assets.zip /root/movie-app/assets.b64")
Write-Host "UNZIP OUTPUT:"
Write-Host $cmd.Result

$ssh.Disconnect()
