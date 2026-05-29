import re

with open('server.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove the require statement
code = code.replace("const rateLimit = require('express-rate-limit');", "")

# Replace the express-rate-limit block with a custom native memory limiter
native_limiter = """
// Security: Native Memory Rate Limiting to prevent DDoS
const requestCounts = new Map();
setInterval(() => requestCounts.clear(), 15 * 60 * 1000); // Clear every 15 minutes

const apiLimiter = (req, res, next) => {
    const ip = req.ip || req.connection.remoteAddress;
    const count = (requestCounts.get(ip) || 0) + 1;
    requestCounts.set(ip, count);
    
    if (count > 60) {
        return res.status(429).json({ error: 'Too many requests from this IP, please try again later.' });
    }
    next();
};
"""

# Find the block to replace
start_str = "// Security: Rate Limiting to prevent DDoS and API Abuse"
end_str = "});"
if start_str in code:
    start_idx = code.find(start_str)
    end_idx = code.find(end_str, start_idx) + len(end_str)
    
    old_block = code[start_idx:end_idx]
    code = code.replace(old_block, native_limiter)

with open('server.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Removed express-rate-limit and added native memory limiter.")
