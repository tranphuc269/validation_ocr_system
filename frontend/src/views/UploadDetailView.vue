<template>
  <div>
    <button @click="goBack" class="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2">
      ← Back
    </button>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      {{ error }}
    </div>
    <div v-else class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ document?.name }}</h1>
          <p class="text-sm text-gray-500 mt-1 break-all">File: {{ upload?.file_path?.split('/').pop() }}</p>
          <p class="text-sm text-gray-500">Uploaded: {{ formatDate(upload?.created_at) }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-600">Overall Accuracy</p>
          <p class="text-2xl font-semibold text-blue-600">{{ overallAccuracy }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="border-b px-6 py-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold">Preview</h2>
            <a
              :href="downloadUrl"
              class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              download
            >
              Download
            </a>
          </div>
          <div class="bg-gray-900 flex items-center justify-center min-h-[360px]">
            <div v-if="previewLoading" class="text-white text-center">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-3"></div>
              <p>Loading preview...</p>
            </div>
            <div v-else-if="previewError" class="text-gray-100 text-center px-6">
              {{ previewError }}
            </div>
            <img v-else-if="previewUrl && previewType.startsWith('image/')" :src="previewUrl" alt="Preview" class="max-h-[480px] max-w-full object-contain" />
            <div v-else class="text-gray-100 text-center px-6">
              Preview not available. Use the download button instead.
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold mb-4">Validation Results</h2>
            <div v-if="resultsLoading" class="text-center py-6">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
            <div v-else-if="validationResults.length" class="overflow-x-auto">
              <table class="w-full border-collapse min-w-[480px]">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="border border-gray-300 px-4 py-2 text-left w-[140px]">Field</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">User Value</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">OCR Value</th>
                    <th class="border border-gray-300 px-4 py-2 text-left w-[100px]">Accuracy</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in validationResults" :key="r.field_name" class="hover:bg-gray-50">
                    <td class="border border-gray-300 px-4 py-2 font-medium align-top">{{ r.field_name }}</td>
                    <td class="border border-gray-300 px-4 py-2 align-top break-words">
                      <div class="text-sm" :title="r.user_value">{{ r.user_value || '-' }}</div>
                    </td>
                    <td class="border border-gray-300 px-4 py-2 align-top break-words">
                      <div class="text-sm" :title="r.ocr_value">{{ r.ocr_value || '-' }}</div>
                    </td>
                    <td class="border border-gray-300 px-4 py-2 align-top">
                      <span :class="getAccuracyClass(r.accuracy)" class="font-semibold">{{ (r.accuracy * 100).toFixed(2) }}%</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-sm text-gray-500">
              No validation results yet. Run validation from the document detail page.
            </div>
          </div>

          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold">Desired User Values</h2>
              <div class="flex items-center gap-2">
                <button v-if="editing" @click="cancelEditing" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
                <button
                  v-if="!editing"
                  @click="startEditing"
                  :disabled="userValuesLoading"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                  Edit Desired Values
                </button>
              </div>
            </div>

            <div v-if="userValuesLoading" class="text-center py-6">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
            <div v-else>
              <div v-if="editing">
                <div v-if="Object.keys(userForm).length" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="field in Object.keys(userForm)" :key="field">
                      <label class="block text-sm font-medium text-gray-700 mb-1">{{ field }}</label>
                      <input
                        v-model="userForm[field]"
                        type="text"
                        :placeholder="`Enter ${field}`"
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div class="flex justify-end gap-3">
                    <button @click="cancelEditing" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
                    <button
                      @click="saveUserValues"
                      :disabled="savingValues"
                      class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                    >
                      {{ savingValues ? 'Saving...' : 'Save Values' }}
                    </button>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-500">No fields available to edit. Upload a sample JSON first.</div>
              </div>
              <div v-else>
                <div v-if="Object.keys(userValues).length" class="overflow-x-auto">
                  <table class="w-full border-collapse min-w-[480px]">
                    <thead>
                      <tr class="bg-gray-100">
                        <th class="border border-gray-300 px-4 py-2 text-left w-[160px]">Field</th>
                        <th class="border border-gray-300 px-4 py-2 text-left">User Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(val, key) in userValues" :key="key" class="hover:bg-gray-50">
                        <td class="border border-gray-300 px-4 py-2 font-medium align-top">{{ key }}</td>
                        <td class="border border-gray-300 px-4 py-2 align-top break-words">
                          <div class="text-sm" :title="val">{{ val || '-' }}</div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-sm text-gray-500">No desired values saved yet.</div>
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

