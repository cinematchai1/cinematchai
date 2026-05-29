import io

index_path = r"public/index.html"

with io.open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add action and method to login form
target_login = '<form id="login-form" class="flex flex-col gap-3">'
replacement_login = '<form id="login-form" action="/api/login" method="POST" class="flex flex-col gap-3">'

if target_login in content:
    content = content.replace(target_login, replacement_login)
    print("Success: Added action/method to login form.")
else:
    print("Warning: Login form HTML target not matched.")

# 2. Add action and method to register form
target_register = '<form id="register-form" class="flex flex-col gap-3 hidden">'
replacement_register = '<form id="register-form" action="/api/register" method="POST" class="flex flex-col gap-3 hidden">'

if target_register in content:
    content = content.replace(target_register, replacement_register)
    print("Success: Added action/method to register form.")
else:
    print("Warning: Register form HTML target not matched.")

# 3. Add a small delay to form reset inside handleAuthSubmit
target_reset = '''                    if (isLogin) loginForm.reset(); else registerForm.reset();
                    authModal.classList.remove('active');'''

replacement_reset = '''                    authModal.classList.remove('active');
                    // Delay reset slightly to let browser credentials heuristics capture the input values before clearing
                    setTimeout(() => {
                        if (isLogin) loginForm.reset(); else registerForm.reset();
                    }, 1000);'''

if target_reset in content:
    content = content.replace(target_reset, replacement_reset)
    print("Success: Delayed reset added.")
else:
    print("Warning: Reset target not matched.")

with io.open(index_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished form optimizations.")
