<template>
  <div>
    <button @click="goBack" class="text-blue-600 hover:text-blue-700 mb-6 flex items-center gap-2 transition-colors font-medium">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
      </svg>
      Back
    </button>

    <div v-if="loading" class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading upload details...</p>
    </div>
    <div v-else-if="error" class="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl shadow-sm">
      <div class="flex items-center gap-3">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="font-medium">{{ error }}</span>
      </div>
    </div>
    <div v-else class="space-y-6">
      <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-3xl font-bold text-gray-900">{{ document?.name }}</h1>
            <div class="flex flex-wrap items-center gap-4 mt-2">
              <p class="text-sm text-gray-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <span class="break-all">{{ upload?.file_path?.split('/').pop() }}</span>
              </p>
              <p class="text-sm text-gray-500 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Uploaded {{ formatDate(upload?.created_at) }}
              </p>
            </div>
          </div>
        </div>
        <div class="text-right px-6 py-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
          <p class="text-sm text-gray-600 mb-1">Overall Accuracy</p>
          <p class="text-3xl font-bold text-blue-600">{{ overallAccuracy }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div class="border-b border-gray-200 px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
              Preview
            </h2>
            <a
              :href="downloadUrl"
              class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl font-medium"
              download
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
              Download
            </a>
          </div>
          <div class="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center min-h-[480px] p-4">
            <div v-if="previewLoading" class="text-white text-center">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-white/30 border-t-white mb-4"></div>
              <p class="font-medium">Loading preview...</p>
            </div>
            <div v-else-if="previewError" class="text-gray-100 text-center px-6">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/20 mb-4">
                <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <p class="font-medium">{{ previewError }}</p>
            </div>
            <img v-else-if="previewUrl && previewType.startsWith('image/')" :src="previewUrl" alt="Preview" class="max-h-[600px] max-w-full object-contain rounded-lg shadow-2xl" />
            <div v-else class="text-gray-100 text-center px-6">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500/20 mb-4">
                <svg class="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
              </div>
              <p class="font-medium mb-2">Preview not available</p>
              <p class="text-sm text-gray-400">Use the download button to view the file</p>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <h2 class="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Validation Results
            </h2>
            <div v-if="resultsLoading" class="text-center py-12">
              <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"></div>
              <p class="mt-4 text-gray-600">Loading results...</p>
            </div>
            <div v-else-if="validationResults.length" class="overflow-x-auto rounded-xl border border-gray-200">
              <table class="w-full border-collapse min-w-[480px]">
                <thead>
                  <tr class="bg-gradient-to-r from-gray-50 to-gray-100">
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 w-[140px]">Field</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">User Value</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">OCR Value</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 w-[120px]">Accuracy</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="r in validationResults" :key="r.field_name" class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-3 font-semibold text-gray-900 align-top">{{ r.field_name }}</td>
                    <td class="px-4 py-3 align-top break-words">
                      <div class="text-sm text-gray-700" :title="r.user_value">{{ r.user_value || '-' }}</div>
                    </td>
                    <td class="px-4 py-3 align-top break-words">
                      <div class="text-sm text-gray-700" :title="r.ocr_value">{{ r.ocr_value || '-' }}</div>
                    </td>
                    <td class="px-4 py-3 align-top">
                      <span :class="getAccuracyClass(r.accuracy)" class="font-bold text-lg">{{ (r.accuracy * 100).toFixed(2) }}%</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-12">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 mb-4">
                <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
              </div>
              <p class="text-gray-600 font-medium mb-2">No validation results yet</p>
              <p class="text-sm text-gray-500">Run validation from the document detail page</p>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                Desired User Values
              </h2>
              <div class="flex items-center gap-2">
                <button v-if="editing" @click="cancelEditing" class="px-4 py-2 border border-gray-300 rounded-xl hover:bg-gray-50 transition font-medium">Cancel</button>
                <button
                  v-if="!editing"
                  @click="startEditing"
                  :disabled="userValuesLoading"
                  class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 transition-all shadow-md hover:shadow-lg font-medium flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  Edit Values
                </button>
              </div>
            </div>

            <div v-if="userValuesLoading" class="text-center py-12">
              <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"></div>
              <p class="mt-4 text-gray-600">Loading user values...</p>
            </div>
            <div v-else>
              <div v-if="editing">
                <div v-if="Object.keys(userForm).length" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="field in Object.keys(userForm)" :key="field" class="bg-gray-50 rounded-lg p-4">
                      <label class="block text-sm font-semibold text-gray-700 mb-2">{{ field }}</label>
                      <input
                        v-model="userForm[field]"
                        type="text"
                        :placeholder="`Enter ${field}`"
                        class="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                      />
                    </div>
                  </div>
                  <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
                    <button @click="cancelEditing" class="px-6 py-2.5 border border-gray-300 rounded-xl hover:bg-gray-50 transition font-medium">Cancel</button>
                    <button
                      @click="saveUserValues"
                      :disabled="savingValues"
                      class="px-6 py-2.5 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 transition-all shadow-lg hover:shadow-xl font-medium flex items-center gap-2"
                    >
                      <svg v-if="!savingValues" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                      <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                      {{ savingValues ? 'Saving...' : 'Save Values' }}
                    </button>
                  </div>
                </div>
                <div v-else class="text-center py-12">
                  <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                  </div>
                  <p class="text-gray-600 font-medium">No fields available to edit</p>
                  <p class="text-sm text-gray-500 mt-1">Upload a sample JSON first</p>
                </div>
              </div>
              <div v-else>
                <div v-if="Object.keys(userValues).length" class="overflow-x-auto rounded-xl border border-gray-200">
                  <table class="w-full border-collapse min-w-[480px]">
                    <thead>
                      <tr class="bg-gradient-to-r from-gray-50 to-gray-100">
                        <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 w-[160px]">Field</th>
                        <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">User Value</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                      <tr v-for="(val, key) in userValues" :key="key" class="hover:bg-gray-50 transition-colors">
                        <td class="px-4 py-3 font-semibold text-gray-900 align-top">{{ key }}</td>
                        <td class="px-4 py-3 align-top break-words">
                          <div class="text-sm text-gray-700" :title="val">{{ val || '-' }}</div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-center py-12">
                  <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </div>
                  <p class="text-gray-600 font-medium">No desired values saved yet</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const router = useRouter()
const documentId = route.params.documentId
const uploadId = route.params.uploadId

const loading = ref(true)
const error = ref('')
const document = ref(null)
const upload = ref(null)
const validationResults = ref([])
const resultsLoading = ref(false)
const userValues = ref({})
const userValuesLoading = ref(false)
const textFields = ref([])
const previewUrl = ref('')
const previewType = ref('')
const previewLoading = ref(false)
const previewError = ref('')
const userForm = ref({})
const editing = ref(false)
const savingValues = ref(false)

const downloadUrl = computed(() => `${api.defaults.baseURL}/api/documents/upload/${uploadId}/file`)
const overallAccuracy = computed(() => {
  if (!validationResults.value.length) return 'N/A'
  const score = validationResults.value.reduce((sum, r) => sum + r.accuracy, 0) / validationResults.value.length
  return `${(score * 100).toFixed(2)}%`
})

async function loadDocument() {
  const { data } = await api.get(`/api/documents/${documentId}`)
  document.value = data
}

async function loadUpload() {
  const { data } = await api.get(`/api/documents/upload/${uploadId}`)
  upload.value = data
}

async function loadTextFields() {
  try {
    const { data } = await api.get(`/api/documents/${documentId}/text-fields`)
    textFields.value = data
  } catch (err) {
    textFields.value = []
  }
}

async function loadResults() {
  resultsLoading.value = true
  try {
    const { data } = await api.get(`/api/validation/upload/${uploadId}/results`)
    validationResults.value = data || []
  } finally {
    resultsLoading.value = false
  }
}

async function loadUserValues() {
  userValuesLoading.value = true
  try {
    const { data } = await api.get(`/api/documents/upload/${uploadId}/user-input`)
    userValues.value = data
  } catch (err) {
    if (err?.response?.status === 404) {
      userValues.value = {}
    } else {
      console.error('Failed to load user values', err)
    }
  } finally {
    userValuesLoading.value = false
    const obj = {}
    const keys = Object.keys(userValues.value).length ? Object.keys(userValues.value) : textFields.value
    keys.forEach((k) => {
      obj[k] = userValues.value[k] ?? ''
    })
    userForm.value = obj
  }
}

async function loadPreview() {
  previewLoading.value = true
  previewError.value = ''
  if (previewUrl.value) {
    window.URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  try {
    const response = await api.get(`/api/documents/upload/${uploadId}/file`, { responseType: 'blob' })
    previewType.value = response.headers['content-type'] || ''
    const blob = new Blob([response.data], { type: previewType.value })
    previewUrl.value = window.URL.createObjectURL(blob)
  } catch (err) {
    console.error('Failed to load preview', err)
    previewError.value = 'Unable to preview this file. Try downloading instead.'
  } finally {
    previewLoading.value = false
  }
}

function startEditing() {
  if (!Object.keys(userForm.value).length && textFields.value.length) {
    const obj = {}
    textFields.value.forEach((k) => {
      obj[k] = userValues.value[k] ?? ''
    })
    userForm.value = obj
  }
  editing.value = true
}

function cancelEditing() {
  editing.value = false
  const obj = {}
  const keys = Object.keys(userValues.value).length ? Object.keys(userValues.value) : textFields.value
  keys.forEach((k) => {
    obj[k] = userValues.value[k] ?? ''
  })
  userForm.value = obj
}

async function saveUserValues() {
  try {
    savingValues.value = true
    const json = JSON.stringify(userForm.value)
    const file = new Blob([json], { type: 'application/json' })
    const form = new FormData()
    form.append('form_json', file, 'user_input.json')
    await api.post(`/api/documents/${uploadId}/user-input`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    editing.value = false
    await loadUserValues()
    await loadResults()
    alert('User values updated successfully')
  } catch (error) {
    console.error('Failed to save user values', error)
    alert('Failed to save user values')
  } finally {
    savingValues.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString()
}

function getAccuracyClass(score) {
  if (score >= 0.9) return 'text-green-600'
  if (score >= 0.7) return 'text-yellow-600'
  return 'text-red-600'
}

function goBack() {
  router.push({ name: 'document-detail', params: { documentId } })
}

onMounted(async () => {
  try {
    loading.value = true
    await Promise.all([loadDocument(), loadUpload(), loadTextFields()])
    await Promise.all([loadResults(), loadUserValues(), loadPreview()])
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load upload detail. Try again later.'
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (previewUrl.value) {
    window.URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

