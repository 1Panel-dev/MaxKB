import { createApp } from 'vue'
import ElementPlus from 'element-plus'
// 路由必须先于其他本地模块加载：权限模块经 resource-context 依赖路由，而路由模块在顶层读取 perm；
// 权限先加载会形成循环依赖，路由模块执行时 perm 尚未初始化。本注释同时作为导入排序边界，勿移动。
import router from '@/router/admin'
import { configureMarkdownEditor } from '@/components/global/markdown-editor/config'
import App from './App.vue'
import { createAppI18n } from '@/locales'
import permission from '@/permission/install'
import { pinia, useStore } from '@/stores/admin'
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
