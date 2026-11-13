<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { downloadBlob } from './use-conversation-export'
import { MsgError } from '@/utils/message'

const visible = ref(false)
const loading = ref(false)
const previewUrl = ref('')
let capturedCanvas: HTMLCanvasElement | null = null
let fileName = '对话记录'

function clear() {
  previewUrl.value = ''
  capturedCanvas = null
}

onBeforeUnmount(clear)

function open(canvas: HTMLCanvasElement, name: string) {
  clear()
  capturedCanvas = canvas
  fileName = name
  previewUrl.value = canvas.toDataURL('image/png')
  visible.value = true
}

async function save(format: 'pdf' | 'png') {
  const canvas = capturedCanvas
  if (!canvas || loading.value) return
  loading.value = true
  try {
    if (format === 'png') {
      const blob = await new Promise<Blob>((resolve, reject) =>
        canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error('图片生成失败'))), 'image/png'),
      )
      downloadBlob(blob, `${fileName}.png`)
    } else {
      const { jsPDF } = await import('jspdf')
      const pdf = new jsPDF('p', 'mm', 'a4')
      const width = pdf.internal.pageSize.getWidth()
      const height = pdf.internal.pageSize.getHeight()
      const pagePixels = Math.max(1, Math.floor((canvas.width * height) / width))
      // 逐页裁切，避免在每页重复嵌入整张长图。
      for (let top = 0; top < canvas.height; top += pagePixels) {
        const page = document.createElement('canvas')
        page.width = canvas.width
        page.height = Math.min(pagePixels, canvas.height - top)
        const context = page.getContext('2d')
        if (!context) throw new Error('无法创建画布')
        context.drawImage(canvas, 0, top, page.width, page.height, 0, 0, page.width, page.height)
        if (top) pdf.addPage()
        pdf.addImage(page.toDataURL('image/jpeg', 0.95), 'JPEG', 0, 0, width, (page.height * width) / page.width)
      }
      pdf.save(`${fileName}.pdf`)
    }
  } catch {
    MsgError('导出失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="导出预览" width="900px" @closed="clear">
    <img v-if="previewUrl" :src="previewUrl" alt="对话导出预览" class="w-full" />
    <template #footer>
      <!-- 导出 PDF -->
      <el-button :loading="loading" @click="save('pdf')">导出 PDF</el-button>
      <!-- 导出图片 -->
      <el-button type="primary" :loading="loading" @click="save('png')">导出图片</el-button>
    </template>
  </MkDialog>
</template>
