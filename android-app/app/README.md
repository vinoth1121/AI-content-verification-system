# ACVS Android App

Kotlin + Jetpack Compose Android client for the AI Content Verification System.

## Stack
- Kotlin 2.0 · Jetpack Compose · Material 3
- Hilt for DI
- Retrofit + OkHttp + Moshi for networking
- EncryptedSharedPreferences for token storage
- Coil for image loading
- DataStore for offline cache (Phase 2)

## Build
Open in Android Studio Giraffe or newer, or:

```bash
cd android-app
./gradlew assembleDebug
```

## Architecture
Clean Architecture with three layers:
- **data/** — Retrofit API, Moshi DTOs, repositories
- **core/** — networking, storage, theme
- **feature/** — Compose screens grouped by feature (auth, overview, scan, history, settings)

Each feature has a `*Screen.kt` (Composables) and a `*ViewModel.kt`
(HiltViewModel + StateFlow).
