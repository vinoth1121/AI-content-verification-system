package com.acvs.app.feature.overview

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun OverviewScreen(viewModel: OverviewViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()

    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Overview", style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(16.dp))

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            KpiCard("Total scans", state.totalScans.toString(), Modifier.weight(1f))
            KpiCard("Deepfakes", state.deepfakes.toString(), Modifier.weight(1f))
        }
        Spacer(Modifier.height(16.dp))

        Text("Recent scans", style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(8.dp))
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(state.recent) { scan ->
                ScanRow(scan)
            }
        }
    }
}

@Composable
private fun KpiCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        Column(Modifier.padding(16.dp)) {
            Text(label, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(value, style = MaterialTheme.typography.headlineMedium)
        }
    }
}

@Composable
private fun ScanRow(scan: com.acvs.app.data.model.ScanResponse) {
    Card(Modifier.fillMaxWidth()) {
        Row(Modifier.padding(12.dp), verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("#${scan.id} · ${scan.modality}", style = MaterialTheme.typography.bodySmall)
                Text(scan.label ?: "—", style = MaterialTheme.typography.titleSmall)
            }
            Text(
                scan.confidence?.let { "${(it * 100).toInt()}%" } ?: "—",
                style = MaterialTheme.typography.titleMedium,
            )
        }
    }
}
