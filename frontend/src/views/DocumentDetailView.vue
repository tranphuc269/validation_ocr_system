<template>
  <div>
    <div class="mb-6">
      <button
        @click="goBack"
        class="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
      >
        ← Back
      </button>
      <h1 class="text-3xl font-bold text-gray-900">{{ document?.name || 'Loading...' }}</h1>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="document" class="space-y-6">
      <!-- Top controls: OCR URL, sample upload, run validation -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div class="lg:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">OCR URL</label>
            <div class="flex gap-3">
              <input v-model="editOcrUrl" type="text" placeholder="OCR URL or 'mock'" class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              <button @click="updateDocument" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Save</button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Sample OCR JSON</label>
            <div class="flex gap-3">
              <input type="file" @change="onSampleChange" accept="application/json" class="flex-1 px-4 py-2 border border-gray-300 rounded-lg" />
              <button @click="uploadSample" :disabled="!sampleFile" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400">Upload</button>
            </div>
          </div>
        </div>
        <div class="mt-4 flex items-center gap-4">
          <button @click="startValidation" :disabled="validating" class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400">
            {{ validating ? 'Validating all uploads...' : 'Run Validation (All Uploads)' }}
          </button>
          <div v-if="job" class="text-sm text-gray-600">
            Status: <span class="font-semibold">{{ job.status }}</span>
            <span v-if="job.total_uploads"> ({{ job.processed_uploads || 0 }}/{{ job.total_uploads }})</span>
          </div>
        </div>
      </div>

      <!-- Two-pane layout: Left uploads, Right results for selected upload -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left: uploads & upload button -->
        <div class="bg-white rounded-lg shadow p-6 lg:col-span-1">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold">Uploaded Files</h2>
            <button @click="openUploadModal" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">Upload file</button>
          </div>
          <div v-if="uploads.length === 0" class="text-gray-500 text-center py-8">No files uploaded yet</div>
          <div v-else class="space-y-3 max-h-[600px] overflow-y-auto">
            <div v-for="upload in uploads" :key="upload.id" @click="selectUpload(upload)" :class="['p-3 border rounded-lg cursor-pointer transition-colors', selectedUpload && selectedUpload.id === upload.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50']">
              <div class="flex justify-between items-start gap-2">
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-sm truncate" :title="upload.file_path.split('/').pop()">{{ upload.file_path.split('/').pop() }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ formatDate(upload.created_at) }}</p>
                </div>
                <span v-if="upload.user_input_json_path" class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded whitespace-nowrap">Has input</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: results for selected upload -->
        <div class="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <h2 class="text-xl font-semibold mb-4">Validation Results</h2>
          <div v-if="!selectedUpload" class="text-gray-500 text-center py-12">
            <p>Select a file from the left to view validation results</p>
          </div>
          <div v-else-if="loadingResults" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
          <div v-else-if="currentUploadResults && currentUploadResults.length > 0" class="space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold">File: {{ selectedUpload.file_path.split('/').pop() }}</h3>
              <div class="text-sm text-gray-600">
                Overall Accuracy: <span class="font-semibold text-blue-600">{{ (currentUploadResults.reduce((sum, r) => sum + r.accuracy, 0) / currentUploadResults.length * 100).toFixed(2) }}%</span>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full border-collapse min-w-[600px]">
                <thead>
                  <tr class="bg-gray-100">
                    <th class="border border-gray-300 px-4 py-2 text-left w-[120px]">Field</th>
                    <th class="border border-gray-300 px-4 py-2 text-left min-w-[200px]">User Value</th>
                    <th class="border border-gray-300 px-4 py-2 text-left min-w-[200px]">OCR Value</th>
                    <th class="border border-gray-300 px-4 py-2 text-left w-[100px]">Accuracy</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in currentUploadResults" :key="r.field_name" class="hover:bg-gray-50">
                    <td class="border border-gray-300 px-4 py-2 font-medium align-top">{{ r.field_name }}</td>
                    <td class="border border-gray-300 px-4 py-2 align-top break-words max-w-[300px]">
                      <div class="text-sm" :title="r.user_value">{{ r.user_value || '-' }}</div>
                    </td>
                    <td class="border border-gray-300 px-4 py-2 align-top break-words max-w-[300px]">
                      <div class="text-sm" :title="r.ocr_value">{{ r.ocr_value || '-' }}</div>
                    </td>
                    <td class="border border-gray-300 px-4 py-2 align-top">
                      <span :class="getAccuracyClass(r.accuracy)" class="font-semibold">{{ (r.accuracy * 100).toFixed(2) }}%</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else-if="selectedUpload" class="text-gray-500 text-center py-12">
            <p>No validation results found for this upload.</p>
            <p class="text-sm mt-2">Run validation first to see results.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload + Desired User Values Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="showUploadModal = false">
      <div class="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">Upload file & Desired User Values</h2>
          <button @click="showUploadModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Choose PDF/Image</label>
            <input type="file" @change="onModalUploadFileChange" accept="application/pdf,image/*" class="w-full px-4 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Fields</label>
            <div class="space-y-3">
              <div v-for="field in textFields" :key="field">
                <label class="block text-xs font-medium text-gray-600 mb-1">{{ field }}</label>
                <input v-model="modalUserForm[field]" type="text" :placeholder="`Enter ${field}`" class="w-full px-3 py-2 border border-gray-300 rounded" />
              </div>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="showUploadModal = false" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
          <button @click="submitUploadWithUserForm" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Save & Upload</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const router = useRouter()
