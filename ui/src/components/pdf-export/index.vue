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
      <div ref="cloneContainerRef" style="width: 100%"></div>
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
import html2Canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

const loading = ref<boolean>(false)
const svgContainerRef = ref()
const cloneContainerRef = ref()
const dialogVisible = ref<boolean>(false)
const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)

const open = (element: HTMLElement | null) => {
  dialogVisible.value = true
  loading.value = true
  if (!element) {
    loading.value = false
    return
  }
  const cElement = element.cloneNode(true) as HTMLElement
  setTimeout(() => {
    nextTick(() => {
      cloneContainerRef.value.appendChild(cElement)
      htmlToImage
        .toSvg(cElement, {
          pixelRatio: 1,
          quality: 1,
          onImageErrorHandler: (
            event: Event | string,
            source?: string,
            lineno?: number,
            colno?: number,
            error?: Error,
          ) => {
            console.log(event, source, lineno, colno, error)
          },
        })
        .then((dataUrl) => {
          if (isSafari) {
            // Safari: 跳过 SVG data URI，直接用 toCanvas
            return htmlToImage
              .toCanvas(cElement, {
                pixelRatio: 1,
                quality: 1,
              })
              .then((canvas) => {
                cloneContainerRef.value.style.display = 'none'
                canvas.style.width = '100%'
                canvas.style.height = 'auto'
                svgContainerRef.value.appendChild(canvas)
                svgContainerRef.value.style.height = canvas.height + 'px'
              })
          } else {
            // Chrome 等：保持原逻辑
            return fetch(dataUrl)
              .then((response) => {
                return response.text()
              })
              .then((text) => {
                const parser = new DOMParser()
                const svgDoc = parser.parseFromString(text, 'image/svg+xml')
                cloneContainerRef.value.style.display = 'none'
                const svgElement = svgDoc.documentElement
                svgContainerRef.value.appendChild(svgElement)
                svgContainerRef.value.style.height = svgElement.scrollHeight + 'px'
              })
          }
        })
        .finally(() => {
          loading.value = false
        })
        .catch((e) => {
          console.error(e)
          loading.value = false
        })
    })
  }, 1)
}

const exportPDF = () => {
  loading.value = true
  setTimeout(() => {
    nextTick(() => {
      if (isSafari) {
        // Safari: 直接取已有的 canvas
        const canvas = svgContainerRef.value.querySelector('canvas')
        if (canvas) {
          generatePDF(canvas)
        }
        loading.value = false
      } else {
        html2Canvas(svgContainerRef.value, {
          logging: false,
          allowTaint: true,
          useCORS: true,
        })
          .then((canvas) => {
            generatePDF(canvas)
          })
          .finally(() => {
            loading.value = false
          })
      }
    })
  })
}

const generatePDF = (canvas: HTMLCanvasElement) => {
  const newCanvas = document.createElement('canvas')
  newCanvas.width = canvas.width
  newCanvas.height = canvas.height
  const ctx = newCanvas.getContext('2d')!
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, newCanvas.width, newCanvas.height)
  ctx.drawImage(canvas, 0, 0)

  const doc = new jsPDF('p', 'mm', 'a4')
  const imgData = newCanvas.toDataURL('image/jpeg', 1)
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const imgWidth = pageWidth
  const imgHeight = (newCanvas.height * imgWidth) / newCanvas.width

  doc.addImage(imgData, 'jpeg', 0, 0, imgWidth, imgHeight)

  let heightLeft = imgHeight - pageHeight

  while (heightLeft > 0) {
    const position = -(imgHeight - heightLeft)
    doc.addPage()
    doc.addImage(imgData, 'jpeg', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight
  }

  doc.save('导出文档.pdf')
}

const exportJepg = () => {
  loading.value = true
  setTimeout(() => {
    nextTick(() => {
      if (isSafari) {
        // Safari: 直接取已有的 canvas
        const canvas = svgContainerRef.value.querySelector('canvas')
        if (canvas) {
          downloadJpeg(canvas)
        }
        loading.value = false
      } else {
        html2Canvas(svgContainerRef.value, {
          logging: false,
          allowTaint: true,
          useCORS: true,
        })
          .then((canvas) => {
            downloadJpeg(canvas)
          })
          .finally(() => {
            loading.value = false
          })
      }
    })
  }, 1)
}

const downloadJpeg = (canvas: HTMLCanvasElement) => {
  // 创建新 canvas，先填充白色背景
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
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
