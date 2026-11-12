import { createApp } from 'vue'
import ElementPlus from 'element-plus'

import App from './App.vue'
import { configureMarkdownEditor } from '@/components/global/markdown-editor/config'
import router from '@/router/admin'
import { pinia, useStore } from '@/stores/admin'
import { createAppI18n } from '@/locales'
import permission from '@/permission/install'
import '@/styles/tailwind.css'
import '@/styles/index.scss'

configureMarkdownEditor()

const app = createApp(App)

app.use(pinia)
app.use(createAppI18n(useStore().user))
app.use(router)
app.use(permission)
app.use(ElementPlus)

app.mount('#app')
