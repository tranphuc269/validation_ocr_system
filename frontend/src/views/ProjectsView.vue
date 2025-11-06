<template>
  <div>
    <div class="mb-6 flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900">Projects</h1>
      <div class="flex gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search projects..."
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          + New Project
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="filteredProjects.length === 0" class="text-center py-12 text-gray-500">
      No projects found
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="project in filteredProjects"
        :key="project.id"
        @click="$router.push(`/projects/${project.id}/documents`)"
        class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition cursor-pointer border border-gray-200"
      >
        <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ project.name }}</h3>
        <p class="text-sm text-gray-500">Created: {{ formatDate(project.created_at) }}</p>
      </div>
    </div>

    <!-- Create Project Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">Create New Project</h2>
        <input
          v-model="newProjectName"
          type="text"
          placeholder="Project name"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500"
          @keyup.enter="createProject"
        />
        <div class="flex gap-3 justify-end">
          <button
            @click="showCreateModal = false"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="createProject"
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
import { ref, computed, onMounted } from 'vue'
import api from '../api/axios'

const projects = ref([])
const loading = ref(true)
const searchQuery = ref('')
const showCreateModal = ref(false)
const newProjectName = ref('')

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  const query = searchQuery.value.toLowerCase()
  return projects.value.filter(p => p.name.toLowerCase().includes(query))
})

async function loadProjects() {
  try {
    loading.value = true
    const { data } = await api.get('/api/projects')
    projects.value = data
  } catch (error) {
    console.error('Failed to load projects:', error)
  } finally {
    loading.value = false
  }
}

async function createProject() {
  if (!newProjectName.value.trim()) return
  try {
    await api.post('/api/projects', { name: newProjectName.value })
    newProjectName.value = ''
    showCreateModal.value = false
    await loadProjects()
  } catch (error) {
    console.error('Failed to create project:', error)
    alert('Failed to create project')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  loadProjects()
})
</script>

