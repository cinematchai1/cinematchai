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

function Upload-Base64Chunked($filePath, $remoteBase64Path) {
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $b64 = [System.Convert]::ToBase64String($bytes)
    
    $ssh.RunCommand("rm -f $remoteBase64Path")
    
    $chunkSize = 30000
    for ($i = 0; $i -lt $b64.Length; $i += $chunkSize) {
        $len = [Math]::Min($chunkSize, $b64.Length - $i)
        $chunk = $b64.Substring($i, $len)
        $ssh.RunCommand("echo -n `"$chunk`" >> $remoteBase64Path")
    }
}

Write-Host "Uploading public/index.html..."
Upload-Base64Chunked "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\index.html" "/root/movie-app/index.b64"
$ssh.RunCommand("base64 -d /root/movie-app/index.b64 > /root/movie-app/public/index.html")

$cmd = $ssh.RunCommand("cd /root/movie-app && npm install google-auth-library@7.14.1 && pm2 restart movie-app")
Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result
Write-Host "ERRORS:"
Write-Host $cmd.Error

$ssh.Disconnect()
$ssh.Dispose()
