package com.acvs.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.acvs.app.core.theme.ACVSTheme
import com.acvs.app.feature.auth.AuthScreen
import com.acvs.app.feature.overview.OverviewScreen
import com.acvs.app.core.storage.TokenStore
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

/**
 * Single-activity host. The decision between AuthScreen and OverviewScreen
 * is made by checking for a stored access token at composition time.
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject lateinit var tokenStore: TokenStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ACVSTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    val hasToken = tokenStore.hasTokenBlocking()
                    if (hasToken) OverviewScreen() else AuthScreen()
                }
            }
        }
    }
}
