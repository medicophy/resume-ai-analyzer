<script setup lang="ts">
import AppIcon from '../ui/AppIcon'

withDefaults(defineProps<{ onDark?: boolean; size?: 'md' | 'sm' }>(), { onDark: true, size: 'md' })
</script>

<template>
  <span class="inline-flex items-center gap-2.5">
    <AppIcon name="lens" :size="size === 'md' ? 30 : 26" :class="onDark ? 'text-mark' : 'text-accent'" />
    <span
      class="font-display font-bold tracking-[-0.01em]"
      :class="[size === 'md' ? 'text-xl' : 'text-[19px]', onDark ? 'text-on-bar-1' : 'text-ink']"
    >Hire<span class="font-semibold" :class="onDark ? 'text-lens' : 'text-accent'">Lens</span></span>
  </span>
</template>
