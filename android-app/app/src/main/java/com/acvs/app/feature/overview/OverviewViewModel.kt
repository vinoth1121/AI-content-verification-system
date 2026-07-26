package com.acvs.app.feature.overview

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.acvs.app.data.api.ACVSApi
import com.acvs.app.data.model.ScanResponse
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class OverviewState(
    val loading: Boolean = true,
    val totalScans: Int = 0,
    val deepfakes: Int = 0,
    val recent: List<ScanResponse> = emptyList(),
    val error: String? = null,
)

@HiltViewModel
class OverviewViewModel @Inject constructor(
    private val api: ACVSApi,
) : ViewModel() {

    private val _state = MutableStateFlow(OverviewState())
    val state: StateFlow<OverviewState> = _state.asStateFlow()

    init { refresh() }

    fun refresh() {
        _state.value = _state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            try {
                val res = api.history(page = 1, pageSize = 20)
                _state.value = OverviewState(
                    loading = false,
                    totalScans = res.total,
                    deepfakes = res.items.count { it.label == "deepfake" },
                    recent = res.items,
                )
            } catch (e: Exception) {
                _state.value = _state.value.copy(loading = false, error = e.message)
            }
        }
    }
}
