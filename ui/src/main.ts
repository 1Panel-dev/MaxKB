import 'nprogress/nprogress.css'
import '@/styles/index.scss'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import { createApp } from 'vue'
import { store } from '@/stores'
import theme from '@/theme'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(store)
const ElementPlusIconsVue: object = ElementPlusIcons
// 将elementIcon放到全局
app.config.globalProperties.$antIcons = ElementPlusIconsVue
app.use(ElementPlus)

app.use(theme)

app.use(router)

app.mount('#app')
