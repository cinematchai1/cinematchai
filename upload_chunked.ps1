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

Write-Host "Uploading server.js..."
Upload-Base64Chunked "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\server.js" "/root/movie-app/server.b64"
$ssh.RunCommand("base64 -d /root/movie-app/server.b64 > /root/movie-app/server.js")

Write-Host "Uploading package.json..."
Upload-Base64Chunked "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\package.json" "/root/movie-app/package.b64"
$ssh.RunCommand("base64 -d /root/movie-app/package.b64 > /root/movie-app/package.json")

$ssh.RunCommand("mkdir -p /root/movie-app/public/assets/avatars")
for ($i = 1; $i -le 5; $i++) {
    Write-Host "Uploading avatar$i.svg..."
    Upload-Base64Chunked "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\public\assets\avatars\avatar$i.svg" "/root/movie-app/avatar$i.b64"
    $ssh.RunCommand("base64 -d /root/movie-app/avatar$i.b64 > /root/movie-app/public/assets/avatars/avatar$i.svg")
}

Write-Host "Running npm install..."
$cmdNpm = $ssh.RunCommand("cd /root/movie-app && npm install")
Write-Host $cmdNpm.Result
Write-Host $cmdNpm.Error

$ssh.RunCommand('PGPASSWORD=cinematch_pass psql -h 127.0.0.1 -U cinematch_user -d cinematch_db -c "TRUNCATE TABLE recommendation_cache CASCADE;"')
$cmd = $ssh.RunCommand("cd /root/movie-app && pm2 restart movie-app")
Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd.Result
Write-Host "ERRORS:"
Write-Host $cmd.Error

$ssh.Disconnect()
$ssh.Dispose()
