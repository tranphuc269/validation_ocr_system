<template>
  <div>
    <div class="mb-8">
      <button
        @click="goBack"
        class="text-blue-600 hover:text-blue-700 mb-6 flex items-center gap-2 transition-colors font-medium"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
        Back
      </button>
      <div class="flex items-center gap-4 mb-2">
        <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <div>
          <h1 class="text-4xl font-bold text-gray-900">{{ document?.name || 'Loading...' }}</h1>
          <p class="text-gray-600 mt-1">Document validation and management</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading document...</p>
    </div>

    <div v-else-if="document" class="space-y-6">
      <!-- Top controls: OCR URL, sample upload, run validation -->
      <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div class="lg:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
              OCR URL
            </label>
            <div class="flex gap-3">
              <input v-model="editOcrUrl" type="text" placeholder="OCR URL or 'mock'" class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition" />
              <button @click="updateDocument" class="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl font-medium whitespace-nowrap">
                <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Save
              </button>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              Upload Sample OCR JSON
            </label>
            <div class="flex gap-3">
              <label class="flex-1 cursor-pointer">
                <input type="file" @change="onSampleChange" accept="application/json" class="hidden" />
                <div class="px-4 py-3 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all flex items-center justify-center gap-2 min-h-[48px]">
                  <svg class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  <span class="text-sm text-gray-600 truncate">{{ sampleFile ? sampleFile.name : 'Choose JSON file...' }}</span>
                </div>
              </label>
              <button @click="uploadSample" :disabled="!sampleFile" class="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 transition-all shadow-lg hover:shadow-xl font-medium whitespace-nowrap flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                Upload
              </button>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-4 flex-wrap pt-6 border-t border-gray-200">
          <button @click="startValidation" :disabled="validating" class="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 transition-all shadow-lg hover:shadow-xl font-medium flex items-center gap-2">
            <svg v-if="!validating" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {{ validating ? 'Validating all uploads...' : 'Run Validation (All Uploads)' }}
          </button>
          <button @click="exportExcel" :disabled="uploads.length === 0" class="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 transition-all shadow-lg hover:shadow-xl font-medium flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Export Excel Report
          </button>
          <div v-if="job" class="ml-auto flex items-center gap-3 px-4 py-2 bg-blue-50 rounded-xl border border-blue-200">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span class="text-sm font-medium text-blue-900">Status: <span class="capitalize">{{ job.status }}</span></span>
            </div>
            <span v-if="job.total_uploads" class="text-sm text-blue-700">({{ job.processed_uploads || 0 }}/{{ job.total_uploads }})</span>
          </div>
        </div>
      </div>

      <!-- Two-pane layout: Left uploads, Right results for selected upload -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left: uploads & upload button -->
        <div class="bg-white rounded-xl shadow-lg p-6 lg:col-span-1 border border-gray-200">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              Uploaded Files
            </h2>
            <button @click="openUploadModal" class="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-md hover:shadow-lg text-sm font-medium flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
              Upload
            </button>
          </div>
          <div v-if="uploads.length === 0" class="text-center py-12">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </div>
            <p class="text-gray-500">No files uploaded yet</p>
          </div>
          <div v-else class="space-y-3 max-h-[600px] overflow-y-auto">
            <div v-for="upload in uploads" :key="upload.id" @click="selectUpload(upload)" :class="['p-4 border-2 rounded-xl cursor-pointer transition-all duration-200', selectedUpload && selectedUpload.id === upload.id ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50 hover:shadow-sm']">
              <div class="flex justify-between items-start gap-2">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="font-semibold text-sm truncate" :title="upload.file_path.split('/').pop()">{{ upload.file_path.split('/').pop() }}</p>
                  </div>
                  <p class="text-xs text-gray-500 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    {{ formatDate(upload.created_at) }}
                  </p>
                </div>
                <span v-if="upload.user_input_json_path" class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full whitespace-nowrap font-medium flex items-center gap-1">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  Has input
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: results for selected upload -->
        <div class="bg-white rounded-xl shadow-lg p-6 lg:col-span-2 border border-gray-200">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6 pb-4 border-b border-gray-200">
            <div>
              <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Validation Results
              </h2>
              <p v-if="selectedUpload" class="text-sm text-gray-600 break-all mt-1 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                {{ selectedUpload.file_path.split('/').pop() }}
              </p>
            </div>
            <div class="flex items-center gap-4">
              <div v-if="currentUploadResults && currentUploadResults.length" class="text-right px-4 py-2 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                <p class="text-xs text-gray-600 mb-1">Overall Accuracy</p>
                <p class="text-2xl font-bold text-blue-600">
                  {{ (currentUploadResults.reduce((sum, r) => sum + r.accuracy, 0) / currentUploadResults.length * 100).toFixed(2) }}%
                </p>
              </div>
              <button
                v-if="selectedUpload"
                @click="goToUploadDetail"
                class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl font-medium flex items-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                </svg>
                View Detail
              </button>
            </div>
          </div>
          <div v-if="!selectedUpload" class="text-center py-16">
            <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-4">
              <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <p class="text-gray-500 font-medium">Select a file from the left to view validation results</p>
          </div>
          <div v-else-if="loadingResults" class="text-center py-16">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
            <p class="mt-4 text-gray-600">Loading results...</p>
          </div>
          <div v-else-if="currentUploadResults && currentUploadResults.length > 0" class="space-y-4">
            <div class="overflow-x-auto rounded-xl border border-gray-200">
              <table class="w-full border-collapse min-w-[600px]">
                <thead>
                  <tr class="bg-gradient-to-r from-gray-50 to-gray-100">
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">Field</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 min-w-[200px]">User Value</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 min-w-[200px]">OCR Value</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200 w-[120px]">Accuracy</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="r in currentUploadResults" :key="r.field_name" class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-3 font-semibold text-gray-900 align-top">{{ r.field_name }}</td>
                    <td class="px-4 py-3 align-top break-words max-w-[300px]">
                      <div class="text-sm text-gray-700" :title="r.user_value">{{ r.user_value || '-' }}</div>
                    </td>
                    <td class="px-4 py-3 align-top break-words max-w-[300px]">
                      <div class="text-sm text-gray-700" :title="r.ocr_value">{{ r.ocr_value || '-' }}</div>
                    </td>
                    <td class="px-4 py-3 align-top">
                      <span :class="getAccuracyClass(r.accuracy)" class="font-bold text-lg">{{ (r.accuracy * 100).toFixed(2) }}%</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else-if="selectedUpload" class="text-center py-16">
            <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-yellow-100 mb-4">
              <svg class="w-10 h-10 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
            </div>
            <p class="text-gray-600 font-medium mb-2">No validation results found</p>
            <p class="text-sm text-gray-500">Run validation first to see results</p>
          </div>

          <div v-if="selectedUpload" class="mt-8 border-t border-gray-200 pt-6">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
              <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                Desired User Values
              </h3>
              <div class="flex items-center gap-2">
                <button
                  v-if="editingUserValues"
                  @click="cancelEditUserValues"
                  class="px-4 py-2 border border-gray-300 rounded-xl hover:bg-gray-50 transition font-medium"
                >
                  Cancel
                </button>
                <button
                  v-if="!editingUserValues"
                  @click="startEditUserValues"
                  :disabled="userInputLoading"
                  class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 transition-all shadow-md hover:shadow-lg font-medium flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  Edit Values
                </button>
              </div>
            </div>

            <div v-if="userInputLoading" class="text-center py-6">
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
            <div v-else>
              <div v-if="editingUserValues">
                <div v-if="textFields.length || Object.keys(userForm).length" class="space-y-4">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="field in (textFields.length ? textFields : Object.keys(userForm))" :key="field">
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
                    <button @click="cancelEditUserValues" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
                    <button
                      @click="submitUserForm"
                      :disabled="userInputSaving"
                      class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                    >
                      {{ userInputSaving ? 'Saving...' : 'Save Values' }}
                    </button>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-500">No fields available to edit. Upload a sample JSON first.</div>
              </div>
              <div v-else>
                <div v-if="Object.keys(selectedUploadUserInput).length" class="overflow-x-auto">
                  <table class="w-full border-collapse min-w-[480px]">
                    <thead>
                      <tr class="bg-gray-100">
                        <th class="border border-gray-300 px-4 py-2 text-left w-[160px]">Field</th>
                        <th class="border border-gray-300 px-4 py-2 text-left">User Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(val, key) in selectedUploadUserInput" :key="key" class="hover:bg-gray-50">
                        <td class="border border-gray-300 px-4 py-2 font-medium align-top">{{ key }}</td>
                        <td class="border border-gray-300 px-4 py-2 align-top break-words">
                          <div class="text-sm" :title="val">{{ val || '-' }}</div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-sm text-gray-500">No desired values saved yet. Click "Edit Desired Values" to add them.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload + Desired User Values Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="showUploadModal = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto transform transition-all">
        <div class="p-6 border-b border-gray-200 sticky top-0 bg-white z-10">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                Upload File & Desired User Values
              </h2>
              <p class="text-sm text-gray-500 mt-1">Upload a file and enter the expected values</p>
            </div>
            <button @click="showUploadModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Choose PDF/Image
              </label>
              <label class="cursor-pointer block">
                <input type="file" @change="onModalUploadFileChange" accept="application/pdf,image/*" class="hidden" />
                <div class="px-4 py-3 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all flex items-center justify-center gap-2 min-h-[48px]">
                  <svg class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  <span class="text-sm text-gray-600 truncate">{{ modalUploadFile ? modalUploadFile.name : 'Choose PDF or Image file...' }}</span>
                </div>
              </label>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                Expected Field Values
              </label>
              <div class="space-y-3 max-h-[400px] overflow-y-auto">
                <div v-for="field in textFields" :key="field" class="bg-gray-50 rounded-lg p-3">
                  <label class="block text-xs font-semibold text-gray-700 mb-2">{{ field }}</label>
                  <input v-model="modalUserForm[field]" type="text" :placeholder="`Enter ${field}`" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-sm" />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 border-t border-gray-200 flex justify-end gap-3 sticky bottom-0 bg-white">
          <button @click="showUploadModal = false" class="px-6 py-2.5 border border-gray-300 rounded-xl hover:bg-gray-50 transition font-medium">Cancel</button>
          <button @click="submitUploadWithUserForm" class="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl font-medium flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Save & Upload
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
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
const selectedUploadUserInput = ref({})
const uploadResults = ref(null)
const currentUploadResults = ref(null)
const loadingResults = ref(false)
const job = ref(null)
const validating = ref(false)
const userInputLoading = ref(false)
const userInputSaving = ref(false)
const editingUserValues = ref(false)
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
    userInputSaving.value = true
    const json = JSON.stringify(userForm.value)
    const file = new Blob([json], { type: 'application/json' })
    const form = new FormData()
    form.append('form_json', file, 'user_input.json')
    await api.post(`/api/documents/${selectedUploadId.value}/user-input`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadUploads()
    await loadUploadUserInput(selectedUploadId.value)
    editingUserValues.value = false
    alert('User values saved successfully')
  } catch (error) {
    console.error('Failed to submit user form:', error)
    alert('Failed to submit user form')
  } finally {
    userInputSaving.value = false
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
  editingUserValues.value = false
  selectedUploadUserInput.value = {}
}