const documentId = route.params.documentId

const document = ref(null)
const uploads = ref([])
const loading = ref(true)
const editOcrUrl = ref('')
const sampleFile = ref(null)
const uploadFile = ref(null) // legacy (not used in modal flow)
const textFields = ref([])
const userForm = ref({})
const selectedUploadId = ref('')
const selectedUpload = ref(null)
const uploadResults = ref(null)
const currentUploadResults = ref(null)
const loadingResults = ref(false)
const job = ref(null)
const validating = ref(false)
let pollTimer = null

// Modal state for upload + user form
const showUploadModal = ref(false)
const modalUploadFile = ref(null)
const modalUserForm = ref({})

async function loadDocument() {
  try {
    loading.value = true
    const { data } = await api.get(`/api/documents/${documentId}`)
    document.value = data
    editOcrUrl.value = data.ocr_url || 'mock'
  } catch (error) {
    console.error('Failed to load document:', error)
  } finally {
    loading.value = false
  }
}

async function loadUploads() {
  try {
    const { data } = await api.get(`/api/documents/${documentId}/uploads`)
    uploads.value = data
    if (data.length && !selectedUploadId.value) {
      selectedUploadId.value = data[0].id
    }
  } catch (error) {
    console.error('Failed to load uploads:', error)
  }
}

async function loadTextFields() {
  try {
    const { data } = await api.get(`/api/documents/${documentId}/text-fields`)
    textFields.value = data
    const obj = {}
    for (const k of data) obj[k] = ''
    userForm.value = obj
  } catch (error) {
    // Sample not uploaded yet
    textFields.value = []
  }
}

async function updateDocument() {
  try {
    const { data } = await api.patch(`/api/documents/${documentId}`, { ocr_url: editOcrUrl.value })
    document.value = data
  } catch (error) {
    console.error('Failed to update document:', error)
    alert('Failed to update document')
  }
}

function onSampleChange(e) {
  sampleFile.value = e.target.files[0]
}

function onUploadFileChange(e) {
  uploadFile.value = e.target.files[0]
}

