const express = require('express');

const compression = require('compression');
const path = require('path');
const { OAuth2Client } = require('google-auth-library');
const https = require('https');
const bcrypt = require('bcrypt');
const session = require('express-session');
const pgSession = require('connect-pg-simple')(session);
const { Pool } = require('pg');
const multer = require('multer');
const sharp = require('sharp');
const fs = require('fs');
const crypto = require('crypto');

// Removed resend SDK because Node v12 on server doesn't support it
// We will use native https module which is already required as 'https'

const app = express();

app.use(compression());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1d' }));


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

app.use('/api/recommend', apiLimiter);


// Ensure upload directory exists
const avatarDir = path.join(__dirname, 'public', 'uploads', 'avatars');
if (!fs.existsSync(avatarDir)) {
    fs.mkdirSync(avatarDir, { recursive: true });
}

// Multer config
const storage = multer.memoryStorage(); // Process with sharp before saving
const upload = multer({ 
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB limit
    fileFilter: (req, file, cb) => {
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('Only images are allowed'));
        }
    }
});


const pool = new Pool({
    user: process.env.DB_USER || 'cinematch_user',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'cinematch_db',
    password: process.env.DB_PASSWORD || 'cinematch_pass',
    port: process.env.DB_PORT || 5432,
});
async function initDatabase() {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255),
                display_name VARCHAR(50),
                avatar_url VARCHAR(255),
                google_id VARCHAR(255) UNIQUE,
                preferences JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);

        await pool.query(`
            CREATE TABLE IF NOT EXISTS password_resets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);

app.use(session({
    store: new pgSession({
        pool: pool,
        tableName: 'session'
    }),
    secret: 'super_secret_cinematch_key_2026',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false, maxAge: 1000 * 60 * 60 * 24 * 30 } // 30 days
}));

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GROQ_API_KEY = process.env.GROQ_API_KEY;

async function fetchFromGroq(promptText, limit, surpriseMe) {
    return new Promise((resolve, reject) => {
        const sysMsg = `You are a movie recommendation API. Analyze the user's reference title based on emotional tone, aesthetic style, thematic subtext, and pacing. Ensure all provided 'imdb_id' fields are absolutely correct. Output ONLY valid JSON matching this schema exactly: {"ref": {"imdb_id": "tt...", "type": "movie"}, "recs": [{"imdb_id": "tt...", "type": "movie"}]}. Do not hallucinate IDs. Do not include markdown formatting.`;
        
        const payload = JSON.stringify({
            model: "llama-3.1-8b-instant",
            messages: [
                { role: "system", content: sysMsg },
                { role: "user", content: promptText + `\nLimit recommendations to ${limit}. Provide raw JSON only.` }
            ],
            temperature: surpriseMe ? 0.8 : 0.4,
            response_format: { type: "json_object" }
        });

        const options = {
            hostname: 'api.groq.com',
            port: 443,
            path: '/openai/v1/chat/completions',
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${GROQ_API_KEY}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(payload)
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    if (data.choices && data.choices[0] && data.choices[0].message) {
                        resolve(data.choices[0].message.content);
                    } else {
                        reject(new Error("Groq API error: " + body));
                    }
                } catch(e) {
                    reject(e);
                }
            });
        });

        req.on('error', (e) => reject(e));
        req.write(payload);
        req.end();
    });
}
        await pool.query(`
            CREATE TABLE IF NOT EXISTS recommendation_cache (
                id SERIAL PRIMARY KEY,
                search_query VARCHAR(255) NOT NULL,
                language VARCHAR(10) NOT NULL,
                reference_movie JSONB NOT NULL,
                recommendations JSONB NOT NULL,
                raw_recommendations JSONB DEFAULT '[]'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(search_query, language)
            )
        `);

        await pool.query(`
            CREATE TABLE IF NOT EXISTS user_watchlist (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                imdb_id VARCHAR(50),
                title VARCHAR(255) NOT NULL,
                original_title VARCHAR(255),
                year VARCHAR(50),
                type VARCHAR(50) DEFAULT 'movie',
                rating VARCHAR(50),
                duration VARCHAR(100),
                category VARCHAR(255),
                description TEXT,
                trailer_yt_id VARCHAR(100),
                poster TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, title, year)
            )
        `);

        await pool.query(`
            CREATE TABLE IF NOT EXISTS donations (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                currency VARCHAR(10) DEFAULT 'EUR',
                created_at TIMESTAMP DEFAULT NOW()
            )
        `);

        await pool.query(`
            CREATE TABLE IF NOT EXISTS movies_cache (
                imdb_id VARCHAR(50) NOT NULL,
                language VARCHAR(10) NOT NULL,
                title VARCHAR(255) NOT NULL,
                type VARCHAR(50) DEFAULT 'movie',
                tmdb_data JSONB,
                omdb_data JSONB,
                cinemeta_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (imdb_id, language)
            )
        `);
        console.log("Database tables initialized successfully.");
    } catch (err) {
        console.error("Error initializing database tables:", err);
    }
}
initDatabase();

// AUTH ROUTES
// --- Google OAuth Setup ---
function getGoogleClient(req) {
    const protocol = req.headers['x-forwarded-proto'] || req.protocol;
    const host = req.get('host');
    const redirectUri = `${protocol}://${host}/api/auth/google/callback`;
    return new OAuth2Client(
        process.env.GOOGLE_CLIENT_ID,
        process.env.GOOGLE_CLIENT_SECRET,
        redirectUri
    );
}

app.get('/api/auth/google', (req, res) => {
    const client = getGoogleClient(req);
    const url = client.generateAuthUrl({
        access_type: 'offline',
        scope: ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']
    });
    res.redirect(url);
});

app.get('/api/auth/google/callback', async (req, res) => {
    const code = req.query.code;
    if (!code) return res.redirect('/?error=NoCode');
    try {
        const client = getGoogleClient(req);
        const { tokens } = await client.getToken(code);
        client.setCredentials(tokens);
        
        let payload;
        if (tokens.id_token) {
            const ticket = await client.verifyIdToken({
                idToken: tokens.id_token,
                audience: process.env.GOOGLE_CLIENT_ID
            });
            payload = ticket.getPayload();
        } else {
            const resProfile = await client.request({url: 'https://www.googleapis.com/oauth2/v2/userinfo'});
            payload = resProfile.data;
        }

        const googleId = payload.id || payload.sub;
        const email = payload.email;
        const name = payload.name;
        const picture = payload.picture;
        
        let userResult = await pool.query('SELECT * FROM users WHERE google_id = $1 OR username = $2', [googleId, email]);
        let user;
        
        if (userResult.rows.length === 0) {
            const result = await pool.query(
                'INSERT INTO users (username, display_name, avatar_url, google_id) VALUES ($1, $2, $3, $4) RETURNING *',
                [email, name, picture, googleId]
            );
            user = result.rows[0];
            
            // Send Welcome Email to the new Google user
            if (typeof sendWelcomeEmail === 'function') {
                sendWelcomeEmail(email, name).catch(e => console.error("Error sending welcome email to Google user:", e));
            }
        } else {
            user = userResult.rows[0];
            if (!user.google_id) {
                await pool.query('UPDATE users SET google_id = $1, display_name = $2, avatar_url = $3 WHERE id = $4', [googleId, name, picture, user.id]);
                user.google_id = googleId;
                user.display_name = name;
                user.avatar_url = picture;
            } else if (!user.avatar_url && picture) {
                await pool.query('UPDATE users SET avatar_url = $1 WHERE id = $2', [picture, user.id]);
                user.avatar_url = picture;
            }
        }
        
        req.session.userId = user.id;
        req.session.username = user.username;
        req.session.displayName = user.display_name;
        req.session.avatarUrl = user.avatar_url;
        
        res.redirect('/');
    } catch (err) {
        console.error('Google Auth Error:', err);
        res.redirect('/?error=AuthFailed');
    }
});

