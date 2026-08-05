const SUPABASE_URL = window.SUPABASE_URL || "https://lkgjenlbmfimjnjvhawm.supabase.co";
const SUPABASE_ANON_KEY = window.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxrZ2plbmxibWZpbWpuanZoYXdtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU4NDM1OTQsImV4cCI6MjEwMTQxOTU5NH0.GZqs1pgU37fJnuBbH8Sh1eu4Bp_sAlHqu9zeLcibamo";

let supabaseClient = null;
if (window.supabase && typeof window.supabase.createClient === 'function') {
  try {
    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  } catch (e) {
    console.warn("Supabase init notice:", e);
  }
}

let currentMode = "signin";

document.addEventListener("DOMContentLoaded", () => {
  checkExistingSession();
});

// Deterministic User ID Generator per Email Address
function getUserId(email) {
  const norm = (email || "").trim().toLowerCase();
  try {
    return "usr_" + btoa(norm).replace(/=/g, "").replace(/[^a-zA-Z0-9]/g, "");
  } catch (e) {
    return "usr_" + norm.replace(/[^a-zA-Z0-9]/g, "");
  }
}

async function checkExistingSession() {
  const localUser = localStorage.getItem("drx_user");
  if (localUser) {
    try {
      const parsed = JSON.parse(localUser);
      if (parsed && parsed.email) {
        window.location.href = "/dashboard";
        return;
      }
    } catch (e) {
      localStorage.removeItem("drx_user");
    }
  }

  if (supabaseClient) {
    try {
      const { data: { session } } = await supabaseClient.auth.getSession();
      if (session && session.user) {
        const uEmail = session.user.email;
        localStorage.setItem("drx_user", JSON.stringify({
          id: getUserId(uEmail),
          email: uEmail,
          name: session.user.user_metadata?.full_name || uEmail.split('@')[0]
        }));
        window.location.href = "/dashboard";
      }
    } catch (e) {
      console.log("No active Supabase session found:", e);
    }
  }
}

function switchAuthTab(mode) {
  currentMode = mode;
  const tabSignin = document.getElementById("tabSignin");
  const tabSignup = document.getElementById("tabSignup");
  const groupName = document.getElementById("groupName");
  const authTitle = document.getElementById("authTitle");
  const authSubtitle = document.getElementById("authSubtitle");
  const btnText = document.getElementById("btnText");
  const authAlert = document.getElementById("authAlert");

  authAlert.classList.add("hidden");

  if (mode === "signin") {
    tabSignin.classList.add("active");
    tabSignup.classList.remove("active");
    groupName.style.display = "none";
    authTitle.textContent = "Welcome Back";
    authSubtitle.textContent = "Access your AI Orthopaedic Diagnostic Workspace";
    btnText.textContent = "Sign In to Dashboard";
  } else {
    tabSignup.classList.add("active");
    tabSignin.classList.remove("active");
    groupName.style.display = "block";
    authTitle.textContent = "Create an Account";
    authSubtitle.textContent = "Start analyzing X-rays & generating AI recovery plans";
    btnText.textContent = "Create Account";
  }
}

function togglePasswordVisibility() {
  const pwd = document.getElementById("password");
  const icon = document.getElementById("passwordIcon");
  if (pwd.type === "password") {
    pwd.type = "text";
    icon.className = "fa-regular fa-eye-slash";
  } else {
    pwd.type = "password";
    icon.className = "fa-regular fa-eye";
  }
}

function showAlert(msg, isError = true) {
  const alert = document.getElementById("authAlert");
  alert.className = `auth-alert ${isError ? "error" : "success"}`;
  alert.innerHTML = `<i class="fa-solid ${isError ? 'fa-circle-exclamation' : 'fa-circle-check'}"></i> ${msg}`;
  alert.classList.remove("hidden");
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("email").value.trim().toLowerCase();
  const password = document.getElementById("password").value;
  const fullName = document.getElementById("fullName").value.trim();

  const btnSpinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");

  btnSpinner.classList.remove("hidden");
  btnText.style.opacity = "0.5";

  try {
    const endpoint = currentMode === "signup" ? "/api/auth/register" : "/api/auth/login";
    const payload = {
      email: email,
      password: password,
      name: fullName
    };

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const resData = await response.json().catch(() => ({ status: "error", message: "Server response error." }));

    if (!response.ok || resData.status !== "success") {
      throw new Error(resData.message || (currentMode === "signup" ? "Failed to create account." : "Invalid email or password."));
    }

    // Sync with Supabase if client is initialized
    if (supabaseClient && SUPABASE_URL.indexOf("demo-project") === -1) {
      if (currentMode === "signup") {
        await supabaseClient.auth.signUp({
          email,
          password,
          options: { data: { full_name: fullName } }
        }).catch(err => console.log("Supabase signup sync notice:", err));
      } else {
        await supabaseClient.auth.signInWithPassword({ email, password })
          .catch(err => console.log("Supabase signin sync notice:", err));
      }
    }

    const authUser = resData.user || {
      id: getUserId(email),
      email: email,
      name: fullName || email.split('@')[0] || "Doctor"
    };

    showAlert(
      currentMode === "signup"
        ? "Account created successfully! Redirecting to dashboard..."
        : "Successfully authenticated! Redirecting to dashboard...",
      false
    );

    localStorage.setItem("drx_user", JSON.stringify(authUser));

    setTimeout(() => {
      window.location.href = "/dashboard";
    }, 700);

  } catch (err) {
    console.error("Auth error:", err);
    showAlert(err.message || "Authentication failed. Please check your credentials.");
  } finally {
    btnSpinner.classList.add("hidden");
    btnText.style.opacity = "1";
  }
}
