import { ref } from 'vue'
import type { PDFDocumentLoadingTask, PDFDocumentProxy, RenderTask } from 'pdfjs-dist/legacy/build/pdf.mjs'

/** 待预览的来源文档；当前预览文档由知识来源 store 维护。 */
export interface PreviewDocument {
  name: string
  url: string
}

/** 按文件名判断是否为可预览的 PDF。 */
export const isPdfDocument = (name: string) => name.trim().toLowerCase().endsWith('.pdf')

type PdfJs = typeof import('pdfjs-dist/legacy/build/pdf.mjs')

// pdf.js 体积较大，首次预览时才加载；worker 地址由构建产出
let pdfJsLoader: Promise<PdfJs> | undefined
function loadPdfJs() {
  pdfJsLoader ??= Promise.all([import('pdfjs-dist/legacy/build/pdf.mjs'), import('pdfjs-dist/legacy/build/pdf.worker.min.mjs?url')]).then(
    ([pdfJs, worker]) => {
      pdfJs.GlobalWorkerOptions.workerSrc = worker.default
      return pdfJs
    },
  )
  return pdfJsLoader
}

const isRenderCancelled = (error: unknown) => (error as { name?: string } | null)?.name === 'RenderingCancelledException'

/**
 * PDF 渲染器：使用 pdf.js 把每页绘制为 canvas，不使用浏览器原生 PDF 预览。
 * 只绘制画布，不创建文本层与注释层，PDF 内的脚本、表单与链接均不会执行；关闭 XFA（pdf.js v6 已不使用 eval）。
 * 首次加载逐页追加；容器宽度变化时在后台按新宽度重绘，全部完成后一次替换并按比例保持滚动位置，
 * 避免清空内容导致高度塌陷、滚动条反复出现而触发循环重绘。切换文档或销毁时取消未完成的加载与绘制。
 */
export function createPdfRenderer() {
  const loading = ref(false)
  const error = ref('')

  // 每次加载或重绘递增，晚到的旧结果据此丢弃
  let token = 0
  let container: HTMLElement | null = null
  let scroller: HTMLElement | null = null
  let loadingTask: PDFDocumentLoadingTask | null = null
  let pdfDocument: PDFDocumentProxy | null = null
  let renderTasks: RenderTask[] = []
  let renderedWidth = 0
  let resizeTimer: number | undefined

  const cancelRenderTasks = () => {
    renderTasks.forEach((task) => task.cancel())
    renderTasks = []
  }

  const releaseDocument = async () => {
    cancelRenderTasks()
    container?.replaceChildren()
    const task = loadingTask
    loadingTask = null
    pdfDocument = null
    await task?.destroy()
  }

  // progressive：首次加载逐页显示；重绘时先绘制到未挂载的 canvas，完成后整体替换
  async function drawPages(current: number, progressive: boolean) {
    if (!pdfDocument || !container) return
    cancelRenderTasks()
    const target = container
    if (progressive) target.replaceChildren()
    renderedWidth = Math.floor(target.clientWidth)
    const outputScale = window.devicePixelRatio || 1
    const canvases: HTMLCanvasElement[] = []

    for (let pageNumber = 1; pageNumber <= pdfDocument.numPages; pageNumber++) {
      const page = await pdfDocument.getPage(pageNumber)
      if (current !== token) return
      const baseViewport = page.getViewport({ scale: 1 })
      const viewport = page.getViewport({ scale: renderedWidth > 0 ? renderedWidth / baseViewport.width : 1 })

      const canvas = document.createElement('canvas')
      canvas.width = Math.floor(viewport.width * outputScale)
      canvas.height = Math.floor(viewport.height * outputScale)
      canvas.style.width = `${Math.floor(viewport.width)}px`
      canvas.style.height = `${Math.floor(viewport.height)}px`
      if (progressive) target.appendChild(canvas)
      else canvases.push(canvas)

      const task = page.render({
        canvas,
        viewport,
        transform: outputScale === 1 ? undefined : [outputScale, 0, 0, outputScale, 0, 0],
      })
      renderTasks.push(task)
      try {
        await task.promise
      } catch (renderError) {
        if (isRenderCancelled(renderError)) return
        throw renderError
      } finally {
        renderTasks = renderTasks.filter((renderTask) => renderTask !== task)
      }
    }
    if (progressive || current !== token) return

    // 按替换前的滚动比例恢复位置，阅读位置不因重绘跳回顶部
    const scrollRatio = scroller && scroller.scrollHeight > 0 ? scroller.scrollTop / scroller.scrollHeight : 0
    target.replaceChildren(...canvases)
    if (scroller) scroller.scrollTop = scrollRatio * scroller.scrollHeight
  }

  // 宽度变化（面板拉伸、全屏）后防抖重绘
  const redraw = () => {
    const current = ++token
    drawPages(current, false).catch(() => {
      if (current === token) error.value = 'PDF 渲染失败'
    })
  }
  const resizeObserver = new ResizeObserver(([entry]) => {
    if (!entry || !pdfDocument || Math.floor(entry.contentRect.width) === renderedWidth) return
    window.clearTimeout(resizeTimer)
    resizeTimer = window.setTimeout(redraw, 200)
  })

  /** target 为放置页面的容器，scrollTarget 为其滚动容器，用于重绘后保持滚动位置。 */
  async function render(target: HTMLElement, scrollTarget: HTMLElement, url: string) {
    const current = ++token
    resizeObserver.disconnect()
    await releaseDocument()
    container = target
    scroller = scrollTarget
    scrollTarget.scrollTop = 0
    resizeObserver.observe(target)
    loading.value = true
    error.value = ''
    try {
      const pdfJs = await loadPdfJs()
      if (current !== token) return
      const task = pdfJs.getDocument({ url, enableXfa: false })
      loadingTask = task
      pdfDocument = await task.promise
      if (current !== token) return
      await drawPages(current, true)
    } catch {
      if (current === token) error.value = 'PDF 加载失败'
    } finally {
      if (current === token) loading.value = false
    }
  }

  async function destroy() {
    token++
    window.clearTimeout(resizeTimer)
    resizeObserver.disconnect()
    await releaseDocument()
    container = null
    scroller = null
  }

  return { loading, error, render, destroy }
}

/** 全屏切换：仅作用于预览区域，退出全屏后由渲染器按新宽度重绘。 */
export function createFullscreenToggle() {
  const isFullscreen = ref(false)
  let element: HTMLElement | null = null

  const sync = () => {
    isFullscreen.value = Boolean(element) && document.fullscreenElement === element
  }

  const bind = (target: HTMLElement) => {
    element = target
    document.addEventListener('fullscreenchange', sync)
  }

  const unbind = () => {
    document.removeEventListener('fullscreenchange', sync)
    if (element && document.fullscreenElement === element) void document.exitFullscreen()
    element = null
  }

  const toggle = async () => {
    if (!element) return
    try {
      if (document.fullscreenElement === element) await document.exitFullscreen()
      else await element.requestFullscreen()
    } catch {
      /* 浏览器拒绝全屏时保持原状 */
    }
  }

  return { isFullscreen, bind, unbind, toggle }
}
