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

// Add this new ref for the copy button
const copied = ref(false)

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

// Add this function
const copyKeywords = () => {
  if (!result.value?.missing_keywords) return
  const text = result.value.missing_keywords.join(', ')
  navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

const handleDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    if (file.type === 'application/pdf') {
      resumeFile.value = file
    } else {
      alert('Please drop a PDF file.')
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100">
    
    <!-- 1. Glassmorphism Header -->
    <header class="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🚀</span>
          <h1 class="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Resume AI Analyzer
          </h1>
        </div>
        <nav class="hidden md:flex gap-6 text-sm font-medium text-slate-600">
          <a href="#" class="hover:text-blue-600 transition-colors">How it Works</a>
          <a href="#" class="hover:text-blue-600 transition-colors">Privacy</a>
          <a href="#" class="hover:text-blue-600 transition-colors">GitHub</a>
        </nav>
      </div>
    </header>

    <!-- 2. Main Content Grid -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">
        
        <!-- LEFT COLUMN: Input Section (Spans 5/12 on large screens) -->
        <!-- LEFT COLUMN: Input Section -->
        <section class="lg:col-span-5 space-y-6">
          <div class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-6 border border-slate-100">
            <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <span class="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs">1</span>
              Upload & Describe
            </h2>
            
            <div class="space-y-5">
              
              <!-- File Upload Zone -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Upload Resume (PDF)</label>
                <div 
                  class="relative group cursor-pointer"
                  @dragover.prevent
                  @drop.prevent="handleDrop"
                >
                  <input 
                    type="file" 
                    accept=".pdf" 
                    @change="handleFileChange"
                    class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                  <div class="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center transition-colors group-hover:border-blue-400 group-hover:bg-blue-50/50">
                    <div class="text-3xl mb-2">📄</div>
                    <p class="text-sm text-slate-600 font-medium">
                      {{ resumeFile ? resumeFile.name : 'Click or drag PDF here' }}
                    </p>
                    <p v-if="!resumeFile" class="text-xs text-slate-400 mt-1">Supported format: .pdf</p>
                    <p v-else class="text-xs text-green-600 mt-1 font-semibold">Ready to upload</p>
                  </div>
                </div>
              </div>

              <!-- Job Description Input -->
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-2">Job Description</label>
                <textarea 
                  v-model="jobDescription"
                  rows="8"
                  class="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all resize-none text-slate-700 placeholder:text-slate-400"
                  placeholder="Paste the full job description here..."
                ></textarea>
                <div class="flex justify-between mt-1">
                  <span class="text-xs text-slate-400">{{ jobDescription.length }} chars</span>
                  <span v-if="jobDescription.length > 50" class="text-xs text-green-600 font-medium">Good length</span>
                </div>
              </div>

              <!-- Analyze Button -->
              <button 
                @click="analyzeResume"
                :disabled="isUploading || !resumeFile || !jobDescription"
                class="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:shadow-none flex items-center justify-center gap-2"
              >
                <span v-if="isUploading">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </span>
                <span v-else>Analyze Resume</span>
              </button>
              
              <p v-if="!resumeFile || !jobDescription" class="text-xs text-center text-slate-400">
                Please upload a file and enter a description to start.
              </p>
            </div>
          </div>
        </section>

        <!-- RIGHT COLUMN: Results Section (Spans 7/12 on large screens) -->
                <!-- RIGHT COLUMN: Results Section -->
        <section class="lg:col-span-7 space-y-6">
          <div class="bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-6 border border-slate-100 min-h-[400px] relative overflow-hidden">
            <h2 class="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
              <span class="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 text-xs">2</span>
              AI Analysis Results
            </h2>

            <!-- STATE 1: Loading Skeleton -->
            <div v-if="isUploading" class="space-y-6 animate-pulse">
              <div class="flex justify-center">
                <div class="w-40 h-40 bg-slate-200 rounded-full"></div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div class="h-24 bg-slate-200 rounded-xl"></div>
                <div class="h-24 bg-slate-200 rounded-xl"></div>
              </div>
              <div class="space-y-2">
                <div class="h-4 bg-slate-200 rounded w-1/3"></div>
                <div class="flex gap-2">
                  <div class="h-8 w-20 bg-slate-200 rounded-full"></div>
                  <div class="h-8 w-24 bg-slate-200 rounded-full"></div>
                  <div class="h-8 w-16 bg-slate-200 rounded-full"></div>
                </div>
              </div>
            </div>

            <!-- STATE 2: Empty State (Initial) -->
            <div v-else-if="!result" class="h-full flex flex-col items-center justify-center text-slate-400 py-12">
              <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-2xl">
                📊
              </div>
              <p class="font-medium">Upload a resume to see analysis</p>
              <p class="text-sm mt-1">Results will appear here instantly</p>
            </div>

            <!-- STATE 3: Results Content -->
            <div v-else class="space-y-8 animate-fade-in-up">
              
              <!-- Top Row: Gauge & Main Stat -->
              <div class="flex flex-col sm:flex-row items-center justify-around gap-6">
                <!-- Circular Gauge -->
                <div class="relative w-40 h-40">
                  <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <!-- Background Circle -->
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#e2e8f0" stroke-width="8" />
                    <!-- Progress Circle -->
                    <circle 
                      cx="50" cy="50" r="45" fill="none" 
                      :stroke="result.match_score > 70 ? '#10b981' : result.match_score > 40 ? '#f59e0b' : '#ef4444'" 
                      stroke-width="8" 
                      stroke-linecap="round"
                      :stroke-dasharray="283"
                      :stroke-dashoffset="283 - (283 * result.match_score) / 100"
                      class="transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div class="absolute inset-0 flex flex-col items-center justify-center">
                    <span class="text-3xl font-bold text-slate-800">{{ result.match_score }}%</span>
                    <span class="text-xs text-slate-500 uppercase font-semibold tracking-wide">Match</span>
                  </div>
                </div>

                <!-- Quick Stats -->
                <div class="grid grid-cols-2 gap-4 w-full sm:w-auto">
                  <div class="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                    <p class="text-xs text-slate-500 uppercase font-semibold">Resume Length</p>
                    <p class="text-xl font-bold text-slate-800">{{ Math.round(result.char_count / 1000) }}k</p>
                    <p class="text-[10px] text-slate-400">chars</p>
                  </div>
                  <div class="bg-slate-50 p-4 rounded-xl border border-slate-100 text-center">
                    <p class="text-xs text-slate-500 uppercase font-semibold">Missing</p>
                    <p class="text-xl font-bold text-red-500">{{ result.missing_keywords?.length || 0 }}</p>
                    <p class="text-[10px] text-slate-400">keywords</p>
                  </div>
                </div>
              </div>

              <!-- Missing Keywords Section -->
              <div class="bg-slate-50 rounded-xl p-5 border border-slate-100">
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-sm font-semibold text-slate-700">Missing Keywords</h3>
                  <button @click="copyKeywords" class="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1">
                    <span v-if="copied">Copied!</span>
                    <span v-else>Copy All</span>
                  </button>
                </div>
                
                <div v-if="result.missing_keywords && result.missing_keywords.length > 0" class="flex flex-wrap gap-2">
                  <span 
                    v-for="(word, index) in result.missing_keywords" 
                    :key="index"
                    class="px-3 py-1.5 bg-white border border-red-100 text-red-600 text-sm font-medium rounded-lg shadow-sm hover:border-red-300 transition-colors cursor-default"
                  >
                    {{ word }}
                  </span>
                </div>
                <div v-else class="text-sm text-green-600 font-medium flex items-center gap-2">
                  <span class="text-lg">✅</span> No critical missing keywords detected!
                </div>
              </div>

              <!-- Preview Snippet -->
              <div class="pt-4 border-t border-slate-100">
                <p class="text-xs text-slate-400 uppercase font-semibold mb-2">Extracted Preview</p>
                <p class="text-sm text-slate-600 line-clamp-3 italic">
                  "{{ result.resume_preview }}"
                </p>
              </div>

            </div>
          </div>
        </section>
        
      </div>
      
      <!-- Optional: How it Works Section (Below Grid) -->
      <section class="mt-20 py-16 border-t border-slate-200">
        <div class="text-center mb-12">
          <h3 class="text-2xl font-bold text-slate-800 mb-3">How It Works</h3>
          <p class="text-slate-600 max-w-xl mx-auto">
            Our local AI engine uses advanced NLP techniques to analyze your resume in seconds, ensuring you never miss a critical keyword.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <!-- Step 1 -->
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 text-center hover:shadow-md transition-shadow">
            <div class="w-14 h-14 mx-auto bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-2xl mb-4">
              📄
            </div>
            <h4 class="font-semibold text-slate-800 mb-2">1. Upload Resume</h4>
            <p class="text-sm text-slate-500 leading-relaxed">
              Drag and drop your PDF resume. We extract text locally without uploading your data to any cloud server.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 text-center hover:shadow-md transition-shadow">
            <div class="w-14 h-14 mx-auto bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-2xl mb-4">
              📝
            </div>
            <h4 class="font-semibold text-slate-800 mb-2">2. Paste Job Description</h4>
            <p class="text-sm text-slate-500 leading-relaxed">
              Copy the job description from the career page. Our algorithm identifies key skills and requirements instantly.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 text-center hover:shadow-md transition-shadow">
            <div class="w-14 h-14 mx-auto bg-green-100 text-green-600 rounded-full flex items-center justify-center text-2xl mb-4">
              🚀
            </div>
            <h4 class="font-semibold text-slate-800 mb-2">3. Get Instant Feedback</h4>
            <p class="text-sm text-slate-500 leading-relaxed">
              Receive a match score and a list of missing keywords to optimize your resume before applying.
            </p>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="mt-20 py-8 border-t border-slate-200 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-xl">🚀</span>
            <span class="text-sm font-semibold text-slate-700">Resume AI Analyzer</span>
          </div>
          
          <p class="text-sm text-slate-500 text-center md:text-right">
            &copy; {{ new Date().getFullYear }} Built with Vue 3 & FastAPI. 
            <span class="hidden md:inline">|</span> 
            <br class="md:hidden" />
            <span class="text-xs">100% Local Processing. No Data Stored.</span>
          </p>
        </div>
      </footer>
      
    </main>
  </div>

</template>

<style scoped>
/* Simple fade-in animation */
.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>