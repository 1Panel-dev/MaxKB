<script setup lang="ts">
import { ref } from 'vue'
import type { WorkflowStoreTemplate } from '@/api/types'
import { resetUrl } from '@/utils/icon'
import { numberFormat } from '@/utils/number'

defineOptions({ name: 'TemplateStoreDetailDrawer' })

const props = defineProps<{ resource: 'application' | 'knowledge' | 'tool'; disabled?: boolean }>()
const emit = defineEmits<{ use: [template: WorkflowStoreTemplate]; closed: [] }>()
const visible = ref(false)
const workflowTemplate = ref<WorkflowStoreTemplate>()

function open(template: WorkflowStoreTemplate) {
  workflowTemplate.value = template
  visible.value = true
}

function handleUse() {
  if (!workflowTemplate.value || props.disabled) return
  emit('use', workflowTemplate.value)
  visible.value = false
}

function handleClosed() {
  workflowTemplate.value = undefined
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="详情" size="60%" @closed="handleClosed">
    <template v-if="workflowTemplate">
      <div class="border-b pb-6 mb-3">
        <div class="flex-between gap-4">
          <div class="flex min-w-0 items-center gap-4">
            <el-avatar class="bg-transparent!" shape="square" :size="60">
              <img :src="resetUrl(workflowTemplate.icon, true)" alt="" />
            </el-avatar>
            <div class="min-w-0">
              <h2 class="truncate" :title="workflowTemplate.name">{{ workflowTemplate.name }}</h2>
              <span class="flex items-center gap-1 text-N600">
                <MkIcon name="icon_download_outlined" />
                {{ numberFormat(workflowTemplate.downloads) }}
              </span>
            </div>
          </div>
          <!-- 使用模板 -->
          <el-button type="primary" :disabled="disabled" @click="handleUse">应用</el-button>
        </div>
        <p class="mt-3 text-N600">{{ workflowTemplate.desc }}</p>
      </div>
      <MdPreview :model-value="workflowTemplate.readMe || workflowTemplate.desc || '暂无详细说明'" />
    </template>
  </MkDrawer>
</template>
