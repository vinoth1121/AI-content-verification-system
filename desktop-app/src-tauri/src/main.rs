// ACVS desktop app — Tauri backend commands.
//
// These commands are exposed to the React frontend via `invoke('cmd_name', ...)`.
// They encapsulate calls to the ACVS backend so the frontend never handles
// tokens or HTTP directly.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use tauri::{Manager, State};

const BASE_URL: &str = "http://localhost:8000";

#[derive(Default)]
struct AppState {
    access_token: Mutex<Option<String>>,
    refresh_token: Mutex<Option<String>>,
}

#[derive(Serialize, Deserialize)]
struct LoginPayload {
    email: String,
    password: String,
}

#[derive(Serialize, Deserialize)]
struct LoginResponse {
    access_token: String,
    refresh_token: String,
    user: serde_json::Value,
}

#[derive(Serialize, Deserialize)]
struct TextScanPayload {
    text: String,
    #[serde(default)]
    title: Option<String>,
}

#[tauri::command]
async fn login(payload: LoginPayload, state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let res = client
        .post(format!("{}/api/v1/auth/login", BASE_URL))
        .json(&payload)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !res.status().is_success() {
        return Err(format!("Login failed: HTTP {}", res.status()));
    }
    let body: LoginResponse = res.json().await.map_err(|e| e.to_string())?;
    *state.access_token.lock().unwrap() = Some(body.access_token.clone());
    *state.refresh_token.lock().unwrap() = Some(body.refresh_token.clone());
    Ok(serde_json::to_value(body).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn scan_text(payload: TextScanPayload, state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let token = state.access_token.lock().unwrap().clone().ok_or("Not authenticated")?;
    let client = reqwest::Client::new();
    let res = client
        .post(format!("{}/api/v1/scan/text", BASE_URL))
        .header("Authorization", format!("Bearer {}", token))
        .json(&payload)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    res.json().await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn history(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let token = state.access_token.lock().unwrap().clone().ok_or("Not authenticated")?;
    let client = reqwest::Client::new();
    let res = client
        .get(format!("{}/api/v1/scan/history", BASE_URL))
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    res.json().await.map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(AppState::default())
        .invoke_handler(tauri::generate_handler![login, scan_text, history])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