app.post('/api/register', async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) return res.status(400).json({ error: 'Username and password required' });
        
        const existing = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
        if (existing.rows.length > 0) return res.status(400).json({ error: 'Username already exists' });

        const hash = await bcrypt.hash(password, 10);
        const result = await pool.query('INSERT INTO users (username, password_hash, display_name) VALUES ($1, $2, $3) RETURNING id, username, display_name, avatar_url', [username, hash, username]);
        
        req.session.userId = result.rows[0].id;
        req.session.username = result.rows[0].username;

        // Send Welcome Email
        const emailHtml = `
            <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #09090b; padding: 40px 20px; color: #e2e8f0; text-align: center;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #18181b; padding: 40px; border-radius: 16px; border: 1px solid #27272a; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);">
                    <h1 style="color: #fff; font-size: 24px; margin-bottom: 8px; font-weight: 800; letter-spacing: -0.5px;">CineMatch AI</h1>
                    <h2 style="color: #38bdf8; font-size: 18px; font-weight: 500; margin-top: 0; margin-bottom: 24px;">Welcome to the Future of Movies</h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #cbd5e1; margin-bottom: 24px; text-align: left;">
                        Hello <strong>${result.rows[0].display_name.split('@')[0]}</strong>,<br><br>Thank you for joining CineMatch AI! We are thrilled to have you on board. Start exploring our AI-powered recommendation engine to find your next favorite movie.
                    </p>
                    
                    <a href="https://cinematchai.com" style="display: inline-block; padding: 14px 28px; background: linear-gradient(135deg, #0ea5e9, #3b82f6); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; letter-spacing: 0.5px; margin: 10px 0 30px; box-shadow: 0 4px 14px 0 rgba(14, 165, 233, 0.39);">Discover Movies</a>
                    
                    <hr style="border: 0; height: 1px; background-color: #27272a; margin: 24px 0;">
                    
                    <p style="font-size: 13px; line-height: 1.5; color: #64748b; margin: 0; text-align: left;">
                        If you have any questions, feel free to contact us at info@cinematchai.com.
                    </p>
                </div>
                <p style="font-size: 12px; color: #475569; margin-top: 24px;">
                    © 2026 CineMatch AI. All rights reserved.
                </p>
            </div>`;

        const emailData = JSON.stringify({
            from: 'CineMatch AI <send@cinematchai.com>',
            to: [username],
            subject: 'Welcome to CineMatch AI 🍿',
            html: emailHtml
        });
        
        const options = {
            hostname: 'api.resend.com',
            port: 443,
            path: '/emails',
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + (process.env.RESEND_API_KEY || 're_C3yX7GPy_FBPjBPAEnBzQo1v8GjEQGf48'),
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(emailData)
            }
        };
        
        const https = require('https');
        const resendReq = https.request(options, (resendRes) => {
            resendRes.on('data', () => {});
        });
        resendReq.on('error', (e) => console.error('Failed to send welcome email:', e));
        resendReq.write(emailData);
        resendReq.end();

        res.json({ success: true, user: result.rows[0] });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during registration' });
    }
});

app.post('/api/login', async (req, res) => {
    console.log('[LOGIN API] Request received for:', req.body.username);
    try {
        const { username, password } = req.body;
        if (!username || !password) return res.status(400).json({ error: 'Username and password required' });
        
        const result = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
        if (result.rows.length === 0) return res.status(401).json({ error: 'Invalid credentials' });

        const user = result.rows[0];
        const match = await bcrypt.compare(password, user.password_hash);
        if (!match) return res.status(401).json({ error: 'Invalid credentials' });

        const rememberMe = req.body.rememberMe || false;

        req.session.userId = user.id;
        req.session.username = user.username;
        req.session.displayName = user.display_name;
        req.session.avatarUrl = user.avatar_url;
        
        req.session.cookie.maxAge = 1000 * 60 * 60 * 24 * 30; // 30 days always

        req.session.save((err) => {
            if (err) console.error("Session save error:", err);
            res.json({ success: true, user: { id: user.id, username: user.username, display_name: user.display_name, avatar_url: user.avatar_url } });
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error during login' });
    }
});

app.post('/api/auth/forgot-password', async (req, res) => {
    const { username, lang = 'pt' } = req.body;
    if (!username) return res.status(400).json({ error: lang === 'en' ? 'Email required' : 'Email obrigatório' });

    try {
        const result = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
        if (result.rows.length === 0) {
            return res.json({ success: true, message: lang === 'en' ? 'If the email exists, we sent a recovery link.' : 'Se o email existir, enviámos um link de recuperação.' });
        }
        
        const user = result.rows[0];
        const token = crypto.randomBytes(32).toString('hex');
        const expiresAt = new Date(Date.now() + 3600000); // 1 hour
        
        await pool.query(
            'INSERT INTO password_resets (user_id, token, expires_at) VALUES ($1, $2, $3)',
            [user.id, token, expiresAt]
        );
        
        const protocol = req.headers['x-forwarded-proto'] || req.protocol;
        const host = req.get('host');
        const resetLink = `${protocol}://${host}?reset=${token}`;
        
        let emailSubject = 'Recuperação de Password - CineMatch AI';
        let emailTitle = 'Recuperação de Password';
        let emailGreeting = `Olá <strong>${user.display_name}</strong>,<br><br>Recebemos um pedido para redefinir a password da tua conta. Clica no botão abaixo para escolher uma nova password segura.`;
        let emailButton = 'Redefinir Password';
        let emailFooter = 'Se não fizeste este pedido, podes simplesmente ignorar este email. A tua conta permanece segura e o link expirará em 1 hora.';
        let emailRights = 'Todos os direitos reservados.';
        
        if (lang === 'en') {
            emailSubject = 'Password Recovery - CineMatch AI';
            emailTitle = 'Password Recovery';
            emailGreeting = `Hello <strong>${user.display_name}</strong>,<br><br>We received a request to reset your account password. Click the button below to choose a new secure password.`;
            emailButton = 'Reset Password';
            emailFooter = 'If you did not make this request, you can safely ignore this email. Your account remains secure and the link will expire in 1 hour.';
            emailRights = 'All rights reserved.';
        }
        
        const emailHtml = `
            <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #09090b; padding: 40px 20px; color: #e2e8f0; text-align: center;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #18181b; padding: 40px; border-radius: 16px; border: 1px solid #27272a; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);">
                    <h1 style="color: #fff; font-size: 24px; margin-bottom: 8px; font-weight: 800; letter-spacing: -0.5px;">CineMatch AI</h1>
                    <h2 style="color: #38bdf8; font-size: 18px; font-weight: 500; margin-top: 0; margin-bottom: 24px;">${emailTitle}</h2>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #cbd5e1; margin-bottom: 24px; text-align: left;">
                        ${emailGreeting}
                    </p>
                    
                    <a href="${resetLink}" style="display: inline-block; padding: 14px 28px; background: linear-gradient(135deg, #0ea5e9, #3b82f6); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; letter-spacing: 0.5px; margin: 10px 0 30px; box-shadow: 0 4px 14px 0 rgba(14, 165, 233, 0.39);">${emailButton}</a>
                    
                    <hr style="border: 0; height: 1px; background-color: #27272a; margin: 24px 0;">
                    
                    <p style="font-size: 13px; line-height: 1.5; color: #64748b; margin: 0; text-align: left;">
                        ${emailFooter}
                    </p>
                </div>
                <p style="font-size: 12px; color: #475569; margin-top: 24px;">
                    © 2026 CineMatch AI. ${emailRights}
                </p>
            </div>`;
            
        // Call Resend API natively
        const emailData = JSON.stringify({
            from: 'CineMatch AI <send@cinematchai.com>',
            to: [username],
            subject: emailSubject,
            html: emailHtml
        });
        
        const options = {
            hostname: 'api.resend.com',
            port: 443,
            path: '/emails',
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + (process.env.RESEND_API_KEY || 're_C3yX7GPy_FBPjBPAEnBzQo1v8GjEQGf48'),
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(emailData)
            }
        };
        
        await new Promise((resolve, reject) => {
            const resendReq = https.request(options, (resendRes) => {
                let body = '';
                resendRes.on('data', chunk => body += chunk);
                resendRes.on('end', () => {
                    if(resendRes.statusCode >= 200 && resendRes.statusCode < 300) resolve();
                    else reject(new Error('Resend error: ' + body));
                });
            });
            resendReq.on('error', reject);
            resendReq.write(emailData);
            resendReq.end();
        });
        
        res.json({ success: true, message: lang === 'en' ? 'Recovery email sent!' : 'Email de recuperação enviado!' });
    } catch (err) {
        console.error('Forgot password error:', err);
        res.status(500).json({ error: 'Server error' });
    }
});

app.post('/api/auth/reset-password', async (req, res) => {
    const { token, newPassword } = req.body;
    if (!token || !newPassword) return res.status(400).json({ error: 'Token and new password required' });
    
    try {
        const result = await pool.query('SELECT * FROM password_resets WHERE token = $1 AND expires_at > NOW()', [token]);
        if (result.rows.length === 0) return res.status(400).json({ error: 'Token inválido ou expirado.' });
        
        const reset = result.rows[0];
        const hash = await bcrypt.hash(newPassword, 10);
        
        await pool.query('UPDATE users SET password_hash = $1 WHERE id = $2', [hash, reset.user_id]);
        await pool.query('DELETE FROM password_resets WHERE token = $1', [token]);
        
        res.json({ success: true, message: 'Password alterada com sucesso!' });
    } catch (err) {
        console.error('Reset password error:', err);
        res.status(500).json({ error: 'Server error' });
    }
});

app.post('/api/logout', (req, res) => {
    req.session.destroy();
    res.json({ success: true });
});

app.get('/api/me', async (req, res) => {
    if (req.session.userId) {
        try {
            const result = await pool.query('SELECT username, display_name, avatar_url FROM users WHERE id = $1', [req.session.userId]);
            if (result.rows.length > 0) {
                const u = result.rows[0];
                res.json({ loggedIn: true, username: u.username, display_name: u.display_name, avatar_url: u.avatar_url });
            } else {
                res.json({ loggedIn: false });
            }
        } catch (err) {
            res.json({ loggedIn: false });
        }
    } else {
        res.json({ loggedIn: false });
    }
});

app.get('/api/profile', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    try {
        const result = await pool.query('SELECT preferences FROM users WHERE id = $1', [req.session.userId]);
        if (result.rows.length > 0) {
            res.json(result.rows[0].preferences || {});
        } else {
            res.status(404).json({ error: 'User not found' });
        }
    } catch (err) {
        console.error("Error fetching profile:", err);
        res.status(500).json({ error: 'Server error' });
    }
});

