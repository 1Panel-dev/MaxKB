<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import EditPublishVersionDialog from './EditPublishVersionDialog.vue'
import DescriptionDialog from './DescriptionDialog.vue'

defineOptions({ name: 'PublishHistoryDrawer' })

const visible = defineModel<boolean>({ default: false })

defineProps<{
  versions: WorkflowVersion[]
  loading?: boolean
  saving?: boolean
  selectedId?: string
}>()
const emit = defineEmits<{
  preview: [version: WorkflowVersion]
  restore: [version: WorkflowVersion]
  submit: [payload: WorkflowVersionPayload, versionId: string]
}>()

/* 弹窗展示由公共 UI 管理，编辑请求交给业务组件。 */
const editingVersionId = ref('')
const editDialogRef = useTemplateRef<InstanceType<typeof EditPublishVersionDialog>>('editDialogRef')
const descriptionDialogRef = useTemplateRef<InstanceType<typeof DescriptionDialog>>('descriptionDialogRef')

function handleEdit(version: WorkflowVersion) {
  editingVersionId.value = version.id
  editDialogRef.value?.open(version)
}

function handleSubmit(payload: WorkflowVersionPayload) {
  emit('submit', payload, editingVersionId.value)
}

function handleShowDescription(version: WorkflowVersion) {
  descriptionDialogRef.value?.open(version.publish_desc ?? '')
}

function closeEdit() {
  editDialogRef.value?.close()
}

function handlePreview(version: WorkflowVersion) {
  emit('preview', version)
}

function handleRestore(version: WorkflowVersion) {
  emit('restore', version)
}

defineExpose({ closeEdit })
</script>

<template>
  <MkDrawer
    v-model="visible"
    title="发布历史"
    size="320"
    class="top-header! h-layout-content! max-w-full rounded-tl-xl!"
    content-class="px-2 py-4"
    :modal="false"
    modal-penetrable
    :lock-scroll="false"
  >
    <div v-loading="loading" class="space-y-4">
      <template v-for="(version, index) in versions" :key="version.id">
        <MkListItem :active="selectedId === version.id" @click="handlePreview(version)">
          <div class="min-w-0 flex-1 pl-2">
            <div class="flex items-center gap-2">
              <h6 class="text-N900! truncate" :title="version.name || datetimeFormat(version.create_time)">
                {{ version.name || datetimeFormat(version.create_time) }}
              </h6>
              <el-tag v-if="index === 0" size="small" class="shrink-0">最近发布</el-tag>
            </div>
            <div class="mt-1 flex items-center gap-1">
              <el-avatar :size="18" class="bg-primary-gradient!">
                <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 54%" />
              </el-avatar>
              <span
                class="truncate text-N600! text-sm font-normal!"
                :title="`${version.publish_user_name || '-'} 发布于 ${datetimeFormat(version.create_time)}`"
                >{{ version.publish_user_name || '-' }} 发布于 {{ datetimeFormat(version.create_time) }}</span
              >
            </div>
          </div>
          <template #action-dropdown>
            <!-- 编辑版本 -->
            <MkDropdownItem @click="handleEdit(version)">
              <template #icon><MkIcon name="icon_edit_outlined" /></template>
              <span>编辑</span>
            </MkDropdownItem>
            <!-- 恢复此版本 -->
            <MkDropdownItem @click="handleRestore(version)">
              <template #icon><MkIcon name="icon_reset_outlined" /></template>
              <span>恢复此版本</span>
            </MkDropdownItem>
            <!-- 查看更新说明 -->
            <MkDropdownItem @click="handleShowDescription(version)">
              <template #icon><MkIcon name="icon_info_outlined" /></template>
              <span>更新说明</span>
            </MkDropdownItem>
          </template>
        </MkListItem>
      </template>
      <MkEmpty v-if="!loading && !versions.length" />
    </div>
  </MkDrawer>
  <!-- 编辑版本 -->
  <EditPublishVersionDialog ref="editDialogRef" :saving="saving" @submit="handleSubmit" />
  <!-- 查看更新说明 -->
  <DescriptionDialog ref="descriptionDialogRef" />
</template>
