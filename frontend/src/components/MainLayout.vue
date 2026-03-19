<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100 flex flex-col">
    
    <!-- Global Header -->
    <header class="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-2 group">
          <span class="text-2xl group-hover:scale-110 transition-transform">🚀</span>
          <h1 class="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Resume AI Analyzer
          </h1>
        </router-link>
        
        <nav class="flex gap-6 text-sm font-medium text-slate-600">
          <router-link to="/how-it-works" class="hover:text-blue-600 transition-colors cursor-pointer">
            How it Works
          </router-link>
          <a href="https://github.com" target="_blank" class="hover:text-blue-600 transition-colors">GitHub</a>
        </nav>
      </div>
    </header>

    <!-- Page Content Swaps Here -->
        <main class="flex-grow bg-yellow-50 border-2 border-dashed border-yellow-300 p-10">
      <!-- Temporary Debug Text -->
      <div class="text-center text-yellow-800 font-bold mb-4">
        DEBUG: MainLayout Loaded. Current Route: {{ $route.path }}
      </div>
      
      <router-view />
      
      <!-- Fallback if router-view is empty -->
      <div v-if="$route.matched.length === 0" class="text-center text-red-500 mt-10">
        No component matched this route. Check router.ts
      </div>
    </main>

    <!-- Global Footer -->
    <footer class="py-8 border-t border-slate-200 bg-white mt-auto">
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
  </div>
</template>