app.put('/api/profile', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    try {
        const { preferences } = req.body;
        await pool.query('UPDATE users SET preferences = $1 WHERE id = $2', [JSON.stringify(preferences || {}), req.session.userId]);
        res.json({ success: true });
    } catch (err) {
        console.error("Error updating profile:", err);
        res.status(500).json({ error: 'Server error' });
    }
});

app.post('/api/profile/upload-avatar', upload.single('avatar'), async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

    try {
        const filename = `avatar_${req.session.userId}_${Date.now()}.webp`;
        const filepath = path.join(avatarDir, filename);

        // Process image with sharp: resize, strip EXIF, convert to WebP
        await sharp(req.file.buffer)
            .resize(256, 256, { fit: 'cover' })
            .webp({ quality: 80 })
            .toFile(filepath);

        const avatarUrl = `/uploads/avatars/${filename}`;

        await pool.query('UPDATE users SET avatar_url = $1 WHERE id = $2', [avatarUrl, req.session.userId]);

        res.json({ success: true, avatar_url: avatarUrl });
    } catch (err) {
        console.error("Error processing avatar:", err);
        res.status(500).json({ error: 'Error processing image' });
    }
});

app.post('/api/profile/update-display', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    try {
        const { display_name, avatar_url } = req.body;
        
        let query = 'UPDATE users SET display_name = $1';
        let params = [display_name || null];
        let paramIndex = 2;

        if (avatar_url !== undefined) {
            query += `, avatar_url = $${paramIndex}`;
            params.push(avatar_url);
            paramIndex++;
        }

        query += ` WHERE id = $${paramIndex}`;
        params.push(req.session.userId);

        await pool.query(query, params);
        res.json({ success: true });
    } catch (err) {
        console.error("Error updating display info:", err);
        res.status(500).json({ error: 'Server error' });
    }
});

app.get('/api/donations/leaderboard', async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT username, SUM(amount) as total_amount 
            FROM donations 
            GROUP BY username 
            ORDER BY total_amount DESC 
            LIMIT 10
        `);
        res.json({ success: true, leaderboard: result.rows });
    } catch (e) {
        console.error("Leaderboard error:", e);
        res.status(500).json({ error: 'Failed to fetch leaderboard' });
    }
});

function fetchCinemetaData(title, type = 'movie') {
    return new Promise((resolve) => {
        if (!title) return resolve(null);
        
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const url = `https://v3-cinemeta.strem.io/catalog/${cleanType}/top/search=${encodeURIComponent(title)}.json`;
        
        const req = https.get(url, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    if (data && data.metas && data.metas.length > 0) {
                        resolve(data.metas[0]);
                    } else {
                        resolve(null);
                    }
                } catch(e) {
                    resolve(null);
                }
            });
        });

        req.on('error', () => resolve(null));
        
        // Prevent hanging
        req.setTimeout(3000, () => {
            req.abort();
            resolve(null);
        });
    });
}

function fetchCinemetaMeta(imdbId, type) {
    return new Promise((resolve) => {
        if (!imdbId) return resolve(null);
        
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const url = `https://v3-cinemeta.strem.io/meta/${cleanType}/${imdbId}.json`;
        
        const req = https.get(url, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    resolve(data && data.meta ? data.meta : null);
                } catch(e) {
                    resolve(null);
                }
            });
        });

        req.on('error', () => resolve(null));
        
        // Prevent hanging
        req.setTimeout(3000, () => {
            req.abort();
            resolve(null);
        });
    });
}

function fetchOMDB(imdbId) {
    return new Promise((resolve) => {
        if (!imdbId) return resolve(null);
        const apiKey = '25c26a4';
        const url = `https://www.omdbapi.com/?i=${imdbId}&apikey=${apiKey}`;
        const req = https.get(url, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(body)); } catch(e) { resolve(null); }
            });
        });
        req.on('error', () => resolve(null));
        req.setTimeout(3000, () => { req.abort(); resolve(null); });
    });
}


