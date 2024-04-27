import '@/styles/index.scss'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { createApp } from 'vue'
import { store } from '@/stores'
import theme from '@/theme'
import directives from '@/directives'
import App from './App.vue'
import router from '@/router'
import Components from '@/components'
import i18n from './locales';
const app = createApp(App)
app.use(store)
app.use(directives)

for (const [key, component] of Object.entries(ElementPlusIcons)) {
  app.component(key, component)
}
app.use(ElementPlus, {
  locale: zhCn
})

app.use(theme)

app.use(router)
app.use(i18n);
app.use(Components)
app.mount('#app')
