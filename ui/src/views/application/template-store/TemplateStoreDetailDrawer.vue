<script setup lang="ts">
import { ref } from 'vue'
import type { ApplicationStoreTemplate } from '@/api/types'
import { numberFormat } from '@/utils/number'

defineOptions({ name: 'TemplateStoreDetailDrawer' })

const emit = defineEmits<{ add: [template: ApplicationStoreTemplate]; closed: [] }>()
const visible = ref(false)
const applicationTemplate = ref<ApplicationStoreTemplate>()

function open(template: ApplicationStoreTemplate) {
  applicationTemplate.value = template
  visible.value = true
}

function handleAdd() {
  if (!applicationTemplate.value) return
  emit('add', applicationTemplate.value)
  visible.value = false
}

function handleClosed() {
  applicationTemplate.value = undefined
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="详情" size="60%" @closed="handleClosed">
    <template v-if="applicationTemplate">
      <div class="border-b pb-6 mb-3">
        <div class="flex-between gap-4">
          <div class="flex min-w-0 items-center gap-4">
            <ApplicationIcon :icon="applicationTemplate.icon" :size="60" />
            <div class="min-w-0">
              <h2 class="truncate" :title="applicationTemplate.name">{{ applicationTemplate.name }}</h2>
              <span class="flex items-center gap-1 text-N600">
                <MkIcon name="icon_download_outlined" />
                {{ numberFormat(applicationTemplate.downloads) }}
              </span>
            </div>
          </div>
          <el-button type="primary" @click="handleAdd">应用</el-button>
        </div>
        <p class="mt-3 text-N600">{{ applicationTemplate.desc }}</p>
      </div>
      <MdPreview :model-value="applicationTemplate.readMe || applicationTemplate.desc || '暂无详细说明'" />
    </template>
  </MkDrawer>
</template>
