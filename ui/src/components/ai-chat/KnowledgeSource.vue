<template>
  <div class="flex align-center mt-16" v-if="!isWorkFlow(props.type)">
    <span class="mr-4 color-secondary">知识来源</span>
    <el-divider direction="vertical" />
    <el-button type="primary" class="mr-8" link @click="openParagraph(data)">
      <AppIcon iconName="app-reference-outlined" class="mr-4"></AppIcon>
      引用分段 {{ data.paragraph_list?.length || 0 }}</el-button
    >
  </div>
  <div class="mt-8" v-if="!isWorkFlow(props.type)">
    <el-space wrap>
      <div v-for="(paragraph, index) in uniqueParagraphList" :key="index">
        <el-icon class="mr-4" :size="25">
          <img :src="getIconPath(paragraph.document_name)" style="width: 90%" alt="" />
        </el-icon>
        <span
          v-if="!paragraph.source_url"
          class="ellipsis"
          :title="paragraph?.document_name?.trim()"
        >
          {{ paragraph?.document_name }}
        </span>
        <a
          v-else
          @click="openLink(paragraph.source_url)"
          class="ellipsis"
          :title="paragraph?.document_name?.trim()"
        >
          <span :title="paragraph?.document_name?.trim()">
            {{ paragraph?.document_name }}
          </span>
        </a>
      </div>
    </el-space>
  </div>

  <div class="border-t color-secondary flex-between mt-12" style="padding-top: 12px">
    <div>
      <span class="mr-8"> 消耗 tokens: {{ data?.message_tokens + data?.answer_tokens }} </span>
      <span> 耗时: {{ data?.run_time?.toFixed(2) }} s</span>
    </div>
    <el-button
      v-if="isWorkFlow(props.type)"
      type="primary"
      link
      @click="openExecutionDetail(data.execution_details)"
    >
      <el-icon class="mr-4"><Document /></el-icon>
      执行详情</el-button
    >
  </div>
  <!-- 知识库引用 dialog -->
  <ParagraphSourceDialog ref="ParagraphSourceDialogRef" />
  <!-- 执行详情 dialog -->
  <ExecutionDetailDialog ref="ExecutionDetailDialogRef" />
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import ParagraphSourceDialog from './ParagraphSourceDialog.vue'
import ExecutionDetailDialog from './ExecutionDetailDialog.vue'
import { isWorkFlow } from '@/utils/application'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  type: {
    type: String,
    default: ''
  }
})
const iconMap: { [key: string]: string } = {
  doc: '../../assets/doc-icon.svg',
  docx: '../../assets/docx-icon.svg',
  pdf: '../../assets/pdf-icon.svg',
  md: '../../assets/md-icon.svg',
  txt: '../../assets/txt-icon.svg',
  xls: '../../assets/xls-icon.svg',
  xlsx: '../../assets/xlsx-icon.svg'
}

const ParagraphSourceDialogRef = ref()
const ExecutionDetailDialogRef = ref()
function openParagraph(row: any, id?: string) {
  ParagraphSourceDialogRef.value.open(row, id)
}
function openExecutionDetail(row: any) {
  ExecutionDetailDialogRef.value.open(row)
}
const uniqueParagraphList = computed(() => {
  const seen = new Set()
  return (
    props.data.paragraph_list?.filter((paragraph: any) => {
      const key = paragraph.document_name.trim()
      if (seen.has(key)) {
        return false
      }
      seen.add(key)
      // 判断如果 meta 属性不是 {} 需要json解析 转对象
      if (paragraph.meta && typeof paragraph.meta === 'string') {
        paragraph.meta = JSON.parse(paragraph.meta)
        paragraph.source_url = paragraph.meta.source_url
      }
      return true
    }) || []
  )
})

function getIconPath(documentName: string) {
  const extension = documentName.split('.').pop()?.toLowerCase()
  if (!documentName || !extension) return new URL(`${iconMap['doc']}`, import.meta.url).href
  if (iconMap && extension && iconMap[extension]) {
    return new URL(`${iconMap[extension]}`, import.meta.url).href
  }
  return new URL(`${iconMap['doc']}`, import.meta.url).href
}
function openLink(url: string) {
  // 如果url不是以/结尾，加上/
  if (url && !url.endsWith('/')) {
    url += '/'
  }
  window.open(url, '_blank')
}
</script>
<style lang="scss" scoped>
.source_dataset-button {
  background: var(--app-text-color-light-1);
  border: 1px solid #ffffff;
  &:hover {
    border: 1px solid var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    color: var(--el-text-color-primary);
  }
}
</style>
