<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('aiChat.preview')"
    style="overflow: auto"
    width="60%"
    :before-close="close"
    destroy-on-close
    align-center
  >
    <div
      v-loading="loading"
      style="
        max-height: calc(100vh - 200px);
        overflow-y: auto;
        display: flex;
        justify-content: center;
      "
    >
      <div ref="svgContainerRef"></div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button :loading="loading" @click="exportPDF">{{ $t('aiChat.exportPDF') }}</el-button>
        <el-button
          :loading="loading"
          type="primary"
          @click="
            () => {
              loading = true
              exportJepg()
            }
          "
        >
          {{ $t('aiChat.exportImg') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import * as htmlToImage from 'html-to-image'
import { ref, nextTick } from 'vue'
import { jsPDF } from 'jspdf'

const loading = ref<boolean>(false)
const svgContainerRef = ref()
const dialogVisible = ref<boolean>(false)

// 保存原始元素引用，用于导出
const originalElement = ref<HTMLElement | null>(null)

// 沙箱 iframe（无 allow-same-origin）的 contentDocument 不可访问，html-to-image 只能克隆出空 iframe。
// 导出前让 iframe 自身序列化 DOM，放入不执行脚本的同源 iframe 中单独截图，再临时替换原 iframe，截图后还原。
const SNAPSHOT_TIMEOUT = 3000

const requestIframeSnapshot = (iframe: HTMLIFrameElement): Promise<string | null> => {
  return new Promise((resolve) => {
    const win = iframe.contentWindow
    if (!win) return resolve(null)
    const requestId = Date.now() + '_' + Math.random()
    const timer = setTimeout(() => done(null), SNAPSHOT_TIMEOUT)
    function handler(e: MessageEvent) {
      if (e.source !== win || e.data?.type !== 'snapshot:response') return
      if (e.data.requestId !== requestId) return
      done(e.data.html || null)
    }
    function done(html: string | null) {
      clearTimeout(timer)
      window.removeEventListener('message', handler)
      resolve(html)
    }
    window.addEventListener('message', handler)
    win.postMessage({ type: 'snapshot', requestId }, '*')
  })
}

const createStaticIframe = (
  iframe: HTMLIFrameElement,
  html: string,
): Promise<HTMLIFrameElement> => {
  return new Promise((resolve) => {
    const staticIframe = document.createElement('iframe')
    // 仅同源、不允许脚本：父页面可读取内容，且不会执行任何脚本
    staticIframe.setAttribute('sandbox', 'allow-same-origin')
    staticIframe.className = iframe.className
    staticIframe.style.cssText = iframe.style.cssText
    staticIframe.style.width = iframe.offsetWidth + 'px'
    staticIframe.style.height = iframe.offsetHeight + 'px'
    // 放到屏幕外渲染，避免影响对话页面布局
    staticIframe.style.position = 'fixed'
    staticIframe.style.left = '-100000px'
    staticIframe.style.top = '0'
    staticIframe.onload = () => resolve(staticIframe)
    staticIframe.srcdoc = html
    document.body.appendChild(staticIframe)
  })
}

// 将 iframe 内容单独截成 canvas。
// 不直接交给 html-to-image 处理 iframe：其克隆同源 iframe 时会用 iframe 的样式覆盖 body 的样式，导致布局/背景丢失
const iframeToCanvas = async (
  iframe: HTMLIFrameElement,
  options: any,
): Promise<HTMLCanvasElement | null> => {
  const html = await requestIframeSnapshot(iframe)
  if (!html) return null
  const staticIframe = await createStaticIframe(iframe, html)
  try {
    const root = staticIframe.contentDocument?.documentElement
    if (!root) return null
    const width = iframe.offsetWidth
    const height = iframe.offsetHeight
    const canvas = await htmlToImage.toCanvas(root, {
      ...options,
      backgroundColor: undefined,
      width,
      height,
      canvasWidth: width,
      canvasHeight: height,
    })
    canvas.style.cssText = iframe.style.cssText
    canvas.style.display = 'block'
    canvas.style.width = width + 'px'
    canvas.style.height = height + 'px'
    return canvas
  } finally {
    staticIframe.remove()
  }
}

const toCanvasWithIframes = async (element: HTMLElement, options: any) => {
  const iframes = Array.from(element.querySelectorAll('iframe')).filter(
    (iframe) => iframe.offsetWidth > 0 && iframe.offsetHeight > 0,
  )
  const replaced: {
    iframe: HTMLIFrameElement
    canvas: HTMLCanvasElement
    display: string
  }[] = []
  try {
    const canvases = await Promise.all(
      iframes.map((iframe) =>
        iframeToCanvas(iframe, options).catch((e) => {
          console.error('iframe snapshot error:', e)
          return null
        }),
      ),
    )
    // 截图全部完成后再统一替换，避免替换过程影响其他 iframe 的尺寸
    iframes.forEach((iframe, i) => {
      const canvas = canvases[i]
      if (!canvas) return
      replaced.push({ iframe, canvas, display: iframe.style.display })
      iframe.after(canvas)
      iframe.style.display = 'none'
    })
    return await htmlToImage.toCanvas(element, options)
  } finally {
    replaced.forEach(({ iframe, canvas, display }) => {
      canvas.remove()
      iframe.style.display = display
    })
  }
}

const open = (element: HTMLElement | null) => {
  dialogVisible.value = true
  loading.value = true
  if (!element) {
    loading.value = false
    return
  }

  // 保存原始元素引用
  originalElement.value = element

  nextTick(() => {
    toCanvasWithIframes(element, {
      pixelRatio: window.devicePixelRatio || 1,
      quality: 1,
      skipFonts: false,
      backgroundColor: '#ffffff',
    })
      .then((canvas) => {
        // 清空之前的内容
        svgContainerRef.value.innerHTML = ''
        canvas.style.width = '100%'
        canvas.style.height = 'auto'
        svgContainerRef.value.appendChild(canvas)
      })
      .finally(() => {
        loading.value = false
      })
      .catch((e) => {
        console.error(e)
        loading.value = false
      })
  })
}

const exportPDF = () => {
  loading.value = true
  setTimeout(() => {
    nextTick(async () => {
      try {
        const targetEl = originalElement.value
        if (!targetEl) return
        const canvas = await toCanvasWithIframes(targetEl, {
          pixelRatio: 2,
          quality: 1,
          skipFonts: false,
          backgroundColor: '#ffffff',
        })
        generatePDF(canvas)
      } catch (e) {
        console.error('PDF export error:', e)
      } finally {
        loading.value = false
      }
    })
  })
}

const generatePDF = (canvas: HTMLCanvasElement) => {
  const doc = new jsPDF('p', 'mm', 'a4')
  const imgData = canvas.toDataURL('image/jpeg', 1)
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const imgWidth = pageWidth
  const imgHeight = (canvas.height * imgWidth) / canvas.width

  doc.addImage(imgData, 'JPEG', 0, 0, imgWidth, imgHeight)

  let heightLeft = imgHeight - pageHeight
  while (heightLeft > 0) {
    const position = -(imgHeight - heightLeft)
    doc.addPage()
    doc.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
  }

  doc.save('导出文档.pdf')
}

const exportJepg = () => {
  loading.value = true
  setTimeout(() => {
    nextTick(async () => {
      try {
        const targetEl = originalElement.value
        if (!targetEl) return
        const canvas = await toCanvasWithIframes(targetEl, {
          pixelRatio: window.devicePixelRatio || 1,
          quality: 1,
          skipFonts: false,
          backgroundColor: '#ffffff',
        })
        downloadJpeg(canvas)
      } catch (e) {
        console.error('JPEG export error:', e)
      } finally {
        loading.value = false
      }
    })
  }, 1)
}

const downloadJpeg = (canvas: HTMLCanvasElement) => {
  const newCanvas = document.createElement('canvas')
  newCanvas.width = canvas.width
  newCanvas.height = canvas.height
  const ctx = newCanvas.getContext('2d')!
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, newCanvas.width, newCanvas.height)
  ctx.drawImage(canvas, 0, 0)

  const imgData = newCanvas.toDataURL('image/jpeg', 1)
  const link = document.createElement('a')
  link.download = 'webpage-screenshot.jpeg'
  link.href = imgData
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const close = () => {
  dialogVisible.value = false
  originalElement.value = null
  // 清空预览内容
  if (svgContainerRef.value) {
    svgContainerRef.value.innerHTML = ''
  }
}

defineExpose({ open, close })
</script>
