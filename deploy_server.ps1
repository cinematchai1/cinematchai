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

$localFile = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js"
$content = Get-Content $localFile -Raw -Encoding UTF8
$base64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))

$ssh.RunCommand("rm -f /root/movie-app/server.b64") | Out-Null

$chunkSize = 30000
for ($i = 0; $i -lt $base64.Length; $i += $chunkSize) {
    $length = [Math]::Min($chunkSize, $base64.Length - $i)
    $chunk = $base64.Substring($i, $length)
    $ssh.RunCommand("echo '$chunk' >> /root/movie-app/server.b64") | Out-Null
}

$ssh.RunCommand("base64 -d /root/movie-app/server.b64 > /root/movie-app/server.js") | Out-Null
$cmd = $ssh.RunCommand("pm2 restart movie-app")
Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result

$ssh.Disconnect()
