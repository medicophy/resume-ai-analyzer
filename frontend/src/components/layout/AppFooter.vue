<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AppIcon from '../ui/AppIcon'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="no-print border-t border-bar-line bg-bar">
    <div class="container-page flex flex-wrap items-center justify-between gap-x-6 gap-y-3 py-5 text-[13px] text-on-bar-3">
      <p class="flex items-center gap-2">
        <AppIcon name="lock" :size="14" />
        Files are processed in memory and never stored.
      </p>
      <nav aria-label="Footer" class="flex flex-wrap gap-x-5 gap-y-2">
        <RouterLink to="/how-it-works" class="text-on-bar-2 hover:text-on-bar-1">How scoring works</RouterLink>
        <RouterLink to="/privacy" class="text-on-bar-2 hover:text-on-bar-1">Privacy</RouterLink>
        <a href="https://github.com/medicophy/resume-ai-analyzer" target="_blank" rel="noopener noreferrer" class="text-on-bar-2 hover:text-on-bar-1">Source on GitHub</a>
      </nav>
      <p>
        © {{ year }} HireLens · Built by
        <a href="https://github.com/medicophy" target="_blank" rel="noopener noreferrer" class="font-semibold text-on-bar-1 hover:underline">Medicophy</a>
      </p>
    </div>
  </footer>
</template>
