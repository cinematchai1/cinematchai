[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll")

$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"

$keyboardAuth = New-Object Renci.SshNet.KeyboardInteractiveAuthenticationMethod($username)
$keyboardAuth.add_AuthenticationPrompt({
    param($sender, $e)
    foreach ($prompt in $e.Prompts) {
        if ($prompt.Request.IndexOf("Password", [System.StringComparison]::InvariantCultureIgnoreCase) -ne -1) {
            $prompt.Response = $password
        }
    }
})

$passwordAuth = New-Object Renci.SshNet.PasswordAuthenticationMethod($username, $password)
$connInfo = New-Object Renci.SshNet.ConnectionInfo($hostName, 22, $username, $passwordAuth, $keyboardAuth)
$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()

$localFile = "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\index.html"
$content = Get-Content $localFile -Raw -Encoding UTF8
$base64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))

Write-Host "Cleaning remote temp file..."
$ssh.RunCommand("rm -f /root/movie-app/public/index.b64") | Out-Null

Write-Host "Uploading index.html in base64 chunks (Size: $($base64.Length) bytes)..."
$chunkSize = 30000
for ($i = 0; $i -lt $base64.Length; $i += $chunkSize) {
    $length = [Math]::Min($chunkSize, $base64.Length - $i)
    $chunk = $base64.Substring($i, $length)
    $ssh.RunCommand("echo '$chunk' >> /root/movie-app/public/index.b64") | Out-Null
}

Write-Host "Decoding remote file..."
$ssh.RunCommand("base64 -d /root/movie-app/public/index.b64 > /root/movie-app/public/index.html") | Out-Null

Write-Host "Restarting PM2..."
$cmd = $ssh.RunCommand("pm2 restart movie-app")
Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result

$ssh.Disconnect()
$ssh.Dispose()
Write-Host "Done."
