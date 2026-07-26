package com.acvs.app.core.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF10B981),
    onPrimary = Color.White,
    secondary = Color(0xFF6750A4),
    background = Color(0xFFF8FAFC),
    surface = Color.White,
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF34D399),
    onPrimary = Color(0xFF002114),
    secondary = Color(0xFFCFBCFF),
    background = Color(0xFF0F172A),
    surface = Color(0xFF1E293B),
)

@Composable
fun ACVSTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(colorScheme = if (darkTheme) DarkColors else LightColors, content = content)
}
