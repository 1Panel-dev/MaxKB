import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from '@/router/admin'
import { pinia } from '@/stores'
import permission from '@/permission/install'
import '@/styles/tailwind.css'
import '@/styles/index.scss'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(permission)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
