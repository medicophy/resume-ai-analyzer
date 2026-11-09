import { createRouter, createWebHistory } from 'vue-router'
import { analysis } from './stores/analysis'
import HomeView from './views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: 'HireLens · Check your resume against a job' } },
    {
      path: '/results',
      name: 'results',
      component: () => import('./views/ResultsView.vue'),
      meta: { title: 'Your report · HireLens' },
      // Without a report (new tab, or the tab was closed) there is nothing to show.
      beforeEnter: () => (analysis.state.result ? true : { name: 'home' }),
    },
    { path: '/how-it-works', name: 'how', component: () => import('./views/HowItWorksView.vue'), meta: { title: 'How scoring works · HireLens' } },
    { path: '/privacy', name: 'privacy', component: () => import('./views/PrivacyView.vue'), meta: { title: 'Privacy · HireLens' } },
    { path: '/:pathMatch(.*)*', redirect: { name: 'home' } },
  ],
  scrollBehavior(to, _from, saved) {
    if (saved) return saved
    if (to.hash) return { el: to.hash, top: 88, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.afterEach((to) => {
  document.title = (to.meta.title as string | undefined) ?? 'HireLens'
})

export default router
