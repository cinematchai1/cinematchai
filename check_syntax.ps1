[System.Reflection.Assembly]::LoadFrom("C:\Users\fjpp8\.gemini\antigravity\scratch\movie-app\sshnet\lib\netstandard2.0\Renci.SshNet.dll")
$ssh = New-Object Renci.SshNet.SshClient("116.203.230.103", "root", "MovieApp123!@#")
$ssh.Connect()
$cmd = $ssh.RunCommand(@"
node -e "
const fs = require('fs');
const html = fs.readFileSync('/root/movie-app/public/index.html', 'utf8');
const scripts = html.split('<script>');
const lastScript = scripts[scripts.length-1].split('</script>')[0];
fs.writeFileSync('/root/movie-app/test.js', lastScript);
"
node -c /root/movie-app/test.js
"@)
Write-Host "RESULT:"
Write-Host $cmd.Result
Write-Host "ERROR:"
Write-Host $cmd.Error
$ssh.Disconnect()
