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
const open = (element: HTMLElement | null) => {
  dialogVisible.value = true
  loading.value = true
  if (!element) {
    return
  }
  const cElement = element.cloneNode(true) as HTMLElement
  const images = cElement.querySelectorAll('img')
  const loadPromises = Array.from(images).map((img) => {
    if (!img.src.startsWith(window.origin) && img.src.startsWith('http')) {
      img.src = `${window.MaxKB.prefix}/api/resource_proxy?url=${encodeURIComponent(img.src)}`
    }
    img.setAttribute('onerror', '')
    return new Promise((resolve) => {
      // 已加载完成的图片直接 resolve
      if (img.complete) {
        resolve({ img, success: img.naturalWidth > 0 })
        return
      }

      // 未加载完成的图片监听事件
      img.onload = () => resolve({ img, success: true })
      img.onerror = () => resolve({ img, success: false })
    })
  })
  Promise.all(loadPromises).finally(() => {
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
          })
          .finally(() => {
            loading.value = false
          })
          .catch((e) => {
            loading.value = false
          })
      })
    }, 1)
  })
}

const exportPDF = () => {
  loading.value = true
  setTimeout(() => {
    nextTick(() => {
      html2Canvas(svgContainerRef.value, {
        logging: false,
        allowTaint: true,
        useCORS: true,
      })
        .then((canvas) => {
          const doc = new jsPDF('p', 'mm', 'a4')
          // 将canvas转换为图片
          const imgData = canvas.toDataURL(`image/jpeg`, 1)
          // 获取PDF页面尺寸
          const pageWidth = doc.internal.pageSize.getWidth()
          const pageHeight = doc.internal.pageSize.getHeight()
          // 计算图像在PDF中的尺寸
          const imgWidth = pageWidth
          const imgHeight = (canvas.height * imgWidth) / canvas.width
          // 添加图像到PDF
          doc.addImage(imgData, 'jpeg', 0, 0, imgWidth, imgHeight)

          // 如果内容超过一页，自动添加新页面
          let heightLeft = imgHeight
          let position = 0

          // 第一页已经添加
          heightLeft -= pageHeight

          // 当内容超过一页时
          while (heightLeft >= 0) {
            position = heightLeft - imgHeight
            doc.addPage()
            doc.addImage(imgData, 'jpeg', 0, position, imgWidth, imgHeight)
            heightLeft -= pageHeight
          }

          // 保存PDF
          doc.save('导出文档.pdf')
          return 'ok'
        })
        .finally(() => {
          loading.value = false
        })
    })
  })
}
const exportJepg = () => {
  loading.value = true
  setTimeout(() => {
    nextTick(() => {
      html2Canvas(svgContainerRef.value, {
        logging: false,
        allowTaint: true,
        useCORS: true,
      })
        .then((canvas) => {
          // 将canvas转换为图片
          const imgData = canvas.toDataURL(`image/jpeg`, 1)
          const link = document.createElement('a')
          link.download = `webpage-screenshot.jpeg`
          link.href = imgData
          document.body.appendChild(link)
          link.click()
          return 'ok'
        })
        .finally(() => {
          loading.value = false
        })
    })
  }, 1)
}
const close = () => {
  dialogVisible.value = false
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
