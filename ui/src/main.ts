import '@/styles/index.scss'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { createApp } from 'vue'
import { store } from '@/stores'
import directives from '@/directives'
import App from './App.vue'
import router from '@/router'
import Components from '@/components'
import i18n from './locales'
import { config } from 'md-editor-v3'

import screenfull from 'screenfull'

import katex from 'katex'
import 'katex/dist/katex.min.css'

import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'

import mermaid from 'mermaid'

import highlight from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

config({
  editorExtensions: {
    highlight: {
      instance: highlight
    },
    screenfull: {
      instance: screenfull
    },
    katex: {
      instance: katex
    },
    cropper: {
      instance: Cropper
    },
    mermaid: {
      instance: mermaid
    }
  }
})

const app = createApp(App)
app.use(store)
app.use(directives)

for (const [key, component] of Object.entries(ElementPlusIcons)) {
  app.component(key, component)
}
app.use(ElementPlus, {
  locale: zhCn
})

app.use(router)
app.use(i18n)
app.use(Components)
app.mount('#app')
export { app }