watch(selectedUpload, async (upload) => {
  if (upload) {
    await loadUploadResults(upload.id)
    await loadUploadUserInput(upload.id)
  } else {
    currentUploadResults.value = null
    selectedUploadUserInput.value = {}
    editingUserValues.value = false
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

async function loadUploadUserInput(uploadId) {
  userInputLoading.value = true
  try {
    const { data } = await api.get(`/api/documents/upload/${uploadId}/user-input`)
    selectedUploadUserInput.value = data
  } catch (error) {
    selectedUploadUserInput.value = {}
    if (error?.response?.status !== 404) {
      console.error('Failed to load user input:', error)
    }
  } finally {
    userInputLoading.value = false
    const fields = textFields.value.length ? textFields.value : Object.keys(selectedUploadUserInput.value)
    const obj = {}
    fields.forEach((field) => {
      obj[field] = selectedUploadUserInput.value[field] ?? ''
    })
    userForm.value = obj
  }
}

function startEditUserValues() {
  const fields = textFields.value.length ? textFields.value : Object.keys(selectedUploadUserInput.value)
  const obj = {}
  fields.forEach((field) => {
    obj[field] = selectedUploadUserInput.value[field] ?? ''
  })
  userForm.value = obj
  editingUserValues.value = true
}

function cancelEditUserValues() {
  editingUserValues.value = false
  const fields = textFields.value.length ? textFields.value : Object.keys(selectedUploadUserInput.value)
  const obj = {}
  fields.forEach((field) => {
    obj[field] = selectedUploadUserInput.value[field] ?? ''
  })
  userForm.value = obj
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

function goToUploadDetail() {
  if (!selectedUpload.value) return
  router.push({ name: 'upload-detail', params: { documentId, uploadId: selectedUpload.value.id } })
}

async function exportExcel() {
  try {
    const response = await api.get(`/api/documents/${documentId}/export-excel`, {
      responseType: 'blob'
    })
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = window.document.createElement('a')
    link.href = url
    const filename = response.headers['content-disposition']
      ? response.headers['content-disposition'].split('filename=')[1].replace(/"/g, '')
      : `report_${document.value?.name || 'document'}_${new Date().toISOString().split('T')[0]}.xlsx`
    link.setAttribute('download', filename)
    window.document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export Excel:', error)
    alert('Failed to export Excel report')
  }
}

onMounted(async () => {
  await loadDocument()
  await loadUploads()
  await loadTextFields()
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})
</script>

