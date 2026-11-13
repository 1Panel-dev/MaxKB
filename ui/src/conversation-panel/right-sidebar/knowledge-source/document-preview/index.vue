<script setup lang="ts">
import { onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue'
import { downloadByURL } from '@/utils/common'
import { useRightSidebarStore } from '../../index'
import { createFullscreenToggle, createPdfRenderer } from './index'

defineOptions({ name: 'DocumentPreview' })

const { knowledgeSource, closeRightSide } = useRightSidebarStore()
const { previewDocument, closePreview } = knowledgeSource
const { loading, error, render, destroy } = createPdfRenderer()
const fullscreen = createFullscreenToggle()

const viewerRef = useTemplateRef<HTMLElement>('viewerRef')
const pagesRef = useTemplateRef<HTMLElement>('pagesRef')

// 下载当前预览的 PDF 原文件
const downloadDocument = () => {
  const document = previewDocument.value
  if (document?.url) downloadByURL(document.url, document.name)
}

// 挂载及切换文档时重新绘制，卸载时释放 pdf.js 资源
onMounted(() => {
  if (viewerRef.value) fullscreen.bind(viewerRef.value)
  watch(
    () => previewDocument.value?.url,
    (url) => {
      if (url && pagesRef.value && viewerRef.value) void render(pagesRef.value, viewerRef.value, url)
    },
    { immediate: true },
  )
})
onBeforeUnmount(() => {
  fullscreen.unbind()
  void destroy()
})
</script>

<template>
  <!-- 知识来源的下一级:来源文档 PDF 预览。数据来自知识来源列表点击 PDF 文档写入 -->
  <div class="document-preview-panel flex-column h-full">
    <div class="flex-between shrink-0 gap-2 px-6 py-4 border-b">
      <div class="flex-align-center min-w-0 gap-1">
        <!-- 返回知识来源 -->
        <el-button text class="-ml-2 shrink-0" @click="closePreview()">
          <MkIcon name="icon_arrow-left_outlined" size="18" />
        </el-button>
        <h4 class="min-w-0 truncate" :title="previewDocument?.name">{{ previewDocument?.name }}</h4>
      </div>
      <div class="flex-align-center gap-2 shrink-0">
        <!-- 下载 -->
        <MkTooltip content="下载">
          <el-button text :disabled="!previewDocument?.url" @click="downloadDocument">
            <MkIcon name="icon_download_outlined" size="18" />
          </el-button>
        </MkTooltip>
        <!-- 全屏预览 -->
        <MkTooltip content="全屏">
          <el-button text @click="fullscreen.toggle()" class="ml-0!">
            <MkIcon name="icon_window-new_outlined" size="18" />
          </el-button>
        </MkTooltip>
        <el-divider direction="vertical" class="mx-1!" />
        <!-- 关闭文档预览 -->
        <el-button text @click="closeRightSide()">
          <MkIcon name="icon_close_outlined" size="18" />
        </el-button>
      </div>
    </div>
    <div ref="viewerRef" class="document-preview-viewer relative min-h-0 flex-1 overflow-auto bg-white">
      <div class="p-6">
        <div ref="pagesRef" class="document-preview-pages" :class="{ invisible: loading || error }" />
      </div>
      <div v-if="loading" class="absolute inset-0 flex-center gap-2 text-N600">
        <LoadingIcon />
        <span>PDF 加载中...</span>
      </div>
      <el-empty v-else-if="error" class="absolute inset-0" :description="error" :image-size="80" />
    </div>
  </div>
</template>

<style scoped lang="scss">
// 预留滚动条位置：内容超出出现滚动条时页面宽度不变，不触发重绘
.document-preview-viewer {
  scrollbar-gutter: stable;
}

.document-preview-pages :deep(canvas) {
  display: block;
  max-width: 100%;
  margin-bottom: 12px;
  &:last-child {
    margin-bottom: 0;
  }
}
</style>
