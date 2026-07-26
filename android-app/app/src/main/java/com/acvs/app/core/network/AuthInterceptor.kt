package com.acvs.app.core.network

import com.acvs.app.core.storage.TokenStore
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Adds `Authorization: Bearer <token>` to every outgoing request.
 * If the backend returns 401, the caller is responsible for refreshing
 * the token via /api/v1/auth/refresh.
 */
@Singleton
class AuthInterceptor @Inject constructor(
    private val tokenStore: TokenStore,
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val req = chain.request()
        val token = tokenStore.accessToken()
        val authed = if (token != null) {
            req.newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else req
        return chain.proceed(authed)
    }
}
