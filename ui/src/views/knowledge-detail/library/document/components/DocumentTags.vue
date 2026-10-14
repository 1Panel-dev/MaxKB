<script setup lang="ts">
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { DocumentItem } from '@/api/types'
import AddTagDialog from '../action-dropdown/setting-tags/AddTagDialog.vue'

defineOptions({ name: 'DocumentTags' })
const props = defineProps<{
  api?: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['tags']
  knowledgeId: string
  document: DocumentItem
  disabled?: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 优先使用接口数量，兼容只返回标签明细的数据。
const tagCount = computed(() => props.document.tag_count ?? props.document.tags?.length ?? 0)

const dialogMounted = ref(false)
const addTagRef = useTemplateRef<InstanceType<typeof AddTagDialog>>('addTagRef')
const targetKnowledgeId = ref('')

function handleOpenDialog() {
  if (!props.api || props.disabled || loading.value || dialogMounted.value) return
  targetKnowledgeId.value = props.knowledgeId
  const documentId = props.document.id
  dialogMounted.value = true
  return nextTick(() => addTagRef.value?.open([documentId]))
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <div class="flex-align-center gap-1">
    <el-popover v-if="tagCount" trigger="hover" placement="bottom-start" width="auto" :show-after="TOOLTIP_SHOW_DELAY" :persistent="false">
      <template #reference>
        <el-tag type="info" effect="plain" class="shrink-0 cursor-pointer">
          <span class="flex-align-center gap-1 text-N900 py-1">
            <MkIcon name="icon_tag" />
            <span class="text-base">{{ tagCount }}</span>
          </span>
        </el-tag>
      </template>
      <div class="py-2 px-3 max-w-210 space-y-1">
        <template v-for="tag in document.tags" :key="tag.id">
          <div class="flex-align-center gap-2">
            <span class="shrink-0 truncate text-N600" :title="tag.key">{{ tag.key }}</span>
            <span class="min-w-0 truncate" :title="tag.value">{{ tag.value }}</span>
          </div>
        </template>
      </div>
    </el-popover>
    <!-- 添加文档标签 -->
    <el-button class="mk-add-tag-button" plain v-if="!disabled" :disabled="loading" @click.stop="handleOpenDialog">
      <MkIcon name="icon_add_outlined" size="14" />
      <span>标签</span>
    </el-button>
  </div>
  <AddTagDialog
    v-if="dialogMounted && api"
    ref="addTagRef"
    v-model:loading="loading"
    :api="api"
    :knowledge-id="targetKnowledgeId"
    @refresh="emit('refresh')"
    @closed="handleDialogClosed"
  />
</template>
