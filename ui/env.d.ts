/// <reference types="vite/client" />
declare module 'element-plus/dist/locale/zh-cn.mjs'
declare module 'element-plus/dist/locale/en.mjs'
declare module 'element-plus/dist/locale/zh-tw.mjs'
declare module 'markdown-it-task-lists'
declare module 'markdown-it-abbr'
declare module 'markdown-it-anchor'
declare module 'markdown-it-footnote'
declare module 'markdown-it-sub'
declare module 'markdown-it-sup'
declare module 'markdown-it-toc-done-right'
declare module 'katex'
interface Window {
  sendMessage: ?((message: string, other_params_data: any) => void)
}
interface ImportMeta {
  readonly env: ImportMetaEnv
}
declare type Recordable<T = any> = Record<string, T>
