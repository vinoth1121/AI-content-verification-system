package com.acvs.app.core.storage

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Encrypted token store backed by EncryptedSharedPreferences (AES-GCM).
 *
 * Token presence is exposed as a StateFlow so Compose can react to
 * sign-in / sign-out.
 */
@Singleton
class TokenStore @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    private val prefs = run {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            context,
            "acvs_secure_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    }

    private val _hasToken = MutableStateFlow(prefs.getString(KEY_ACCESS, null) != null)
    val hasToken: StateFlow<Boolean> = _hasToken

    fun saveTokens(access: String, refresh: String) {
        prefs.edit()
            .putString(KEY_ACCESS, access)
            .putString(KEY_REFRESH, refresh)
            .apply()
        _hasToken.value = true
    }

    fun accessToken(): String? = prefs.getString(KEY_ACCESS, null)
    fun refreshToken(): String? = prefs.getString(KEY_REFRESH, null)

    fun clear() {
        prefs.edit().clear().apply()
        _hasToken.value = false
    }

    fun hasTokenBlocking(): Boolean = _hasToken.value

    companion object {
        private const val KEY_ACCESS = "access_token"
        private const val KEY_REFRESH = "refresh_token"
    }
}
