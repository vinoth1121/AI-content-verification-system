/**
 * Popup script — sign-in form + quick scan + recent verdict display.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const { user, access_token } = await chrome.storage.local.get(["user", "access_token"]);
  if (user && access_token) {
    showSignedIn(user);
  } else {
    showSignIn();
  }
});

function showSignIn(): void {
  const root = document.getElementById("app")!;
  root.innerHTML = `
    <h1>Sign in to ACVS</h1>
    <form id="login-form">
      <label>Email<input type="email" id="email" required></label>
      <label>Password<input type="password" id="password" required></label>
      <button type="submit">Sign in</button>
    </form>
    <p id="err" class="err"></p>
  `;
  document.getElementById("login-form")!.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (document.getElementById("email") as HTMLInputElement).value;
    const password = (document.getElementById("password") as HTMLInputElement).value;
    const res = await chrome.runtime.sendMessage({ type: "login", email, password });
    if (res.error) {
      document.getElementById("err")!.textContent = res.error;
    } else {
      showSignedIn(res.user);
    }
  });
}

function showSignedIn(user: any): void {
  const root = document.getElementById("app")!;
  root.innerHTML = `
    <header>
      <h1>ACVS</h1>
      <p>Signed in as <strong>${user.full_name}</strong></p>
    </header>
    <section>
      <h2>Quick text scan</h2>
      <textarea id="text" rows="5" placeholder="Paste text to verify…"></textarea>
      <button id="scan">Detect AI-generated text</button>
    </section>
    <div id="result"></div>
    <footer>
      <button id="logout">Sign out</button>
    </footer>
  `;
  document.getElementById("scan")!.addEventListener("click", async () => {
    const text = (document.getElementById("text") as HTMLTextAreaElement).value;
    if (!text.trim()) return;
    const res = await chrome.runtime.sendMessage({ type: "scan-text", text });
    renderResult(res.error ? { error: res.error } : res);
  });
  document.getElementById("logout")!.addEventListener("click", async () => {
    await chrome.storage.local.remove(["access_token", "refresh_token", "user"]);
    showSignIn();
  });
}

function renderResult(result: any): void {
  const el = document.getElementById("result")!;
  if (result.error) {
    el.innerHTML = `<p class="err">${result.error}</p>`;
    return;
  }
  const tone =
    result.label === "deepfake" ? "#f43f5e" :
    result.label === "ai_generated" || result.label === "suspicious" ? "#f59e0b" :
    "#10b981";
  el.innerHTML = `
    <div class="card" style="border-left:4px solid ${tone};">
      <div><strong style="text-transform:capitalize;color:${tone};">${result.label?.replace(/_/g," ")}</strong> · ${Math.round((result.confidence ?? 0) * 100)}%</div>
      <p>${result.explanation ?? ""}</p>
    </div>
  `;
}
