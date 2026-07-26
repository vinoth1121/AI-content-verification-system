package com.acvs.app.feature.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.acvs.app.core.storage.TokenStore
import com.acvs.app.data.api.ACVSApi
import com.acvs.app.data.model.LoginRequest
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthState(
    val email: String = "",
    val password: String = "",
    val loading: Boolean = false,
    val error: String? = null,
    val authed: Boolean = false,
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val api: ACVSApi,
    private val tokenStore: TokenStore,
) : ViewModel() {

    private val _state = MutableStateFlow(AuthState())
    val state: StateFlow<AuthState> = _state.asStateFlow()

    fun onEmailChange(v: String) = _state.update { it.copy(email = v, error = null) }
    fun onPasswordChange(v: String) = _state.update { it.copy(password = v, error = null) }

    fun login() {
        val s = _state.value
        if (s.email.isBlank() || s.password.isBlank()) return
        _state.update { it.copy(loading = true, error = null) }
        viewModelScope.launch {
            try {
                val res = api.login(LoginRequest(s.email, s.password))
                tokenStore.saveTokens(res.access_token, res.refresh_token)
                _state.update { it.copy(loading = false, authed = true) }
            } catch (e: Exception) {
                _state.update { it.copy(loading = false, error = e.message ?: "Login failed") }
            }
        }
    }
}
