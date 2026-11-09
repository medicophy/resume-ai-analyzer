<script setup lang="ts">
import AppIcon, { type IconName } from '../ui/AppIcon'

defineProps<{ icon: IconName; title: string; headingId: string }>()
</script>

<template>
  <div class="mb-5 flex flex-wrap items-center gap-3">
    <span class="section-icon"><AppIcon :name="icon" /></span>
    <h2 :id="headingId" class="text-[19px] font-semibold text-ink">{{ title }}</h2>
    <div class="ml-auto flex items-center gap-3"><slot /></div>
  </div>
</template>
