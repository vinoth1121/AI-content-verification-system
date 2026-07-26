package com.acvs.app.core.network

import com.acvs.app.data.model.LoginRequest
import com.acvs.app.data.model.LoginResponse
import com.acvs.app.data.model.ScanListResponse
import com.acvs.app.data.model.ScanResponse
import com.acvs.app.data.model.TextScanRequest
import com.acvs.app.data.model.UserResponse
import okhttp3.MultipartBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Retrofit interface mirroring the FastAPI backend.
 *
 * Keep the paths in sync with `backend/app/api/v1/`.
 */
interface ACVSApi {

    @POST("api/v1/auth/register")
    suspend fun register(@Body body: LoginRequest): LoginResponse

    @POST("api/v1/auth/login")
    suspend fun login(@Body body: LoginRequest): LoginResponse

    @GET("api/v1/auth/me")
    suspend fun me(): UserResponse

    @POST("api/v1/scan/text")
    suspend fun scanText(@Body body: TextScanRequest): ScanResponse

    @POST("api/v1/scan/fake-news")
    suspend fun scanFakeNews(@Body body: TextScanRequest): ScanResponse

    @Multipart
    @POST("api/v1/scan/image")
    suspend fun scanImage(@Part file: MultipartBody.Part): ScanResponse

    @Multipart
    @POST("api/v1/scan/audio")
    suspend fun scanAudio(@Part file: MultipartBody.Part): ScanResponse

    @Multipart
    @POST("api/v1/scan/video")
    suspend fun scanVideo(@Part file: MultipartBody.Part): ScanResponse

    @GET("api/v1/scan/history")
    suspend fun history(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20,
        @Query("modality") modality: String? = null,
    ): ScanListResponse

    @GET("api/v1/scan/history/{id}")
    suspend fun scanDetail(@Path("id") id: Int): ScanResponse
}
