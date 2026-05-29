import io

index_path = r"public/index.html"

with io.open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update English translations dictionary
target_en_trans = '''                tooltipSurpriseMe: "Mixes in 2-3 highly-rated, critically acclaimed hidden indie gems or cult classics related to your search that still boast outstanding reviews.",'''
replacement_en_trans = '''                tooltipSurpriseMe: "Mixes in 2-3 highly-rated, critically acclaimed hidden indie gems or cult classics related to your search that still boast outstanding reviews.",
                lblRememberMe: "Remember Me",'''

if target_en_trans in content:
    content = content.replace(target_en_trans, replacement_en_trans)
    print("Success: English translation added.")
else:
    print("Warning: English translation target not matched.")

# 2. Update Portuguese translations dictionary
target_pt_trans = '''                tooltipSurpriseMe: "Mistura 2 a 3 raridades obscuras, clássicos de culto ou pérolas independentes aclamadas pela crítica com avaliações excelentes.",'''
replacement_pt_trans = '''                tooltipSurpriseMe: "Mistura 2 a 3 raridades obscuras, clássicos de culto ou pérolas independentes aclamadas pela crítica com avaliações excelentes.",
                lblRememberMe: "Lembrar-me",'''

if target_pt_trans in content:
    content = content.replace(target_pt_trans, replacement_pt_trans)
    print("Success: Portuguese translation added.")
else:
    print("Warning: Portuguese translation target not matched.")

# 3. Update updateUI() call
target_ui_block = '''            const tooltipSurpriseMe = document.getElementById('tooltip-surprise-me');
            if (tooltipSurpriseMe) tooltipSurpriseMe.textContent = t.tooltipSurpriseMe;'''
replacement_ui_block = '''            const tooltipSurpriseMe = document.getElementById('tooltip-surprise-me');
            if (tooltipSurpriseMe) tooltipSurpriseMe.textContent = t.tooltipSurpriseMe;
            const lblRememberMe = document.getElementById('lbl-remember-me');
            if (lblRememberMe) lblRememberMe.textContent = t.lblRememberMe;'''

if target_ui_block in content:
    content = content.replace(target_ui_block, replacement_ui_block)
    print("Success: updateUI elements added.")
else:
    print("Warning: updateUI target not matched.")

# 4. Modify login form to add name attributes and Remember Me checkbox
target_login_form = '''            <form id="login-form" class="flex flex-col gap-3">
                <input type="text" id="login-user" placeholder="Username" required autocomplete="username" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <input type="password" id="login-pass" placeholder="Password" required autocomplete="current-password" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <button type="submit" class="mt-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg px-4 py-2.5 text-sm transition-all shadow-md w-full">
                    <span id="login-btn-text">Login</span>
                </button>
            </form>'''

replacement_login_form = '''            <form id="login-form" class="flex flex-col gap-3">
                <input type="text" id="login-user" name="username" placeholder="Username" required autocomplete="username" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <input type="password" id="login-pass" name="password" placeholder="Password" required autocomplete="current-password" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <div class="flex items-center justify-between mt-1 mb-2 px-1">
                    <label class="flex items-center gap-2 cursor-pointer select-none">
                        <input type="checkbox" id="login-remember" class="w-3.5 h-3.5 rounded border-slate-700 bg-slate-900 text-sky-500 focus:ring-0 focus:ring-offset-0 focus:outline-none">
                        <span id="lbl-remember-me" class="text-[11px] font-medium text-slate-400">Remember Me</span>
                    </label>
                </div>
                <button type="submit" class="mt-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg px-4 py-2.5 text-sm transition-all shadow-md w-full">
                    <span id="login-btn-text">Login</span>
                </button>
            </form>'''

if target_login_form in content:
    content = content.replace(target_login_form, replacement_login_form)
    print("Success: Login form HTML modified.")
else:
    print("Warning: Login form HTML target not matched.")

# 5. Modify register form to add name attributes
target_register_form = '''            <form id="register-form" class="flex flex-col gap-3 hidden">
                <input type="text" id="register-user" placeholder="Username" required autocomplete="username" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <input type="password" id="register-pass" placeholder="Password" required autocomplete="new-password" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <button type="submit" class="mt-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg px-4 py-2.5 text-sm transition-all shadow-md w-full">
                    <span id="register-btn-text">Register</span>
                </button>
            </form>'''

replacement_register_form = '''            <form id="register-form" class="flex flex-col gap-3 hidden">
                <input type="text" id="register-user" name="username" placeholder="Username" required autocomplete="username" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <input type="password" id="register-pass" name="password" placeholder="Password" required autocomplete="new-password" class="bg-slate-900 border border-slate-700/60 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500 text-white w-full">
                <button type="submit" class="mt-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg px-4 py-2.5 text-sm transition-all shadow-md w-full">
                    <span id="register-btn-text">Register</span>
                </button>
            </form>'''

if target_register_form in content:
    content = content.replace(target_register_form, replacement_register_form)
    print("Success: Register form HTML modified.")
else:
    print("Warning: Register form HTML target not matched.")

# 6. Inject pre-fill username check on DOMContentLoaded
target_domcontentloaded = '''        document.addEventListener('DOMContentLoaded', () => {
            loadSettings();
            updateUI();
            loadTrending();
            registerSettingsListeners();
        });'''

replacement_domcontentloaded = '''        document.addEventListener('DOMContentLoaded', () => {
            loadSettings();
            updateUI();
            loadTrending();
            registerSettingsListeners();
            // Pre-fill username if remembered
            const savedUsername = localStorage.getItem('remembered_username');
            if (savedUsername) {
                const loginUser = document.getElementById('login-user');
                const loginRemember = document.getElementById('login-remember');
                if (loginUser) loginUser.value = savedUsername;
                if (loginRemember) loginRemember.checked = true;
            }
        });'''

if target_domcontentloaded in content:
    content = content.replace(target_domcontentloaded, replacement_domcontentloaded)
    print("Success: Pre-fill logic injected into DOMContentLoaded listener.")
else:
    print("Warning: DOMContentLoaded listener target not matched.")

# 7. Modify handleAuthSubmit to save/remove username from localStorage and trigger PasswordCredential storage
target_handleauth = '''                if (res.ok && data.success) {
                    if (isLogin) loginForm.reset(); else registerForm.reset();
                    authModal.classList.remove('active');'''

replacement_handleauth = '''                if (res.ok && data.success) {
                    // Save or remove remembered username
                    if (isLogin) {
                        const loginRemember = document.getElementById('login-remember');
                        if (loginRemember && loginRemember.checked) {
                            localStorage.setItem('remembered_username', username);
                        } else {
                            localStorage.removeItem('remembered_username');
                        }

                        // Trigger native browser save password prompt
                        if (window.PasswordCredential) {
                            try {
                                const cred = new PasswordCredential({
                                    id: username,
                                    password: password
                                });
                                navigator.credentials.store(cred).catch(err => console.error("Error storing credentials", err));
                            } catch (e) {
                                console.error("Error building PasswordCredential", e);
                            }
                        }
                    }

                    if (isLogin) loginForm.reset(); else registerForm.reset();
                    authModal.classList.remove('active');'''

if target_handleauth in content:
    content = content.replace(target_handleauth, replacement_handleauth)
    print("Success: handleAuthSubmit logic modified to persist username and store native credentials.")
else:
    print("Warning: handleAuthSubmit target not matched.")

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Credentials patch finished.")
