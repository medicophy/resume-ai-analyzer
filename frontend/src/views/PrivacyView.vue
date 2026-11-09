<script setup lang="ts">
import { RouterLink } from 'vue-router'

const points = [
  { title: 'Your file is never stored', text: 'Your resume is read in memory to produce the report and discarded as soon as the response is sent. There is no database and no file storage.' },
  { title: 'Your report stays in your browser', text: "The report is kept in this browser tab so it survives a page refresh. It is deleted when you close the tab. The resume file itself isn't kept, even in the browser." },
  { title: 'AI suggestions only when you ask', text: 'If you click "Get AI suggestions", the resume text, with email addresses, phone numbers and links removed, and the job posting are sent to Groq to generate the suggestions. Nothing is sent to Groq otherwise.' },
  { title: 'No accounts, no analytics', text: 'There is no sign-up, no analytics and no advertising. The hosting provider keeps standard request logs (time and network address), and server error logs may include the file name, never its contents.' },
]
</script>

<template>
  <div class="container-page max-w-[880px] py-10">
    <h1 class="font-display text-[34px] font-bold tracking-[-0.02em] text-ink">Privacy</h1>
    <p class="mt-3 text-[17px] leading-relaxed text-text-2">A resume is personal. Here is exactly what happens to yours.</p>

    <ul class="mt-8 grid gap-4 sm:grid-cols-2">
      <li v-for="p in points" :key="p.title" class="card p-6">
        <h2 class="text-[16px] font-semibold text-ink">{{ p.title }}</h2>
        <p class="mt-2 text-[15px] leading-relaxed text-text-2">{{ p.text }}</p>
      </li>
    </ul>

    <p class="mt-8 text-[15px] text-text-2">
      The source code is public:
      <a href="https://github.com/medicophy/resume-ai-analyzer" target="_blank" rel="noopener noreferrer" class="btn-link">github.com/medicophy/resume-ai-analyzer</a>
    </p>
    <RouterLink to="/" class="btn-primary mt-8 h-12">Analyze a resume</RouterLink>
  </div>
</template>
