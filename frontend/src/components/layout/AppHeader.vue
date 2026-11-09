<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useTheme } from '../../composables/useTheme'
import AppIcon from '../ui/AppIcon'
import BrandLogo from './BrandLogo.vue'

const route = useRoute()
const { theme, toggle } = useTheme()
const menuOpen = ref(false)
const onResults = computed(() => route.name === 'results')

watch(() => route.fullPath, () => (menuOpen.value = false))

const links = [
  { to: '/', label: 'Analyze' },
  { to: '/how-it-works', label: 'How scoring works' },
  { to: '/privacy', label: 'Privacy' },
]
</script>

<template>
  <header class="no-print sticky top-0 z-30 border-b border-bar-line bg-bar">
    <div class="container-page flex h-16 items-center justify-between gap-4">
      <RouterLink to="/" aria-label="HireLens home" class="shrink-0">
        <BrandLogo />
      </RouterLink>

      <nav aria-label="Main" class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="rounded-lg px-3.5 py-2 text-sm font-medium text-on-bar-2 transition-colors hover:bg-white/5 hover:text-on-bar-1"
          exact-active-class="!bg-white/10 !text-white !font-semibold"
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="flex h-10 w-10 items-center justify-center rounded-[10px] border border-white/15 bg-white/5 text-on-bar-1 transition-colors hover:bg-white/10"
          :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggle"
        >
          <AppIcon :name="theme === 'dark' ? 'sun' : 'moon'" />
        </button>
        <RouterLink
          v-if="onResults"
          to="/"
          class="hidden h-10 items-center gap-2 rounded-[10px] bg-mark px-4 text-sm font-semibold text-bar transition-opacity hover:opacity-90 sm:inline-flex"
        >
          <AppIcon name="plus" :size="16" :stroke-width="2.2" />
          New analysis
        </RouterLink>
        <a
          v-else
          href="https://github.com/medicophy/resume-ai-analyzer"
          target="_blank"
          rel="noopener noreferrer"
          class="hidden h-10 items-center gap-2 rounded-[10px] border border-white/15 bg-white/5 px-3.5 text-sm font-medium text-on-bar-1 transition-colors hover:bg-white/10 sm:inline-flex"
        >
          GitHub
          <AppIcon name="external" :size="15" />
        </a>
        <button
          type="button"
          class="flex h-10 w-10 items-center justify-center rounded-[10px] border border-white/15 bg-white/5 text-on-bar-1 md:hidden"
          :aria-expanded="menuOpen"
          aria-controls="mobile-menu"
          :aria-label="menuOpen ? 'Close menu' : 'Open menu'"
          @click="menuOpen = !menuOpen"
        >
          <AppIcon :name="menuOpen ? 'x' : 'menu'" :size="20" />
        </button>
      </div>
    </div>

    <nav v-if="menuOpen" id="mobile-menu" aria-label="Main" class="border-t border-bar-line px-4 pb-4 pt-2 md:hidden">
      <RouterLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="block rounded-lg px-3 py-3 text-[15px] font-medium text-on-bar-2"
        exact-active-class="!bg-white/10 !text-white"
      >
        {{ link.label }}
      </RouterLink>
      <RouterLink v-if="onResults" to="/" class="mt-2 flex h-11 items-center justify-center gap-2 rounded-[10px] bg-mark text-sm font-semibold text-bar">
        <AppIcon name="plus" :size="16" /> New analysis
      </RouterLink>
    </nav>
  </header>
</template>
