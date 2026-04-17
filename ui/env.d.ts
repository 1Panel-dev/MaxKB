/// <reference types="vite/client" />
declare module 'katex'
declare module 'pdfjs-dist/build/pdf.mjs'
interface Window {
  sendMessage: ?((message: string, other_params_data: any) => void)
  chatUserProfile: ?(() => any)
  MaxKB: {
    prefix: string
    chatPrefix: string
  }
}
