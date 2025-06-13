import '@/styles/index.scss'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enUs from 'element-plus/es/locale/lang/en'
import zhTW from 'element-plus/es/locale/lang/zh-tw'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from '@/router/chat'
import i18n from '@/locales'
import Components from '@/components'
import directives from '@/directives'

import { config } from 'md-editor-v3'
import screenfull from 'screenfull'

import katex from 'katex'
import 'katex/dist/katex.min.css'

import Cropper from 'cropperjs'

import mermaid from 'mermaid'

import highlight from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

config({
  editorExtensions: {
    highlight: {
      instance: highlight,
    },
    screenfull: {
      instance: screenfull,
    },
    katex: {
      instance: katex,
    },
    cropper: {
      instance: Cropper,
    },
    mermaid: {
      instance: mermaid,
    },
  },
})
const app = createApp(App)
app.use(createPinia())
for (const [key, component] of Object.entries(ElementPlusIcons)) {
  app.component(key, component)
}
const locale_map: any = {
  'zh-CN': zhCn,
  'zh-Hant': zhTW,
  'en-US': enUs,
}
app.use(ElementPlus, {
  locale: locale_map[localStorage.getItem('MaxKB-locale') || navigator.language || 'en-US'],
})
app.use(directives)
app.use(router)
app.use(i18n)
app.use(Components)
app.mount('#app')
export { app }
