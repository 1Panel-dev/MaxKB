<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WorkflowStoreTemplate } from '@/api/types'
import TemplateCard from './components/TemplateCard.vue'

defineOptions({ name: 'TemplateStoreDialog' })
const props = defineProps<{
  templates: WorkflowStoreTemplate[]
  resource: 'application' | 'knowledge' | 'tool'
  loading?: boolean
}>()
const emit = defineEmits<{
  search: [keyword: string]
  use: [template: WorkflowStoreTemplate]
}>()
const visible = ref(false)
const searchKeyword = ref('')
const appliedSearchKeyword = ref('')
const hasSearchKeyword = computed(() => Boolean(appliedSearchKeyword.value))

function handleSearch() {
  appliedSearchKeyword.value = searchKeyword.value.trim()
  emit('search', appliedSearchKeyword.value)
}

function resetData() {
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
}

function open() {
  resetData()
  visible.value = true
  handleSearch()
}

function close() {
  visible.value = false
}

function handleUseTemplate(template: WorkflowStoreTemplate) {
  if (!props.loading) emit('use', template)
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" title="模板中心" width="1200" @closed="resetData">
    <template #header="{ titleId }">
      <div class="relative flex-align-center">
        <h4 :id="titleId">模板中心</h4>
        <MkSearchInput
          v-model="searchKeyword"
          class="absolute left-1/2 w-80! -translate-x-2/3"
          placeholder="搜索"
          :disabled="loading"
          @change="handleSearch"
        />
      </div>
    </template>
    <div v-loading="loading" class="px-6 py-4">
      <div v-if="hasSearchKeyword" class="mb-4 font-semibold">
        找到 <span class="text-primary">{{ templates.length }}</span> 个相关模板
      </div>
      <div class="mk-resource-card-grid-sm">
        <template v-for="template in templates" :key="template.id">
          <TemplateCard :template="template" :resource="resource" :disabled="loading" @use="handleUseTemplate" />
        </template>
      </div>
      <MkEmpty v-if="!loading && !templates.length" :type="hasSearchKeyword ? 'search' : 'default'" />
    </div>
  </MkDialog>
</template>
