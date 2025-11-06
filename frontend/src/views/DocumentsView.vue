<template>
  <div>
    <div class="mb-6">
      <button
        @click="$router.push('/projects')"
        class="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
      >
        ← Back to Projects
      </button>
      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-900">Documents - {{ projectName }}</h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          + New Document
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="documents.length === 0" class="text-center py-12 text-gray-500">
      No documents found
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="doc in documents"
        :key="doc.id"
        @click="$router.push(`/documents/${doc.id}`)"
        class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition cursor-pointer border border-gray-200"
      >
        <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ doc.name }}</h3>
        <p class="text-sm text-gray-500 mb-2">OCR URL: {{ doc.ocr_url || 'Not set' }}</p>
        <p class="text-sm text-gray-500">Created: {{ formatDate(doc.created_at) }}</p>
      </div>
    </div>

    <!-- Create Document Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Create New Document</h2>
        <input
          v-model="newDocName"
          type="text"
          placeholder="Document name"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500"
        />
        <input
          v-model="newDocOcrUrl"
          type="text"
          placeholder="OCR URL (or 'mock')"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500"
        />
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload Sample OCR JSON (optional)</label>
          <input
            type="file"
            @change="onNewDocSampleChange"
            accept="application/json"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="flex gap-3 justify-end">
          <button
            @click="showCreateModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="createDocument"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create
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

