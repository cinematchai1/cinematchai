[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll")
$hostName = "116.203.230.103"
$username = "root"
$password = "MovieApp123!@#"
$passwordAuth = New-Object Renci.SshNet.PasswordAuthenticationMethod($username, $password)
$keyboardAuth = New-Object Renci.SshNet.KeyboardInteractiveAuthenticationMethod($username)
$keyboardAuth.add_AuthenticationPrompt({
    param($sender, $e)
    foreach ($prompt in $e.Prompts) {
        if ($prompt.Request.IndexOf("Password", [System.StringComparison]::InvariantCultureIgnoreCase) -ne -1) {
            $prompt.Response = $password
        }
    }
})
$connInfo = New-Object Renci.SshNet.ConnectionInfo($hostName, 22, $username, $passwordAuth, $keyboardAuth)
$ssh = New-Object Renci.SshNet.SshClient($connInfo)
$ssh.Connect()

$cmd = $ssh.CreateCommand("cat << 'EOF' > /root/extractor.js
const fs = require('fs');
const html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if(scriptMatch) {
    fs.writeFileSync('/root/temp.js', scriptMatch[1]);
    console.log('Extract successful. Linting...');
} else {
    console.log('No script tag found!');
}
EOF
node /root/extractor.js
node -c /root/temp.js 2>&1
")
$cmd.Execute()
Write-Host "Result:" $cmd.Result

$ssh.Disconnect()
