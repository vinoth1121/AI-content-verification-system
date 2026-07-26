package com.acvs.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * ACVS application entry point.
 *
 * Hilt wiring happens via the @HiltAndroidApp annotation; this class only
 * needs to exist so the rest of the app can use @HiltViewModel / @Inject.
 */
@HiltAndroidApp
class ACVSApplication : Application()
