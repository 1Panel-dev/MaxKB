import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import { configureMarkdownEditor } from '@/components/global/markdown-editor/config'
import App from './App.vue'
import { createAppI18n } from '@/locales'
import router from '@/router/chat'
import { pinia, useStore } from '@/stores/chat'
import { configureElementPlus } from '@/utils/element-plus'
import 'element-plus/dist/index.css'
import '@/styles/tailwind.css'
import '@/styles/index.scss'

configureMarkdownEditor()

configureElementPlus()

const app = createApp(App)

app.use(pinia)
app.use(createAppI18n(useStore().user, null))
app.use(router)
app.use(ElementPlus)

app.mount('#app')