async function uploadSample() {
  if (!sampleFile.value) return
  try {
    const form = new FormData()
    form.append('sample', sampleFile.value)
    const { data } = await api.post(`/api/documents/${documentId}/sample-json`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    document.value = data
    sampleFile.value = null
    await loadTextFields()
  } catch (error) {
    console.error('Failed to upload sample:', error)
    alert('Failed to upload sample')
  }
}

async function uploadFileToDoc() {
  if (!uploadFile.value) return
  try {
    const form = new FormData()
    form.append('file', uploadFile.value)
    await api.post(`/api/documents/${documentId}/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadFile.value = null
    await loadUploads()
  } catch (error) {
    console.error('Failed to upload file:', error)
    alert('Failed to upload file')
  }
}

function openUploadModal() {
  showUploadModal.value = true
  // ensure text fields loaded
  loadTextFields().then(() => {
    const obj = {}
    for (const k of textFields.value) obj[k] = ''
    modalUserForm.value = obj
  })
}

function onModalUploadFileChange(e) {
  modalUploadFile.value = e.target.files[0]
}

async function submitUploadWithUserForm() {
  if (!modalUploadFile.value) {
    alert('Please choose a file to upload')
    return
  }
  try {
    // 1) Upload file
    const form = new FormData()
    form.append('file', modalUploadFile.value)
    const { data: uploaded } = await api.post(`/api/documents/${documentId}/upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const uploadId = uploaded.id
    // 2) Upload user JSON tied to this upload
    const json = JSON.stringify(modalUserForm.value)
    const file = new Blob([json], { type: 'application/json' })
    const userFormData = new FormData()
    userFormData.append('form_json', file, 'user_input.json')
    await api.post(`/api/documents/${uploadId}/user-input`, userFormData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    showUploadModal.value = false
    modalUploadFile.value = null
    await loadUploads()
  } catch (error) {
    console.error('Failed to upload with user form:', error)
    alert('Failed to upload with user form')
  }
}

async function submitUserForm() {
  if (!selectedUploadId.value) return
  try {
    const json = JSON.stringify(userForm.value)
    const file = new Blob([json], { type: 'application/json' })
    const form = new FormData()
    form.append('form_json', file, 'user_input.json')
    await api.post(`/api/documents/${selectedUploadId.value}/user-input`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadUploads()
    alert('User input submitted successfully')
  } catch (error) {
    console.error('Failed to submit user form:', error)
    alert('Failed to submit user form')
  }
}

async function startValidation() {
  try {
    validating.value = true
    const { data } = await api.post('/api/validation/run', { document_id: documentId })
    job.value = data
    if (pollTimer) clearInterval(pollTimer)
    pollTimer = setInterval(async () => {
      try {
        const { data: st } = await api.get(`/api/validation/status/${job.value.job_id}`)
        job.value = st
        if (st.status === 'completed' || st.status === 'failed') {
          clearInterval(pollTimer)
          validating.value = false
          const { data: res } = await api.get(`/api/validation/result/${job.value.job_id}`)
          if (res.result) {
            uploadResults.value = res.result.upload_results
          }
        }
      } catch (error) {
        console.error('Failed to poll status:', error)
      }
    }, 1500)
  } catch (error) {
    console.error('Failed to start validation:', error)
    alert('Failed to start validation')
    validating.value = false
  }
}

function selectUpload(upload) {
  selectedUpload.value = upload
  selectedUploadId.value = upload.id
  loadUploadResults(upload.id)
}

watch(selectedUpload, async (upload) => {
  if (upload) {
    await loadUploadResults(upload.id)
  } else {
    currentUploadResults.value = null
  }
})

async function loadUploadResults(uploadId) {
  try {
    loadingResults.value = true
    const { data } = await api.get(`/api/validation/upload/${uploadId}/results`)
    currentUploadResults.value = data || []
  } catch (error) {
    console.error('Failed to load upload results:', error)
    currentUploadResults.value = []
  } finally {
    loadingResults.value = false
  }
}

function getAccuracyClass(accuracy) {
  if (accuracy >= 0.9) return 'text-green-600 font-semibold'
  if (accuracy >= 0.7) return 'text-yellow-600 font-semibold'
  return 'text-red-600 font-semibold'
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString()
}

function goBack() {
  if (document.value) {
    router.push(`/projects/${document.value.project_id}/documents`)
  } else {
    router.push('/projects')
  }
}

onMounted(async () => {
  await loadDocument()
  await loadUploads()
  await loadTextFields()
})
</script>

