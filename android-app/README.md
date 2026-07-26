# ACVS Android App

Kotlin + Jetpack Compose Android client for the AI Content Verification
System. Shares the same REST API as the other clients.

## Features

- Material 3 UI with Compose
- Bottom navigation: Overview · New Scan · History · Settings
- Text / image / audio / video upload & detection
- Scan history with offline cache (DataStore)
- Encrypted token storage (AndroidX Security)
- Background monitoring service (Phase 2)

## Build

Open the `android-app/` folder in Android Studio (Giraffe or newer) and
press Run, or from the command line:

```bash
cd android-app
./gradlew assembleDebug
# APK at app/build/outputs/apk/debug/app-debug.apk
```

## Project layout

```
app/src/main/java/com/acvs/app/
├── ACVSApplication.kt          # @HiltAndroidApp entry
├── MainActivity.kt             # Single-activity Compose host
├── core/
│   ├── network/                # Retrofit + OkHttp + auth interceptor
│   ├── storage/                # Encrypted token store
│   └── theme/                  # Material 3 theme
├── data/
│   ├── api/                    # ACVSApi interface
│   ├── model/                  # DTOs
│   └── repo/                   # Repositories
├── feature/
│   ├── auth/                   # Login + register screens
│   ├── overview/               # KPI cards + recent scans
│   ├── scan/                   # Text / image / audio / video scan
│   ├── history/                # Paginated history
│   └── settings/               # Profile + sign-out
```

## Configuration

Set the backend URL in `core/network/NetworkModule.kt`:

```kotlin
private const val BASE_URL = "http://10.0.2.2:8000/"   // emulator → host
```
