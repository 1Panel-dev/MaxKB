import { createApp } from 'vue';
import App from './App.vue';
import Vue3Menus from '../package/index'

const app = createApp(App)
app.use(Vue3Menus)
app.mount('#app')