async function fetchAndCacheMetadata(imdbId, type, language) {
    if (!imdbId) return null;
    
    try {
        const cacheQuery = await pool.query('SELECT tmdb_data, omdb_data, cinemeta_data, title, type FROM movies_cache WHERE imdb_id = $1 AND language = $2', [imdbId, language]);
        
        let tmdb = null;
        let omdb = null;
        let cinemeta = null;
        let cachedTitle = null;
        let cachedType = type || 'movie';

        if (cacheQuery.rows.length > 0) {
            tmdb = cacheQuery.rows[0].tmdb_data;
            omdb = cacheQuery.rows[0].omdb_data;
            cinemeta = cacheQuery.rows[0].cinemeta_data;
            cachedTitle = cacheQuery.rows[0].title;
            cachedType = cacheQuery.rows[0].type || cachedType;
        }

        if (tmdb && omdb) {
            return { tmdb, omdb, cinemeta, title: cachedTitle, type: cachedType };
        }

        const tasks = [];
        if (!tmdb && !cinemeta) tasks.push(fetchTMDBMeta(imdbId, type, language).then(data => tmdb = data));
        if (!omdb) tasks.push(fetchOMDB(imdbId).then(data => omdb = data));

        if (tasks.length > 0) await Promise.all(tasks);

        if (!tmdb && !cinemeta) {
            cinemeta = await fetchCinemetaMeta(imdbId, type);
        }

        const fallbackTitle = tmdb ? (tmdb.title || tmdb.name) : (cinemeta ? cinemeta.name : imdbId);

        if (tasks.length > 0) {
            await pool.query(`
                INSERT INTO movies_cache (imdb_id, language, title, type, tmdb_data, omdb_data, cinemeta_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (imdb_id, language) DO UPDATE SET
                tmdb_data = EXCLUDED.tmdb_data,
                omdb_data = EXCLUDED.omdb_data,
                cinemeta_data = EXCLUDED.cinemeta_data,
                updated_at = CURRENT_TIMESTAMP
            `, [imdbId, language, fallbackTitle, cachedType, JSON.stringify(tmdb), JSON.stringify(omdb), JSON.stringify(cinemeta)]);
        }

        return { tmdb, omdb, cinemeta, title: fallbackTitle, type: cachedType };
    } catch(e) {
        console.error("Error in fetchAndCacheMetadata:", e);
        return null;
    }
}

async function fetchTMDBMeta(imdbId, type, language) {
    return new Promise((resolve) => {
        if (!imdbId) return resolve(null);
        const apiKey = process.env.TMDB_API_KEY || 'a371649908276cdfd4448c0585638a77';
        const tmdbLang = language === 'pt' ? 'pt-PT' : 'en-US';
        const tmdbType = (type === 'series' || type === 'tv') ? 'tv' : 'movie';
        
        const url = `https://api.themoviedb.org/3/find/${imdbId}?api_key=${apiKey}&external_source=imdb_id&language=${tmdbLang}`;
        
        const req = https.get(url, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    let result = null;
                    if (tmdbType === 'movie' && data.movie_results && data.movie_results.length > 0) {
                        result = data.movie_results[0];
                    } else if (data.tv_results && data.tv_results.length > 0) {
                        result = data.tv_results[0];
                    }
                    
                    if (!result) return resolve(null);

                    // Fetch full details for runtime/genres/translations
                    const detailsUrl = `https://api.themoviedb.org/3/${tmdbType}/${result.id}?api_key=${apiKey}&language=${tmdbLang}&append_to_response=videos,translations,credits`;
                    https.get(detailsUrl, (res2) => {
                        let body2 = '';
                        res2.on('data', c => body2 += c);
                        res2.on('end', () => {
                            try {
                                const details = JSON.parse(body2);
                                let trailerYtId = null;
                                if (details.videos && details.videos.results && details.videos.results.length > 0) {
                                    const trailer = details.videos.results.find(v => v.type === 'Trailer' && v.site === 'YouTube') || details.videos.results[0];
                                    trailerYtId = trailer.key;
                                }
                                let description = details.overview || result.overview;
                                let title = details.title || details.name || result.title || result.name;

                                if ((!description || !title) && details.translations && details.translations.translations) {
                                    const enTrans = details.translations.translations.find(t => t.iso_639_1 === 'en');
                                    if (enTrans && enTrans.data) {
                                        if (!description) description = enTrans.data.overview || '';
                                        if (!title) title = enTrans.data.title || enTrans.data.name || '';
                                    }
                                }

                                resolve({
                                    title: title,
                                    originalTitle: details.original_title || details.original_name || result.original_title || result.original_name,
                                    description: description,
                                    year: (details.release_date || details.first_air_date || result.release_date || result.first_air_date || '').substring(0, 4),
                                    poster: details.poster_path ? `https://image.tmdb.org/t/p/w500${details.poster_path}` : (result.poster_path ? `https://image.tmdb.org/t/p/w500${result.poster_path}` : null),
                                    rating: details.vote_average ? details.vote_average.toFixed(1) : (result.vote_average ? result.vote_average.toFixed(1) : null),
                                    category: details.genres ? details.genres.map(g => g.name).join(', ') : '',
                                    duration: tmdbType === 'movie' ? (details.runtime ? `${details.runtime} min` : '') : (details.number_of_seasons ? `${details.number_of_seasons} Seasons` : ''),
                                    type: tmdbType,
                                    imdb_id: imdbId,
                                    tmdbId: details.id,
                                    trailerYtId: trailerYtId
                                });
                            } catch(e) { resolve(null); }
                        });
                    }).on('error', () => resolve(null));

                } catch(e) {
                    resolve(null);
                }
            });
        });

        req.on('error', () => resolve(null));
        req.setTimeout(5000, () => { req.abort(); resolve(null); });
    });
}

function cleanAndParseJSON(str) {
    if (!str) throw new Error("Empty JSON string");
    let clean = str.replace(/```json/g, '').replace(/```/g, '').trim();
    try {
        return JSON.parse(clean);
    } catch (initialErr) {
        console.warn("Initial JSON parse failed, attempting automatic repair...", initialErr.message);
        try {
            let repaired = "";
            let inString = false;
            let escape = false;
            
            for (let i = 0; i < clean.length; i++) {
                let char = clean[i];
                if (char === '\\' && inString) {
                    escape = !escape;
                    repaired += char;
                } else if (char === '"') {
                    if (!inString) {
                        inString = true;
                        repaired += char;
                    } else if (escape) {
                        escape = false;
                        repaired += char;
                    } else {
                        // Scan ahead to find the next non-whitespace character
                        let nextNonWs = '';
                        for (let j = i + 1; j < clean.length; j++) {
                            if (!/\s/.test(clean[j])) {
                                nextNonWs = clean[j];
                                break;
                            }
                        }
                        
                        if (nextNonWs === ':' || nextNonWs === '}' || nextNonWs === ']' || nextNonWs === ',') {
                            inString = false;
                            repaired += char;
                        } else {
                            repaired += '\\"';
                        }
                    }
                } else {
                    escape = false;
                    repaired += char;
                }
            }
            return JSON.parse(repaired);
        } catch (repairErr) {
            console.error("Automatic JSON repair failed:", repairErr.message);
            throw initialErr;
        }
    }
}

