/**
 * Options page script — configure backend URL.
 */
document.addEventListener("DOMContentLoaded", async () => {
  const { apiBase } = await chrome.storage.local.get("apiBase");
  const input = document.getElementById("apiBase") as HTMLInputElement;
  input.value = apiBase || "http://localhost:8000";

  document.getElementById("save")!.addEventListener("click", async () => {
    await chrome.storage.local.set({ apiBase: input.value });
    document.getElementById("saved")!.textContent = "Saved.";
  });
});
