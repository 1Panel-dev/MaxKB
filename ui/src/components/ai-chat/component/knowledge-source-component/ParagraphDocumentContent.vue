<template>
  <div ref="viewerRef" class="pdf-viewer">
    <div class="pdf-stage" ref="stageRef">
      <div class="pdf-actions">
        <el-button size="small" type="primary" plain @click="toggleFullscreen">
          <el-icon><FullScreen /></el-icon>
          <span>{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
        </el-button>
      </div>

      <div ref="pagesRef" class="pdf-pages" :class="{ 'is-hidden': !!overlayText }"></div>

      <div v-if="loading" class="pdf-overlay">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>PDF 加载中...</span>
      </div>

      <div v-else-if="overlayText" class="pdf-overlay" :class="{ 'pdf-overlay--error': !!error }">
        <span>{{ overlayText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  markRaw,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  shallowRef,
  watch,
} from 'vue'
import { FullScreen, Loading } from '@element-plus/icons-vue'
import * as pdfjsLib from 'pdfjs-dist/build/pdf.mjs'

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

type PdfDocumentProxy = any
type RenderTask = any
type PdfLoadingTask = any

const props = defineProps<{
  detail?: any
}>()

const viewerRef = ref<HTMLDivElement | null>(null)
const stageRef = ref<HTMLDivElement | null>(null)
const pagesRef = ref<HTMLDivElement | null>(null)

const loading = ref(false)
const error = ref('')
const isFullscreen = ref(false)

const pdfDoc = shallowRef<PdfDocumentProxy | null>(null)
const loadingTaskRef = shallowRef<PdfLoadingTask | null>(null)
const renderTasks = shallowRef<RenderTask[]>([])
const requestToken = ref(0)

const isPdf = computed(() => !!props.detail?.meta?.source_file_id)

const pdfSrc = computed(() => {
  const fileId = props.detail?.meta?.source_file_id
  return fileId ? `${window.MaxKB.prefix}/oss/file/${fileId}` : ''
})

const overlayText = computed(() => {
  if (error.value) return error.value
  if (!isPdf.value) return '暂无 PDF 预览'
  return ''
})

function clearPages() {
  if (pagesRef.value) {
    pagesRef.value.innerHTML = ''
  }
}

async function cancelRenderTasks() {
  if (!renderTasks.value.length) return

  for (const task of renderTasks.value) {
    try {
      task.cancel()
    } catch {
      //
    }
  }

  renderTasks.value = []
}

async function destroyLoadingTask() {
  if (!loadingTaskRef.value) return

  try {
    await loadingTaskRef.value.destroy()
  } catch {
    //
  } finally {
    loadingTaskRef.value = null
  }
}

async function destroyPdfDoc() {
  if (!pdfDoc.value) return

  try {
    await pdfDoc.value.destroy()
  } catch {
    //
  } finally {
    pdfDoc.value = null
  }
}

function getAvailableWidth() {
  if (!stageRef.value) return 0
  const style = getComputedStyle(stageRef.value)
  const paddingLeft = Number.parseFloat(style.paddingLeft || '0')
  const paddingRight = Number.parseFloat(style.paddingRight || '0')
  return stageRef.value.clientWidth - paddingLeft - paddingRight
}

async function renderAllPages() {
  if (!pdfDoc.value || !pagesRef.value) return

  const currentToken = requestToken.value
  const container = pagesRef.value
  clearPages()
  renderTasks.value = []

  const availableWidth = getAvailableWidth()

  for (let pageNum = 1; pageNum <= pdfDoc.value.numPages; pageNum++) {
    if (currentToken !== requestToken.value) return

    const page = await pdfDoc.value.getPage(pageNum)
    if (currentToken !== requestToken.value) return

    const baseViewport = page.getViewport({ scale: 1 })
    const fitScale =
      availableWidth > 0 && baseViewport.width > 0
        ? Math.min(3, Math.max(0.5, availableWidth / baseViewport.width))
        : 1

    const viewport = page.getViewport({ scale: fitScale })

    const canvas = document.createElement('canvas')
    canvas.className = 'pdf-canvas'

    const context = canvas.getContext('2d')
    if (!context) continue

    const outputScale = window.devicePixelRatio || 1
    canvas.width = Math.floor(viewport.width * outputScale)
    canvas.height = Math.floor(viewport.height * outputScale)
    canvas.style.width = `${Math.floor(viewport.width)}px`
    canvas.style.height = `${Math.floor(viewport.height)}px`

    context.setTransform(1, 0, 0, 1, 0, 0)
    context.clearRect(0, 0, canvas.width, canvas.height)
    context.setTransform(outputScale, 0, 0, outputScale, 0, 0)

    container.appendChild(canvas)

    const task = markRaw(
      page.render({
        canvasContext: context,
        viewport,
      }),
    )

    renderTasks.value = [...renderTasks.value, task]

    try {
      await task.promise
    } catch (err: any) {
      if (err?.name !== 'RenderingCancelledException') {
        throw err
      }
    } finally {
      renderTasks.value = renderTasks.value.filter((item) => item !== task)
    }
  }
}

async function loadPdf(url: string) {
  const currentToken = ++requestToken.value
  loading.value = true
  error.value = ''

  await cancelRenderTasks()
  await destroyLoadingTask()
  await destroyPdfDoc()
  clearPages()

  try {
    const loadingTask = pdfjsLib.getDocument({
      url,
    })

    loadingTaskRef.value = markRaw(loadingTask)
    const doc = await loadingTask.promise

    if (currentToken !== requestToken.value) {
      await doc.destroy()
      return
    }

    loadingTaskRef.value = null
    pdfDoc.value = markRaw(doc)

    await nextTick()
    await renderAllPages()
  } catch (err: any) {
    console.error(err)
    error.value = err?.message || 'PDF 加载失败'
    clearPages()
  } finally {
    if (currentToken === requestToken.value) {
      loading.value = false
    }
  }
}

async function handleResize() {
  if (!pdfDoc.value || loading.value) return

  const currentToken = ++requestToken.value
  loading.value = true
  error.value = ''

  try {
    await cancelRenderTasks()
    if (currentToken !== requestToken.value) return
    clearPages()
    await nextTick()
    await renderAllPages()
  } catch (err: any) {
    console.error(err)
    error.value = err?.message || 'PDF 重绘失败'
  } finally {
    if (currentToken === requestToken.value) {
      loading.value = false
    }
  }
}

async function toggleFullscreen() {
  try {
    if (!document.fullscreenElement) {
      await viewerRef.value?.requestFullscreen()
    } else {
      await document.exitFullscreen()
    }
  } catch (err) {
    console.error('toggle fullscreen failed:', err)
  }
}

function syncFullscreenState() {
  isFullscreen.value = document.fullscreenElement === viewerRef.value
}

async function onFullscreenChange() {
  syncFullscreenState()
  await nextTick()
  await handleResize()
}

watch(
  pdfSrc,
  async (url) => {
    await nextTick()

    if (!isPdf.value || !url) {
      error.value = ''
      await cancelRenderTasks()
      await destroyLoadingTask()
      await destroyPdfDoc()
      clearPages()
      return
    }

    await loadPdf(url)
  },
  { immediate: true },
)

let resizeTimer: number | null = null

function onWindowResize() {
  if (resizeTimer) {
    window.clearTimeout(resizeTimer)
  }

  resizeTimer = window.setTimeout(() => {
    handleResize()
  }, 200)
}

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
  window.addEventListener('resize', onWindowResize)
})

