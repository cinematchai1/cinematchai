import re

with open('server.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Add require
if "const rateLimit = require('express-rate-limit');" not in code:
    code = code.replace("const express = require('express');", "const express = require('express');\nconst rateLimit = require('express-rate-limit');")

# Add rate limiter implementation after app initialization
rate_limit_code = """
// Security: Rate Limiting to prevent DDoS and API Abuse
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 60, // Limit each IP to 60 requests per window (4 requests per min)
    message: { error: 'Too many requests from this IP, please try again later.' },
    standardHeaders: true,
    legacyHeaders: false
});
app.use('/api/recommend', apiLimiter);
"""
if "const apiLimiter =" not in code:
    code = code.replace("app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1d' }));", "app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1d' }));\n" + rate_limit_code)

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched server.js with Rate Limiter")
