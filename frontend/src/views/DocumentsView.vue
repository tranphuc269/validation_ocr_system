<template>
  <div>
    <div class="mb-8">
      <button
        @click="$router.push('/projects')"
        class="text-blue-600 hover:text-blue-700 mb-6 flex items-center gap-2 transition-colors font-medium"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
        Back to Projects
      </button>
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">{{ projectName }}</h1>
          <p class="text-gray-600">Manage documents and OCR configurations</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2 font-medium whitespace-nowrap"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Document
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading documents...</p>
    </div>

    <div v-else-if="documents.length === 0" class="text-center py-20">
      <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-4">
        <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      </div>
      <p class="text-lg text-gray-600 mb-2">No documents found</p>
      <p class="text-sm text-gray-500">Create your first document to get started</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="doc in documents"
        :key="doc.id"
        @click="$router.push(`/documents/${doc.id}`)"
        class="group bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer border border-gray-200 hover:border-blue-300 relative overflow-hidden"
      >
        <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full -mr-16 -mt-16 opacity-50 group-hover:opacity-75 transition-opacity"></div>
        <div class="relative">
          <div class="flex items-start justify-between mb-4">
            <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3 group-hover:text-indigo-600 transition-colors">{{ doc.name }}</h3>
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
              <span class="text-gray-600 truncate">{{ doc.ocr_url || 'Not configured' }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm text-gray-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              <span>Created {{ formatDate(doc.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Document Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md transform transition-all max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Create New Document</h2>
            <button
              @click="showCreateModal = false"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <p class="text-sm text-gray-500 mt-2">Configure a new document type for validation</p>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Document Name</label>
            <input
              v-model="newDocName"
              type="text"
              placeholder="e.g., Invoice, ID Card"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              autofocus
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">OCR URL</label>
            <input
              v-model="newDocOcrUrl"
              type="text"
              placeholder="OCR endpoint URL or 'mock'"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
            />
            <p class="text-xs text-gray-500 mt-1">Use 'mock' for testing without a real OCR service</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Upload Sample OCR JSON (optional)</label>
            <label class="cursor-pointer block">
              <input
                type="file"
                @change="onNewDocSampleChange"
                accept="application/json"
                class="hidden"
              />
              <div class="px-4 py-3 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all flex items-center justify-center gap-2 min-h-[48px]">
                <svg class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                <span class="text-sm text-gray-600 truncate">{{ newDocSampleFile ? newDocSampleFile.name : 'Choose JSON file...' }}</span>
              </div>
            </label>
            <p class="text-xs text-gray-500 mt-1">Upload a sample JSON to define the expected data structure</p>
          </div>
        </div>
        <div class="p-6 border-t border-gray-200 flex gap-3 justify-end">
          <button
            @click="showCreateModal = false"
            class="px-6 py-2.5 border border-gray-300 rounded-xl hover:bg-gray-50 transition font-medium"
          >
            Cancel
          </button>
          <button
            @click="createDocument"
            class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl font-medium"
          >
            Create Document
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const router = useRouter()
const projectId = route.params.projectId

const documents = ref([])
const loading = ref(true)
const projectName = ref('')
const showCreateModal = ref(false)
const newDocName = ref('')
const newDocOcrUrl = ref('mock')
const newDocSampleFile = ref(null)

async function loadProject() {
  try {
    const { data } = await api.get(`/api/projects`)
    const project = data.find(p => p.id === projectId)
    if (project) projectName.value = project.name
  } catch (error) {
    console.error('Failed to load project:', error)
  }
}

async function loadDocuments() {
  try {
    loading.value = true
    const { data } = await api.get('/api/documents', { params: { project_id: projectId } })
    documents.value = data
  } catch (error) {
    console.error('Failed to load documents:', error)
  } finally {
    loading.value = false
  }
}

function onNewDocSampleChange(e) {
  newDocSampleFile.value = e.target.files[0]
}

async function createDocument() {
  if (!newDocName.value.trim()) return
  try {
    const { data: newDoc } = await api.post('/api/documents', {
      project_id: projectId,
      name: newDocName.value,
      ocr_url: newDocOcrUrl.value || 'mock'
    })
    
    // Upload sample JSON if provided
    if (newDocSampleFile.value) {
      const form = new FormData()
      form.append('sample', newDocSampleFile.value)
      await api.post(`/api/documents/${newDoc.id}/sample-json`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    newDocName.value = ''
    newDocOcrUrl.value = 'mock'
    newDocSampleFile.value = null
    showCreateModal.value = false
    await loadDocuments()
  } catch (error) {
    console.error('Failed to create document:', error)
    alert('Failed to create document')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(async () => {
  await loadProject()
  await loadDocuments()
})
</script>

