<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- Simple Header for this page -->
    <header class="bg-white border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <button @click="goHome" class="flex items-center gap-2 text-slate-600 hover:text-blue-600 transition-colors font-medium">
          <span>←</span> Back to Analyzer
        </button>
        <span class="text-lg font-bold text-slate-800">How It Works</span>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow py-16 px-4 sm:px-6 lg:px-8">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-4xl font-extrabold text-slate-900 mb-6">
          How Resume AI Analyzer Works
        </h1>
        <p class="text-lg text-slate-600 mb-16 max-w-2xl mx-auto">
          We use advanced Natural Language Processing (NLP) right in your browser and local backend to ensure your resume matches the job description perfectly. No data leaves your device.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
          <!-- Step 1 -->
          <div class="relative group">
            <div class="w-20 h-20 mx-auto bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center text-4xl mb-6 shadow-sm group-hover:scale-110 transition-transform duration-300">
              📄
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-3">1. Upload Securely</h3>
            <p class="text-slate-600 leading-relaxed">
              Drag and drop your PDF. Our Python backend uses PyMuPDF to extract text locally. Your file is processed in memory and never stored on any server.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="relative group">
            <div class="w-20 h-20 mx-auto bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center text-4xl mb-6 shadow-sm group-hover:scale-110 transition-transform duration-300">
              🧠
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-3">2. AI Analysis</h3>
            <p class="text-slate-600 leading-relaxed">
              We convert both your resume and the job description into mathematical vectors using TF-IDF. This allows the AI to understand context, not just keyword matching.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="relative group">
            <div class="w-20 h-20 mx-auto bg-green-100 text-green-600 rounded-2xl flex items-center justify-center text-4xl mb-6 shadow-sm group-hover:scale-110 transition-transform duration-300">
              📊
            </div>
            <h3 class="text-xl font-bold text-slate-800 mb-3">3. Get Optimized</h3>
            <p class="text-slate-600 leading-relaxed">
              Receive an instant match score and a curated list of missing keywords. Update your resume and re-upload to see your score improve in real-time.
            </p>
          </div>
        </div>

        <!-- CTA Section -->
        <div class="mt-20 bg-white rounded-3xl p-8 shadow-xl border border-slate-100">
          <h2 class="text-2xl font-bold text-slate-800 mb-4">Ready to optimize your resume?</h2>
          <button @click="goHome" class="px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold shadow-lg shadow-blue-500/30 hover:bg-blue-700 hover:-translate-y-1 transition-all">
            Start Analyzing Now
          </button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-8 border-t border-slate-200 bg-white mt-auto">
      <div class="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm">
        &copy; {{ new Date().getFullYear }} Resume AI Analyzer. All rights reserved.
      </div>
    </footer>
  </div>
</template>