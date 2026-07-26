/**
 * Content script — listens for "acvs-result" messages from the background
 * worker and renders a non-intrusive overlay on the page.
 */

interface ScanResult {
  id: number;
  modality: string;
  label: string | null;
  confidence: number | null;
  explanation: string | null;
  status: string;
}

chrome.runtime.onMessage.addListener((msg, _sender, _sendResponse) => {
  if (msg.type === "acvs-result" && msg.result) {
    renderOverlay(msg.result as ScanResult);
  }
});

function renderOverlay(result: ScanResult): void {
  // Remove any existing overlay
  document.getElementById("acvs-overlay")?.remove();

  const overlay = document.createElement("div");
  overlay.id = "acvs-overlay";
  overlay.style.cssText = `
    position: fixed;
    bottom: 16px;
    right: 16px;
    z-index: 2147483647;
    width: 320px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    padding: 12px 14px;
    font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #111;
  `;

  const tone =
    result.label === "deepfake" ? "#f43f5e" :
    result.label === "ai_generated" || result.label === "suspicious" ? "#f59e0b" :
    "#10b981";

  const label = result.label ? result.label.replace(/_/g, " ") : "—";
  const conf = result.confidence != null ? `${Math.round(result.confidence * 100)}%` : "—";

  overlay.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
      <strong style="font-size:13px;">ACVS verdict</strong>
      <button id="acvs-close" style="border:0;background:transparent;cursor:pointer;font-size:16px;color:#6b7280;">×</button>
    </div>
    <div style="display:flex;gap:6px;align-items:center;margin-bottom:6px;">
      <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${tone};"></span>
      <span style="text-transform:capitalize;font-weight:600;color:${tone};">${label}</span>
      <span style="margin-left:auto;color:#374151;font-weight:500;">${conf}</span>
    </div>
    <p style="color:#4b5563;font-size:12px;margin:0;">${result.explanation ?? ""}</p>
    <p style="color:#9ca3af;font-size:10px;margin:6px 0 0;">Scan #${result.id} · ${result.modality}</p>
  `;

  document.body.appendChild(overlay);
  document.getElementById("acvs-close")?.addEventListener("click", () => overlay.remove());

  // Auto-dismiss after 12s
  setTimeout(() => overlay.remove(), 12000);
}
