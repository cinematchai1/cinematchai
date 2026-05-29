Add-Type -Path "C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\net462\Renci.SshNet.dll"

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

$nodeScript = @"
const fs = require('fs');
let html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');

// Fix e.preventDefault() being called without e
html = html.replace('async function performSearch(isLoadMore = false) {\n            e.preventDefault();', 'async function performSearch(isLoadMore = false) {');

fs.writeFileSync('/root/movie-app/public/index.html', html);
console.log('Fixed e.preventDefault');
"@

$b64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($nodeScript))
$cmd1 = $ssh.RunCommand("echo `"$b64`" | base64 -d > /root/movie-app/patch_v6.js")
$cmd2 = $ssh.RunCommand("cd /root/movie-app && node patch_v6.js")

Write-Host "DEPLOY OUTPUT:"
Write-Host $cmd2.Result
Write-Host "ERRORS:"
Write-Host $cmd2.Error

$ssh.Disconnect()
$ssh.Dispose()
