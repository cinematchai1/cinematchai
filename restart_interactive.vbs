Set objShell = WScript.CreateObject("WScript.Shell")
objShell.Run "C:\Users\fjpp8\.gemini\antigravity\scratch\putty\plink.exe -hostkey ""ssh-ed25519 255 SHA256:8M32/X/sgcT1PfMtLgB5HhWhqBTDM/fNLpqhP7yp6Bg"" root@116.203.230.103 ""pm2 restart movie-app"""
WScript.Sleep 1500
objShell.SendKeys "9pNMt43iFAaPKuCWqqtK"
objShell.SendKeys "{ENTER}"
