<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('chat.preview')"
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
        <el-button :loading="loading" @click="exportPDF">{{ $t('chat.exportPDF') }}</el-button>
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
          {{ $t('chat.exportImg') }}
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
    htmlToImage
      .toCanvas(element, {
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
        const canvas = await htmlToImage.toCanvas(targetEl, {
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
        const canvas = await htmlToImage.toCanvas(targetEl, {
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
