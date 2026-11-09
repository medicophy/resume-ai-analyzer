<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppFooter from './components/layout/AppFooter.vue'
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-4 focus:py-2 focus:text-ink">Skip to content</a>
  <div class="flex min-h-dvh flex-col">
    <AppHeader />
    <main id="main" class="flex flex-1 flex-col">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>