// RECOMMEND ROUTE
app.post('/api/recommend', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized. Please login.' });

    let userPrefs = {};
    try {
        const prefResult = await pool.query('SELECT preferences FROM users WHERE id = $1', [req.session.userId]);
        if (prefResult.rows.length > 0 && prefResult.rows[0].preferences) {
            userPrefs = prefResult.rows[0].preferences;
        }
    } catch(e) {
        console.error("Error fetching user prefs for recommend:", e);
    }

    const movie = req.body.movie;
    const imdbId = req.body.imdbId || '';
    const language = req.body.language || userPrefs.language || 'en';
    const limit = req.body.limit || 5; // Request exact limit (default 5)
    const afterYear = req.body.afterYear || '';
    const minRating = req.body.minRating || userPrefs.minRating || '';
    const excludeTitles = req.body.excludeTitles || [];
    
    let excludeGenresArray = [];
    if (req.body.excludeGenres) excludeGenresArray.push(req.body.excludeGenres);
    if (userPrefs.excludedGenres && Array.isArray(userPrefs.excludedGenres) && userPrefs.excludedGenres.length > 0) {
        excludeGenresArray.push(...userPrefs.excludedGenres);
    }
    const excludeGenres = excludeGenresArray.join(', ');

    let favGenresArray = [];
    if (userPrefs.favoriteGenres && Array.isArray(userPrefs.favoriteGenres) && userPrefs.favoriteGenres.length > 0) {
        favGenresArray.push(...userPrefs.favoriteGenres);
    }
    const favoriteGenres = favGenresArray.join(', ');
    const defaultType = req.body.defaultType || userPrefs.defaultType || 'any';
    const surpriseMe = req.body.surpriseMe || false;
    
    console.log(`Received request for movie: ${movie} (Lang: ${language}, afterYear: ${afterYear}, minRating: ${minRating}, excludeGenres: ${excludeGenres}, defaultType: ${defaultType}, surpriseMe: ${surpriseMe})`);
    if (!movie) return res.status(400).json({ error: 'Movie name required' });

    const normalizedQuery = movie.trim().toLowerCase();
    
    // Construct collision-free composite search query for caching
    let searchQueryWithFilters = imdbId ? `${imdbId}||${normalizedQuery}` : normalizedQuery;
    if (afterYear || minRating || excludeGenres || favoriteGenres || defaultType !== 'any' || surpriseMe || excludeTitles.length > 0) {
        const y = afterYear ? `y:${afterYear}` : '';
        const r = minRating ? `r:${minRating}` : '';
        const e = excludeGenres ? `e:${excludeGenres.toLowerCase().trim()}` : '';
        const f = favoriteGenres ? `f:${favoriteGenres.toLowerCase().trim()}` : '';
        const t = defaultType !== 'any' ? `t:${defaultType}` : '';
        const s = surpriseMe ? 's:true' : '';
        const xt = excludeTitles.length > 0 ? `xt:${excludeTitles.join(',').toLowerCase().trim()}` : '';
        searchQueryWithFilters = `${imdbId ? imdbId + '||' : ''}${normalizedQuery}||${y}||${r}||${e}||${f}||${t}||${s}||${xt}`;
    }

    try {
        // Check cache first (valid for 7 days)
        const cacheResult = await pool.query(
            `SELECT id, reference_movie, recommendations, raw_recommendations FROM recommendation_cache 
             WHERE search_query = $1 AND created_at > NOW() - INTERVAL '7 days'`,
            [searchQueryWithFilters]
        );

        if (cacheResult.rows.length > 0) {
            const rawRecs = cacheResult.rows[0].raw_recommendations || [];
            
            // Re-fetch TMDB data for the requested language based on cached IDs
            console.log(`[CACHE HIT] Found ${rawRecs.length} IDs. Fetching localized TMDB metadata (${language})...`);
            
            const mappedRecs = [];
            for (const r of rawRecs) {
                if (r.imdb_id) {
                    const meta = await fetchAndCacheMetadata(r.imdb_id, r.type || 'movie', language);
                    if (meta && meta.tmdb) {
                        const enriched = meta.tmdb;
                        enriched.omdb = meta.omdb;
                        mappedRecs.push(enriched);
                    } else if (meta && meta.cinemeta) {
                        mappedRecs.push({
                            title: meta.cinemeta.name,
                            originalTitle: meta.cinemeta.name,
                            description: meta.cinemeta.description,
                            year: meta.cinemeta.year || meta.cinemeta.releaseInfo,
                            type: meta.cinemeta.type,
                            imdbId: r.imdb_id,
                            poster: meta.cinemeta.poster,
                            omdb: meta.omdb
                        });
                    }
                }
            }

            // Also map ref if available
            let mappedRef = null;
            if (cacheResult.rows[0].reference_movie && cacheResult.rows[0].reference_movie.imdb_id) {
                const refMeta = await fetchAndCacheMetadata(cacheResult.rows[0].reference_movie.imdb_id, cacheResult.rows[0].reference_movie.type || 'movie', language);
                if (refMeta && refMeta.tmdb) {
                    mappedRef = refMeta.tmdb;
                    mappedRef.omdb = refMeta.omdb;
                } else if (refMeta && refMeta.cinemeta) {
                    mappedRef = {
                        title: refMeta.cinemeta.name,
                        originalTitle: refMeta.cinemeta.name,
                        description: refMeta.cinemeta.description,
                        year: refMeta.cinemeta.year || refMeta.cinemeta.releaseInfo,
                        type: refMeta.cinemeta.type,
                        imdbId: cacheResult.rows[0].reference_movie.imdb_id,
                        poster: refMeta.cinemeta.poster,
                        omdb: refMeta.omdb
                    };
                }
            }

            return res.json({
                cacheId: cacheResult.rows[0].id,
                referenceMovie: mappedRef || cacheResult.rows[0].reference_movie,
                recommendations: mappedRecs,
                hasMore: rawRecs.length > (req.body.limit || 5),
                totalCached: rawRecs.length
            });
        }
        
        console.log(`[CACHE MISS] Fetching from Gemini for: ${searchQueryWithFilters} (Will fetch IDs only)`);

    } catch (e) {
        console.error("Cache check error:", e);
    }

    // Start verification and Gemini fetch concurrently!
    const cinemetaPromise = imdbId 
        ? fetchCinemetaMeta(imdbId, defaultType === 'any' ? (req.body.type || 'series') : defaultType).then(meta => [meta, null])
        : Promise.all([
            fetchCinemetaData(movie, 'movie'),
            fetchCinemetaData(movie, 'series')
        ]);

    let filterConstraints = '';
    if (afterYear) {
        filterConstraints += ` release year must be strictly after ${afterYear} (exclusive, i.e., > ${afterYear});`;
    }
    if (minRating && minRating !== 'all') {
        const numericRating = minRating.replace('>', '');
        filterConstraints += ` minimum IMDB rating must be ${numericRating};`;
    }
    if (excludeGenres) {
        filterConstraints += ` strictly exclude any movies or TV series belonging to the following genres: ${excludeGenres};`;
    }
    if (favoriteGenres) {
        filterConstraints += ` heavily prioritize movies or TV series belonging to the following genres: ${favoriteGenres};`;
    }
    if (excludeTitles && excludeTitles.length > 0) {
        filterConstraints += ` strictly DO NOT recommend any of the following titles (they have already been recommended): ${excludeTitles.join(', ')};`;
    }
    if (defaultType === 'movie') {
        filterConstraints += ` ONLY recommend movies. Do not recommend series/tv shows;`;
    } else if (defaultType === 'series') {
        filterConstraints += ` ONLY recommend series/tv shows. Do not recommend movies;`;
    }
    if (surpriseMe) {
        filterConstraints += `\nCRITICAL RULE: Deliver a mix of highly acclaimed mainstream hits and strictly 2-3 extremely obscure, critically-acclaimed hidden indie gems or cult classics related to the search to surprise the user.`;
    }

    const promptText = `User requested recommendations for the movie/series: "${movie}".
${filterConstraints ? `Additional filter constraints for the recommended items:${filterConstraints}` : ''}
Provide recommendations similar to this movie/series (${limit} recs max). Output ONLY the exact IMDB ID (e.g. 'tt1375666') and type for the reference movie and each recommendation.`;

    const responseSchema = {
        type: "OBJECT",
        properties: {
            ref: {
                type: "OBJECT",
                properties: {
                    imdb_id: { type: "STRING", description: "The exact IMDB ID (starting with 'tt')" },
                    type: { type: "STRING", description: "Either 'movie' or 'series'" }
                },
                required: ["imdb_id", "type"]
            },
            recs: {
                type: "ARRAY",
                description: `${limit} recommendations max`,
                items: {
                    type: "OBJECT",
                    properties: {
                        imdb_id: { type: "STRING", description: "The exact IMDB ID (starting with 'tt')" },
                        type: { type: "STRING", description: "Either 'movie' or 'series'" }
                    },
                    required: ["imdb_id", "type"]
                }
            }
        },
        required: ["ref", "recs"]
    };

    const postData = JSON.stringify({
        systemInstruction: {
            parts: [{ text: "You are a highly sophisticated movie recommendation engine. Analyze the user's reference title based on emotional tone, aesthetic style, thematic subtext, and pacing. Ensure all provided 'imdb_id' fields are absolutely correct by searching your knowledge base. Output ONLY IMDB IDs and types. Do not hallucinate IDs." }]
        },
        contents: [{ parts: [{ text: promptText }] }],
        generationConfig: { 
            temperature: surpriseMe ? 0.8 : 0.4,
            responseMimeType: "application/json",
            responseSchema: responseSchema
        }
    });

    const geminiPromise = new Promise((resolveGemini, rejectGemini) => {
        const options = {
            hostname: 'generativelanguage.googleapis.com',
            port: 443,
            path: `/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const apiReq = https.request(options, (apiRes) => {
            let body = '';
            apiRes.on('data', (chunk) => body += chunk);
            apiRes.on('end', () => resolveGemini(body));
        });

        apiReq.on('error', (e) => rejectGemini(e));
        apiReq.write(postData);
        apiReq.end();
    });

    try {
        const [[movieVerify, seriesVerify], body] = await Promise.all([cinemetaPromise, geminiPromise]);

        let verifiedData = null;
        if (imdbId) {
            verifiedData = movieVerify; // Since we resolved [meta, null], movieVerify contains the exact meta
        } else {
            const queryLower = movie.trim().toLowerCase();
            const isMovieExact = movieVerify && movieVerify.name && movieVerify.name.trim().toLowerCase() === queryLower;
            const isSeriesExact = seriesVerify && seriesVerify.name && seriesVerify.name.trim().toLowerCase() === queryLower;

            if (isSeriesExact && !isMovieExact) {
                verifiedData = seriesVerify;
            } else if (isMovieExact && !isSeriesExact) {
                verifiedData = movieVerify;
            } else {
                if (defaultType === 'series') {
                    verifiedData = seriesVerify || movieVerify;
                } else if (defaultType === 'movie') {
                    verifiedData = movieVerify || seriesVerify;
                } else {
                    verifiedData = movieVerify || seriesVerify;
                }
            }
        }

        if (!verifiedData) {
            console.log(`[IMDB VERIFY FAILED] "${movie}" not found on IMDB via Cinemeta.`);
            return res.json({ error: 'Not a valid movie or TV series.' });
        }

        const verifiedYear = verifiedData.releaseInfo || '';
        const verifiedType = verifiedData.type || 'movie';
        const verifiedImdbId = verifiedData.imdb_id || verifiedData.id || '';
            try {
                let reply = '';
                const data = JSON.parse(body);
                
                if (data.error || !data.candidates || data.candidates.length === 0 || !data.candidates[0].content || !data.candidates[0].content.parts || data.candidates[0].content.parts.length === 0) {
                    console.warn('[GEMINI FAILED] Falling back to Groq...', data.error ? data.error.message : 'Invalid response');
                    try {
                        reply = await fetchFromGroq(promptText, limit, surpriseMe);
                    } catch (groqErr) {
                        console.error('[GROQ FALLBACK ERROR]', groqErr.message);
                        return res.status(500).json({ error: 'Both AI APIs failed.' });
                    }
                } else {
                    reply = data.candidates[0].content.parts[0].text;
                }
                
                reply = reply.trim();
                if (reply === 'ERROR' || reply.startsWith('ERROR')) return res.json({ error: 'Not a valid movie or TV series.' });

                let parsed;
                try {
                    parsed = cleanAndParseJSON(reply);
                } catch(e) {
                    console.error("Gemini output was not valid JSON and could not be repaired:", reply);
                    return res.status(500).json({ error: 'Failed to parse recommendations' });
                }

                if (parsed.error) {
                    return res.json({ error: parsed.error });
                }

                if (Array.isArray(parsed)) {
                    // Fallback repair
                    parsed = { ref: { imdb_id: verifiedImdbId, type: verifiedType }, recs: parsed };
                }

                // Make sure ref has an imdb_id
                if (!parsed.ref) parsed.ref = { imdb_id: verifiedImdbId, type: verifiedType };
                if (!parsed.ref.imdb_id) parsed.ref.imdb_id = verifiedImdbId;

                const rawRecs = parsed.recs || [];
                const updatedRecommendations = [];

                for (const r of rawRecs) {
                    if (r.imdb_id || r.imdbId) {
                        const idToUse = r.imdb_id || r.imdbId;
                        const meta = await fetchAndCacheMetadata(idToUse, r.type || 'movie', language);
                        if (meta && meta.tmdb) {
                            const enriched = meta.tmdb;
                            enriched.omdb = meta.omdb;
                            updatedRecommendations.push(enriched);
                        } else if (meta && meta.cinemeta) {
                            updatedRecommendations.push({
                                title: meta.cinemeta.name,
                                originalTitle: meta.cinemeta.name,
                                description: meta.cinemeta.description,
                                year: meta.cinemeta.year || meta.cinemeta.releaseInfo,
                                type: meta.cinemeta.type,
                                imdbId: idToUse,
                                poster: meta.cinemeta.poster,
                                omdb: meta.omdb
                            });
                        } else {
                            // Fallback if TMDB fails
                            const cmMeta = await fetchCinemetaMeta(idToUse, r.type || 'movie');
                            if (cmMeta) {
                                updatedRecommendations.push({
                                    title: cmMeta.name,
                                    originalTitle: cmMeta.name,
                                    description: cmMeta.description,
                                    year: cmMeta.year || cmMeta.releaseInfo,
                                    poster: cmMeta.poster,
                                    rating: cmMeta.imdbRating,
                                    category: cmMeta.genre ? cmMeta.genre.join(', ') : '',
                                    duration: cmMeta.runtime,
                                    type: cmMeta.type || 'movie',
                                    imdb_id: idToUse
                                });
                            }
                        }
                    }
                }

                let finalRef = null;
                if (parsed.ref.imdb_id) {
                    const finalRefMeta = await fetchAndCacheMetadata(parsed.ref.imdb_id, parsed.ref.type || 'movie', language);
                    if (finalRefMeta && finalRefMeta.tmdb) {
                        finalRef = finalRefMeta.tmdb;
                        finalRef.omdb = finalRefMeta.omdb;
                    }
                }

                const finalParsed = {
                    referenceMovie: finalRef || { imdb_id: verifiedImdbId, type: verifiedType, title: movie },
                    recommendations: updatedRecommendations
                };
                
                let cacheId = null;
                // Save to cache only if we found valid recommendations
                if (updatedRecommendations.length > 0) {
                    try {
                        const insertResult = await pool.query(
                            `INSERT INTO recommendation_cache (search_query, language, reference_movie, recommendations, raw_recommendations) 
                             VALUES ($1, $2, $3, $4, $5)
                             ON CONFLICT (search_query, language) 
                             DO UPDATE SET reference_movie = $3, recommendations = $4, raw_recommendations = $5, created_at = NOW()
                             RETURNING id`,
                            [searchQueryWithFilters, 'all', JSON.stringify(parsed.ref), JSON.stringify(finalParsed.recommendations), JSON.stringify(rawRecs)]
                        );
                        if (insertResult.rows.length > 0) {
                            cacheId = insertResult.rows[0].id;
                        }
                    } catch(cacheErr) {
                        console.error("Failed to save to cache:", cacheErr);
                    }
                } else {
                    // Delete from cache if empty so the user can try again and trigger the AI/fallback anew
                    try {
                        await pool.query('DELETE FROM recommendation_cache WHERE search_query = $1 AND language = $2', [searchQueryWithFilters, 'all']);
                    } catch(delErr){}
                }

                res.json({ 
                    cacheId,
                    referenceMovie: finalParsed.referenceMovie, 
                    recommendations: updatedRecommendations,
                    hasMore: finalParsed.recommendations.length >= limit,
                    totalCached: finalParsed.recommendations.length
                });
                
            } catch (e) {
                console.error("Parse error:", e);
                res.status(500).json({ error: 'Failed to parse recommendations' });
            }
    } catch (e) {
        console.error("Gemini API or Cinemeta verification failed:", e);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.post('/api/recommend/more', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    const { cacheId, offset, language = 'en' } = req.body;
    if (!cacheId || offset === undefined) return res.status(400).json({ error: 'Missing cacheId or offset' });

    try {
        const cacheResult = await pool.query(
            `SELECT raw_recommendations, recommendations FROM recommendation_cache WHERE id = $1`,
            [cacheId]
        );
        if (cacheResult.rows.length === 0) return res.status(404).json({ error: 'Cache not found' });
        
        const rawRecs = cacheResult.rows[0].raw_recommendations || [];
        let processedRecs = cacheResult.rows[0].recommendations || [];
        
        if (offset >= rawRecs.length) {
            return res.json({ recommendations: [], hasMore: false });
        }
        
        const recsToProcess = rawRecs.slice(offset, offset + 5);
        const updatedRecommendations = [];

        for (const r of recsToProcess) {
            if (r.imdb_id || r.imdbId) {
                const idToUse = r.imdb_id || r.imdbId;
                const meta = await fetchAndCacheMetadata(idToUse, r.type || 'movie', language);
                        if (meta && meta.tmdb) {
                            const enriched = meta.tmdb;
                            enriched.omdb = meta.omdb;
                            updatedRecommendations.push(enriched);
                        } else if (meta && meta.cinemeta) {
                            updatedRecommendations.push({
                                title: meta.cinemeta.name,
                                originalTitle: meta.cinemeta.name,
                                description: meta.cinemeta.description,
                                year: meta.cinemeta.year || meta.cinemeta.releaseInfo,
                                type: meta.cinemeta.type,
                                imdbId: idToUse,
                                poster: meta.cinemeta.poster,
                                omdb: meta.omdb
                            });
                        } else {
                    const cmMeta = await fetchCinemetaMeta(idToUse, r.type || 'movie');
                    if (cmMeta) {
                        updatedRecommendations.push({
                            title: cmMeta.name,
                            originalTitle: cmMeta.name,
                            description: cmMeta.description,
                            year: cmMeta.year || cmMeta.releaseInfo,
                            poster: cmMeta.poster,
                            rating: cmMeta.imdbRating,
                            category: cmMeta.genre ? cmMeta.genre.join(', ') : '',
                            duration: cmMeta.runtime,
                            type: cmMeta.type || 'movie',
                            imdb_id: idToUse
                        });
                    }
                }
            }
        }

        // Append to processed recs and update DB
        processedRecs = [...processedRecs, ...updatedRecommendations];
        await pool.query('UPDATE recommendation_cache SET recommendations = $1 WHERE id = $2', [JSON.stringify(processedRecs), cacheId]);

        res.json({
            recommendations: updatedRecommendations,
            hasMore: offset + 5 < rawRecs.length,
            totalCached: rawRecs.length
        });
    } catch (e) {
        console.error("Error in load more:", e);
        res.status(500).json({ error: 'Server error' });
    }
});

// WATCHLIST ENDPOINTS
app.post('/api/watchlist/add', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    const { imdb_id, title, original_title, year, type, rating, duration, category, description, trailer_yt_id, poster } = req.body;
    if (!title) return res.status(400).json({ error: 'Title is required' });
    
    try {
        const result = await pool.query(
            `INSERT INTO user_watchlist (user_id, imdb_id, title, original_title, year, type, rating, duration, category, description, trailer_yt_id, poster)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
             ON CONFLICT (user_id, title, year) DO NOTHING
             RETURNING id`,
            [req.session.userId, imdb_id, title, original_title, year, type || 'movie', rating, duration, category, description, trailer_yt_id || null, poster || null]
        );
        res.json({ success: true, added: result.rows.length > 0 });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to add item to watchlist' });
    }
});

app.post('/api/watchlist/remove', async (req, res) => {
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    const { title, year } = req.body;
    if (!title) return res.status(400).json({ error: 'Title is required' });
    
    try {
        await pool.query(
            `DELETE FROM user_watchlist WHERE user_id = $1 AND title = $2 AND year = $3`,
            [req.session.userId, title, year]
        );
        res.json({ success: true });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to remove item from watchlist' });
    }
});

app.get('/api/watchlist', async (req, res) => {
    console.log('[WATCHLIST API] Request received. Session userId:', req.session.userId, '| Cookies:', req.headers.cookie);
    if (!req.session.userId) return res.status(401).json({ error: 'Unauthorized' });
    
    try {
        const result = await pool.query(
            `SELECT * FROM user_watchlist WHERE user_id = $1 ORDER BY created_at DESC`,
            [req.session.userId]
        );
        console.log('[WATCHLIST API] Returning rows:', result.rows.length);
        res.json({ success: true, watchlist: result.rows });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch watchlist' });
    }
});

// NEW MASTER ENDPOINT (DB CACHE -> TMDB+OMDB -> CINEMETA)
app.get('/api/details/:type/:id', async (req, res) => {
    try {
        const type = req.params.type;
        const id = req.params.id; // IMDb ID
        const lang = req.query.lang || 'en';

        const meta = await fetchAndCacheMetadata(id, type, lang);
        if (!meta || (!meta.tmdb && !meta.cinemeta)) {
            return res.status(404).json({ error: 'Movie metadata not found' });
        }
        return res.json({ success: true, source: 'cache_or_api', tmdb: meta.tmdb, omdb: meta.omdb, cinemeta: meta.cinemeta });
    } catch (e) {
        console.error("Details API Error:", e);
        res.status(500).json({ error: 'Server error' });
    }
});

// SAME-ORIGIN CINEMETA PROXY ENDPOINTS
app.get('/api/proxy/catalog/:type/:query', async (req, res) => {
    try {
        const type = req.params.type;
        const query = req.params.query;
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const url = `https://v3-cinemeta.strem.io/catalog/${cleanType}/top/${query}.json`;
        
        https.get(url, (apiRes) => {
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Cache-Control', 'public, max-age=86400');
            apiRes.pipe(res);
        }).on('error', (err) => {
            res.status(500).json({ error: 'Proxy fetch failed' });
        });
    } catch(e) {
        res.status(500).json({ error: 'Proxy error' });
    }
});

app.get('/api/proxy/meta/:type/:id', async (req, res) => {
    try {
        const type = req.params.type;
        const id = req.params.id;
        const cleanType = (type === 'series' || type === 'tv') ? 'series' : 'movie';
        const url = `https://v3-cinemeta.strem.io/meta/${cleanType}/${id}.json`;
        
        https.get(url, (apiRes) => {
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Cache-Control', 'public, max-age=86400');
            apiRes.pipe(res);
        }).on('error', (err) => {
            res.status(500).json({ error: 'Proxy fetch failed' });
        });
    } catch(e) {
        res.status(500).json({ error: 'Proxy error' });
    }
});

// PUBLIC SHARE RETRIEVAL ENDPOINT
app.get('/api/share/:id', async (req, res) => {
    try {
        const id = parseInt(req.params.id, 10);
        if (isNaN(id)) return res.status(400).json({ error: 'Invalid share ID' });
        
        const result = await pool.query(
            `SELECT id, reference_movie, recommendations FROM recommendation_cache WHERE id = $1`,
            [id]
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Watchlist not found' });
        }
        
        res.json({
            success: true,
            shareId: result.rows[0].id,
            referenceMovie: result.rows[0].reference_movie,
            recommendations: result.rows[0].recommendations
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error retrieving shared watchlist' });
    }
});

let trendingCache = null;
let trendingCacheTime = 0;
const TRENDING_CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

app.get('/api/trending', async (req, res) => {
    const now = Date.now();
    if (trendingCache && (now - trendingCacheTime < TRENDING_CACHE_DURATION)) {
        return res.json({ success: true, trending: trendingCache });
    }

    try {
        const fetchTop = (type) => {
            return new Promise((resolve) => {
                const url = `https://cinemeta-catalogs.strem.io/top/catalog/${type}/top.json`;
                const reqHttps = https.get(url, (resHttps) => {
                    let body = '';
                    resHttps.on('data', chunk => body += chunk);
                    resHttps.on('end', () => {
                        try {
                            const data = JSON.parse(body);
                            if (data && data.metas && Array.isArray(data.metas)) {
                                resolve(data.metas.slice(0, 10).map(m => ({
                                    name: m.name,
                                    year: m.releaseInfo || m.year || '',
                                    type: m.type || type,
                                    imdbId: m.id || m.imdb_id || ''
                                })));
                            } else {
                                resolve([]);
                            }
                        } catch (e) {
                            resolve([]);
                        }
                    });
                });
                reqHttps.on('error', () => resolve([]));
                reqHttps.setTimeout(2500, () => {
                    reqHttps.abort();
                    resolve([]);
                });
            });
        };

        const [movies, series] = await Promise.all([fetchTop('movie'), fetchTop('series')]);
        
        let merged = [];
        const maxLen = Math.max(movies.length, series.length);
        for (let i = 0; i < maxLen; i++) {
            if (movies[i]) merged.push(movies[i]);
            if (series[i]) merged.push(series[i]);
        }
        
        // Deduplicate objects by imdbId
        const seenIds = new Set();
        const uniqueMerged = [];
        for (const item of merged) {
            if (item && item.imdbId && !seenIds.has(item.imdbId)) {
                seenIds.add(item.imdbId);
                uniqueMerged.push(item);
            }
        }
        
        let finalTrending = uniqueMerged.slice(0, 8);
        
        let isSuccess = true;
        if (finalTrending.length === 0) {
            finalTrending = [
                { name: "Inception", year: "2010", type: "movie", imdbId: "tt1375666" },
                { name: "Breaking Bad", year: "2008-2013", type: "series", imdbId: "tt0903747" },
                { name: "Interstellar", year: "2014", type: "movie", imdbId: "tt0816692" },
                { name: "Game of Thrones", year: "2011-2019", type: "series", imdbId: "tt0944947" },
                { name: "The Matrix", year: "1999", type: "movie", imdbId: "tt0133093" },
                { name: "Stranger Things", year: "2016-", type: "series", imdbId: "tt5027774" }
            ];
            isSuccess = false; // Do not cache long if we got an empty result
        }
        
        if (isSuccess) {
            trendingCache = finalTrending;
            trendingCacheTime = now;
        }
        
        res.json({ success: true, trending: finalTrending });
    } catch (err) {
        console.error("Error in trending API:", err);
        res.json({ 
            success: true, 
            trending: ["Inception", "Breaking Bad", "Interstellar", "Game of Thrones", "The Matrix", "Stranger Things"] 
            // Do not cache on error to retry sooner
        });
    }
});

const PORT = process.env.PORT || 80;

// --- PRE-WARMING SCRIPT ---
async function prewarmTrendingCache() {
    console.log("[PRE-WARMING] Starting background cache population...");
    try {
        const res = await new Promise(resolve => {
            https.get('https://cinemeta-catalogs.strem.io/top/catalog/movie/top.json', (r) => {
                let body = '';
                r.on('data', chunk => body += chunk);
                r.on('end', () => resolve(JSON.parse(body)));
            }).on('error', () => resolve(null));
        });
        
        if (res && res.metas && res.metas.length > 0) {
            // Get top 10 movies
            const topMovies = res.metas.slice(0, 10);
            for (let m of topMovies) {
                const id = m.imdb_id || m.id;
                if (!id) continue;
                
                // Check if already in DB
                const check = await pool.query('SELECT 1 FROM movies_cache WHERE imdb_id = $1 AND language = $2', [id, 'en']);
                if (check.rows.length === 0) {
                    console.log(`[PRE-WARMING] Fetching missing data for: ${m.name} (${id})`);
                    const [tmdbMeta, omdbMeta] = await Promise.all([
                        fetchTMDBMeta(id, 'movie', 'en'),
                        fetchOMDB(id)
                    ]);
                    
                    let cinemeta = null;
                    if (!tmdbMeta) {
                        cinemeta = await fetchCinemetaMeta(id, 'movie');
                    }
                    
                    const fallbackTitle = tmdbMeta ? (tmdbMeta.title || tmdbMeta.name) : m.name;
                    await pool.query(`
                        INSERT INTO movies_cache (imdb_id, language, title, type, tmdb_data, omdb_data, cinemeta_data)
                        VALUES ($1, 'en', $2, 'movie', $3, $4, $5)
                        ON CONFLICT DO NOTHING
                    `, [id, fallbackTitle, JSON.stringify(tmdbMeta), JSON.stringify(omdbMeta), JSON.stringify(cinemeta)]);
                }
            }
            console.log("[PRE-WARMING] Completed.");
        }
    } catch(e) {
        console.error("[PRE-WARMING] Error:", e.message);
    }
}

// Call prewarm on startup
prewarmTrendingCache();

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});





