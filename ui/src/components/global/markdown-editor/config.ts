/** 配置 Markdown 编辑器的本地扩展、内容过滤和繁体中文语言包。 */

import ZH_TW from '@vavt/cm-extension/dist/locale/zh-TW'
import Cropper from 'cropperjs'
import * as echarts from 'echarts'
import highlight from 'highlight.js'
import katex from 'katex'
import mermaid from 'mermaid'
import { config, XSSPlugin } from 'md-editor-v3'
import * as prettierMarkdownPlugin from 'prettier/plugins/markdown'
import * as prettier from 'prettier/standalone'
import screenfull from 'screenfull'
import { supPopover } from './sup-popover'
import 'cropperjs/dist/cropper.css'
import 'highlight.js/styles/atom-one-dark.css'
import 'katex/dist/katex.min.css'
import './md-editor.scss'

let configured = false

/** 在应用挂载前注册本地扩展，避免 Markdown 编辑器运行时加载 CDN 资源。 */
export function configureMarkdownEditor() {
  if (configured) return

  config({
    editorConfig: {
      languageUserDefined: {
        'zh-Hant': ZH_TW,
        'zh-TW': ZH_TW,
      },
    },
    editorExtensions: {
      cropper: { instance: Cropper },
      echarts: { instance: echarts },
      highlight: { instance: highlight },
      katex: { instance: katex },
      mermaid: { instance: mermaid },
      prettier: {
        parserMarkdownInstance: prettierMarkdownPlugin,
        prettierInstance: prettier,
      },
      screenfull: { instance: screenfull },
    },
    markdownItPlugins(plugins) {
      return [
        ...plugins,
        {
          type: 'xss',
          plugin: XSSPlugin,
          options: {
            extendedWhiteList: {
              a: ['href', 'style'],
              iframe: ['allow', 'allowfullscreen', 'border', 'class', 'frameborder', 'framespacing', 'height', 'src', 'title', 'width'],
              input: ['checked', 'class', 'disabled', 'type'],
              source: ['src', 'type'],
              sup: ['data-title'],
              video: ['controls', 'height', 'playsinline', 'preload', 'src', 'width'],
            },
            xss: {
              onTagAttr(tag: string, name: string, value: string) {
                if (tag !== 'video') return undefined
                if (name === 'autoplay') return ''
                if (name === 'preload' && !['none', 'metadata'].includes(value)) return 'preload="metadata"'
                return undefined
              },
            },
          },
        },
      ]
    },
  })

  supPopover.init()
  configured = true
}