onBeforeUnmount(async () => {
  if (resizeTimer) {
    window.clearTimeout(resizeTimer)
    resizeTimer = null
  }

  document.removeEventListener('fullscreenchange', onFullscreenChange)
  window.removeEventListener('resize', onWindowResize)
  requestToken.value++

  await cancelRenderTasks()
  await destroyLoadingTask()
  await destroyPdfDoc()
  clearPages()
})
</script>

<style scoped>
.pdf-viewer {
  width: 100%;
  height: calc(100vh - 57px);
  background: #fff;
}

.pdf-viewer:fullscreen {
  width: 100vw;
  height: 100vh;
  background: #fff;
}

.pdf-stage {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: auto;
  background: #fff;
}

.pdf-actions {
  position: sticky;
  top: 12px;
  right: 12px;
  z-index: 3;
  display: flex;
  justify-content: flex-end;
  padding: 12px 12px 0 12px;
  pointer-events: none;
}

.pdf-actions :deep(.el-button) {
  pointer-events: auto;
}

.pdf-pages {
  width: 100%;
  min-height: 100%;
}

.pdf-pages.is-hidden {
  visibility: hidden;
}

:deep(.pdf-canvas) {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  margin: 0 0 12px 0;
  background: #fff;
  box-shadow: none;
  border-radius: 0;
}

:deep(.pdf-canvas:last-child) {
  margin-bottom: 0;
}

.pdf-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #fff;
  color: var(--el-text-color-regular);
  font-size: 14px;
  z-index: 2;
}

.pdf-overlay--error {
  color: var(--el-color-danger);
}
</style>
