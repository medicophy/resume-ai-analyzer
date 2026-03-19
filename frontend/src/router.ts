import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from './components/MainLayout.vue'
import HomeContent from './App.vue'
import HowItWorks from './views/HowItWorks.vue'

const routes = [
    {
        path: '/',
        component: MainLayout,
        children: [
            { path: '', component: HomeContent } // Default child
        ]
    },
    {
        path: '/how-it-works',
        component: MainLayout,
        children: [
            { path: '', component: HowItWorks }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router