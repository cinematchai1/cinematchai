[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll")

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"

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

$localFile = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\favicon.png"
$bytes = [System.IO.File]::ReadAllBytes($localFile)
$base64 = [Convert]::ToBase64String($bytes)

$ssh.RunCommand("rm -f /root/movie-app/public/favicon.b64") | Out-Null

$chunkSize = 30000
for ($i = 0; $i -lt $base64.Length; $i += $chunkSize) {
    $length = [Math]::Min($chunkSize, $base64.Length - $i)
    $chunk = $base64.Substring($i, $length)
    $ssh.RunCommand("echo '$chunk' >> /root/movie-app/public/favicon.b64") | Out-Null
}

$ssh.RunCommand("base64 -d /root/movie-app/public/favicon.b64 > /root/movie-app/public/favicon.png") | Out-Null
$ssh.Disconnect()
Write-Host "Favicon uploaded."
