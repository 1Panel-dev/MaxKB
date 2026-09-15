<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import StoreApi from '@/api/admin/store.ts'
import type { ApplicationStoreTemplate } from '@/api/types'
import TemplateCard from './components/TemplateCard.vue'
import AdvancedCreateDialog from '../create-application/AdvancedCreateDialog.vue'

defineOptions({ name: 'TemplateStoreDialog' })

const props = withDefaults(
  defineProps<{
    source?: 'application' | 'work_flow'
    applying?: boolean
  }>(),
  { source: 'application', applying: false },
)

const emit = defineEmits<{ use: [template: ApplicationStoreTemplate] }>()

/* 模板查询 */
const visible = ref(false)
const loading = ref(false)
const folderId = ref('default')
const searchKeyword = ref('')
const appliedSearchKeyword = ref('')
const applicationTemplates = ref<ApplicationStoreTemplate[]>([])
const hasSearchKeyword = computed(() => Boolean(appliedSearchKeyword.value))
function loadTemplates() {
  loading.value = true
  applicationTemplates.value = []
  appliedSearchKeyword.value = searchKeyword.value.trim()
  const query = appliedSearchKeyword.value ? { name: appliedSearchKeyword.value } : undefined
  return StoreApi.getStoreApplicationList(query)
    .then((response) => {
      applicationTemplates.value = response.apps.map((template) => ({ ...template, desc: template.description ?? template.desc }))
    })
    .finally(() => {
      loading.value = false
    })
}

function resetData() {
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
  applicationTemplates.value = []
}

function open(targetFolderId = 'default') {
  folderId.value = targetFolderId || 'default'
  visible.value = true
  loadTemplates()
}

/* 创建模板智能体：统一管理创建弹窗及成功刷新。 */
const createDialogMounted = ref(false)
const createDialogRef = useTemplateRef<InstanceType<typeof AdvancedCreateDialog>>('createDialogRef')

/* 工作流使用交给页面处理，普通模式打开创建弹窗。 */
function handleUseTemplate(template: ApplicationStoreTemplate) {
  if (props.applying) return
  if (props.source === 'work_flow') {
    emit('use', template)
    return
  }
  if (createDialogMounted.value) return
  createDialogMounted.value = true
  nextTick(() => createDialogRef.value?.open(template))
}

function close() {
  visible.value = false
}

function handleBeforeClose(done: () => void) {
  if (!props.applying) done()
}

function handleUseSuccess() {
  visible.value = false
}

function handleClosed() {
  resetData()
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog
    v-model="visible"
    align-center
    class="mk-aside-content-dialog"
    title="模板中心"
    width="1200"
    :before-close="handleBeforeClose"
    :show-close="!applying"
    @closed="handleClosed"
  >
    <template #header="{ titleId }">
      <div class="relative flex items-center">
        <h4 :id="titleId">模板中心</h4>
        <MkSearchInput
          v-model="searchKeyword"
          class="absolute left-1/2 w-80! -translate-x-2/3"
          placeholder="搜索"
          :disabled="applying"
          @change="loadTemplates"
        />
      </div>
    </template>
    <div v-loading="loading || applying" class="px-6 py-4">
      <div v-if="hasSearchKeyword" class="mb-4 font-semibold">
        找到 <span class="text-primary">{{ applicationTemplates.length }}</span> 个相关模板
      </div>
      <div class="mk-resource-card-grid-sm">
        <template v-for="template in applicationTemplates" :key="template.id">
          <TemplateCard :template="template" @use="handleUseTemplate" />
        </template>
      </div>
      <MkEmpty v-if="!applicationTemplates.length" :type="hasSearchKeyword ? 'search' : 'default'" />
    </div>
  </MkDialog>
  <AdvancedCreateDialog
    v-if="createDialogMounted"
    ref="createDialogRef"
    :folder-id="folderId"
    @refresh="handleUseSuccess"
    @closed="createDialogMounted = false"
  />
</template>
