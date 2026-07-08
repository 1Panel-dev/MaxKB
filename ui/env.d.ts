/// <reference types="vite/client" />
declare module 'katex'
declare module 'pdfjs-dist/build/pdf.mjs'
declare module 'sanitize-html' {
  interface IOptions {
    allowedTags?: string[]
    allowedAttributes?: Record<string, string[]>
    allowedSchemes?: string[]
    allowedSchemesByTag?: Record<string, string[]>
    allowProtocolRelative?: boolean
  }

  function sanitizeHtml(dirty: string, options?: IOptions): string

  export = sanitizeHtml
}
interface Window {
  sendMessage: ?((message: string, other_params_data: any) => void)
  chatUserProfile: ?(() => any)
  MaxKB: {
    prefix: string
    chatPrefix: string
  }
}
