/**
 * Background service worker — handles context-menu registration, message
 * routing between content script / popup / options, and calls to the ACVS
 * backend via fetch().
 */

const API_BASE = "http://localhost:8000"; // overridden via options page in production

// --------------------------------------------------------------------------- //
// Context menu
// --------------------------------------------------------------------------- //
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "acvs-scan-text",
    title: "Verify with ACVS (text)",
    contexts: ["selection"],
  });
  chrome.contextMenus.create({
    id: "acvs-scan-image",
    title: "Verify with ACVS (image)",
    contexts: ["image"],
  });
  chrome.contextMenus.create({
    id: "acvs-scan-link",
    title: "Verify with ACVS (fake news)",
    contexts: ["link"],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const token = await getAccessToken();
  if (!token) {
    notify("Please sign in to ACVS via the extension popup.");
    return;
  }

  try {
    if (info.menuItemId === "acvs-scan-text" && info.selectionText) {
      const result = await scanText(token, info.selectionText);
      showResultInTab(tab.id, result);
    } else if (info.menuItemId === "acvs-scan-image" && info.srcUrl) {
      const blob = await fetch(info.srcUrl).then((r) => r.blob());
      const result = await scanImage(token, blob);
      showResultInTab(tab.id, result);
    } else if (info.menuItemId === "acvs-scan-link" && info.linkUrl) {
      // Fetch the linked page text and run fake-news detection
      const text = await fetch(info.linkUrl).then((r) => r.text());
      const result = await scanFakeNews(token, text, info.linkUrl);
      showResultInTab(tab.id, result);
    }
  } catch (err) {
    notify(`ACVS scan failed: ${err.message}`);
  }
});

// --------------------------------------------------------------------------- //
// Message router (popup / options / content)
// --------------------------------------------------------------------------- //
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    try {
      switch (msg.type) {
        case "login":
          sendResponse(await login(msg.email, msg.password));
          break;
        case "scan-text":
          sendResponse(await scanText(await getAccessToken(), msg.text));
          break;
        case "scan-image":
          sendResponse(await scanImage(await getAccessToken(), msg.blob));
          break;
        case "get-user":
          sendResponse(await getUser(await getAccessToken()));
          break;
        default:
          sendResponse({ error: `Unknown message type: ${msg.type}` });
      }
    } catch (err) {
      sendResponse({ error: err.message });
    }
  })();
  return true; // async
});

// --------------------------------------------------------------------------- //
// API helpers
// --------------------------------------------------------------------------- //
async function login(email, password) {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(`Login failed (${res.status})`);
  const data = await res.json();
  await chrome.storage.local.set({
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    user: data.user,
  });
  return data;
}

async function getUser(token) {
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Not authenticated (${res.status})`);
  return res.json();
}

async function scanText(token, text) {
  const res = await fetch(`${API_BASE}/api/v1/scan/text`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`Scan failed (${res.status})`);
  return res.json();
}

async function scanImage(token, blob) {
  const fd = new FormData();
  fd.append("file", blob);
  const res = await fetch(`${API_BASE}/api/v1/scan/image`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  });
  if (!res.ok) throw new Error(`Scan failed (${res.status})`);
  return res.json();
}

async function scanFakeNews(token, text, title) {
  const res = await fetch(`${API_BASE}/api/v1/scan/fake-news`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ text, title }),
  });
  if (!res.ok) throw new Error(`Scan failed (${res.status})`);
  return res.json();
}

async function getAccessToken() {
  const { access_token } = await chrome.storage.local.get("access_token");
  return access_token;
}

// --------------------------------------------------------------------------- //
// UI helpers
// --------------------------------------------------------------------------- //
function notify(message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title: "ACVS",
    message,
  });
}

function showResultInTab(tabId, result) {
  chrome.tabs.sendMessage(tabId, { type: "acvs-result", result });
}
