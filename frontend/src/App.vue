<script setup lang="ts">
import { ref } from 'vue'

const resumeFile = ref<File | null>(null)
const jobDescription = ref('')
const isUploading = ref(false)
const result = ref<any>(null)

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    resumeFile.value = target.files[0]
  }
}

const analyzeResume = async () => {
  if (!resumeFile.value || !jobDescription.value) {
    alert('Please upload a resume and enter a job description.')
    return
  }

  isUploading.value = true
  result.value = null

  const formData = new FormData()
  // Ensure 'file' matches the FastAPI parameter name
  formData.append('file', resumeFile.value)
  // Ensure 'job_description' matches the FastAPI parameter name EXACTLY
  formData.append('job_description', jobDescription.value)

  // Debug: Log what we are sending (Check console in browser F12)
  console.log("Sending File:", resumeFile.value.name)
  console.log("Sending JD Length:", jobDescription.value.length)
  console.log("FormData entries:", Array.from(formData.entries()))

  try {
    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      body: formData,
      // Do NOT set Content-Type header manually! 
      // The browser sets it automatically with the boundary for FormData.
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Analysis failed')
    }
    
    result.value = data
  } catch (error: any) {
    console.error(error)
    alert(`Error: ${error.message}`)
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <h1 class="text-3xl font-bold text-center text-gray-900 mb-8">
        Smart Resume Analyzer
      </h1>

      <!-- Input Section -->
      <div class="bg-white shadow rounded-lg p-6 mb-6 space-y-6">
        
        <!-- File Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Upload Resume (PDF)</label>
          <input 
            type="file" 
            accept=".pdf" 
            @change="handleFileChange"
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p v-if="resumeFile" class="mt-2 text-sm text-green-600">Selected: {{ resumeFile.name }}</p>
        </div>

        <!-- Job Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
          <textarea 
            v-model="jobDescription"
            rows="6"
            class="shadow-sm block w-full focus:ring-blue-500 focus:border-blue-500 sm:text-sm border border-gray-300 rounded-md p-3"
            placeholder="Paste the job description here..."
          ></textarea>
        </div>

        <!-- Submit Button -->
        <button 
          @click="analyzeResume"
          :disabled="isUploading"
          class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ isUploading ? 'Analyzing...' : 'Analyze Resume' }}
        </button>
      </div>

      <!-- Results Section -->
      <div v-if="result" class="bg-white shadow rounded-lg p-6 animate-fade-in">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Analysis Results</h2>
        
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div class="bg-blue-50 p-4 rounded-md">
            <p class="text-sm text-blue-600 font-medium">Match Score</p>
            <p class="text-2xl font-bold text-blue-900">{{ result.match_score }}%</p>
          </div>
          <div class="bg-gray-50 p-4 rounded-md">
            <p class="text-sm text-gray-600 font-medium">Resume Length</p>
            <p class="text-2xl font-bold text-gray-900">{{ result.char_count }} chars</p>
          </div>
        </div>

        <div v-if="result.missing_keywords && result.missing_keywords.length > 0">
          <p class="text-sm font-medium text-gray-700 mb-2">Missing Keywords:</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="keyword in result.missing_keywords" :key="keyword" class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
              {{ keyword }}
            </span>
          </div>
        </div>
        
        <div v-else class="text-sm text-gray-500">No missing keywords detected (or logic pending).</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Simple fade-in animation */
.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>