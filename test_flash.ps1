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

$cmd = $ssh.RunCommand("cd /root/movie-app && node -e `"require('dotenv').config(); const https = require('https'); const req = https.request({hostname: 'generativelanguage.googleapis.com', path: '/v1beta/models/gemini-1.5-flash:generateContent?key=' + process.env.GEMINI_API_KEY, method: 'POST', headers: {'Content-Type': 'application/json'}}, res => { let body = ''; res.on('data', d => body += d); res.on('end', () => console.log('FLASH:', body)); }); req.write(JSON.stringify({contents: [{parts: [{text: 'hi'}]}]})); req.end();`"")
Write-Host "FLASH TEST:"
Write-Host $cmd.Result

$ssh.Disconnect()
$ssh.Dispose()
