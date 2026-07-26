package com.acvs.app.data.model

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class LoginRequest(val email: String, val password: String, val full_name: String? = null)

@JsonClass(generateAdapter = true)
data class LoginResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String,
    val user: UserResponse,
)

@JsonClass(generateAdapter = true)
data class UserResponse(
    val id: Int,
    val email: String,
    val full_name: String,
    val role: String,
    val is_active: Boolean,
)

@JsonClass(generateAdapter = true)
data class TextScanRequest(val text: String, val title: String? = null)

@JsonClass(generateAdapter = true)
data class ScanResponse(
    val id: Int,
    val modality: String,
    val status: String,
    val confidence: Double?,
    val label: String?,
    val explanation: String?,
    val result: Map<String, Any>?,
    val created_at: String,
    val completed_at: String?,
    val duration_ms: Int?,
)

@JsonClass(generateAdapter = true)
data class ScanListResponse(
    val items: List<ScanResponse>,
    val total: Int,
    val page: Int,
    val page_size: Int,
)
