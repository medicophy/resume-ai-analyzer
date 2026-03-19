import { createApp } from 'vue'
import './style.css'
import App from './App.vue' // We will turn App.vue BACK into the root wrapper temporarily to test
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')