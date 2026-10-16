<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'
import type { KnowledgeHitTestResult } from '@/api/types'

defineOptions({ name: 'KnowledgeHitTestResult' })
defineProps<{ paragraph: KnowledgeHitTestResult; index: number }>()
</script>

<template>
  <article class="overflow-hidden rounded-xl border bg-white p-4">
    <header class="flex-between gap-3">
      <div class="flex-align-center min-w-0 gap-2">
        <span class="flex-center size-6 shrink-0 rounded-md bg-primary/10 text-sm text-primary">{{ index }}</span>
        <h6 class="min-w-0 break-words">{{ paragraph.title || '未命名分段' }}</h6>
      </div>
      <MkTooltip content="检索相似度">
        <span class="shrink-0 text-primary">{{ paragraph.similarity.toFixed(3) }}</span>
      </MkTooltip>
    </header>
    <el-image
      v-if="paragraph.hit_asset"
      :src="paragraph.hit_asset.url"
      :alt="paragraph.hit_asset.caption || paragraph.hit_asset.file_name"
      :preview-src-list="[paragraph.hit_asset.url]"
      preview-teleported
      fit="contain"
      class="mt-3 h-40 max-w-full rounded-md"
    />
    <el-scrollbar max-height="280" class="my-3">
      <MdPreview :model-value="paragraph.content" />
    </el-scrollbar>
    <footer class="flex-align-center min-w-0 gap-1 border-t pt-3 text-sm text-N600">
      <el-icon class="shrink-0"><Document /></el-icon>
      <span class="truncate" :title="paragraph.document_name">{{ paragraph.document_name }}</span>
    </footer>
  </article>
</template>
