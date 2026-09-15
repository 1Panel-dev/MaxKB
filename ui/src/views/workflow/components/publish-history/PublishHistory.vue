<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from 'vue'
import { Close, Document, Edit, RefreshLeft, UserFilled } from '@element-plus/icons-vue'
import type WorkflowVersionApi from '@/api/admin/workspace/application/workflow-version'
import type { WorkflowVersion } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import EditPublishVersionDialog from './EditPublishVersionDialog.vue'
import UpdateDescriptionDialog from './UpdateDescriptionDialog.vue'

defineOptions({ name: 'PublishHistory' })

const props = defineProps<{
  resourceId: string
  api: typeof WorkflowVersionApi
  selectedId?: string
  disabled?: boolean
}>()
const emit = defineEmits<{
  preview: [version: WorkflowVersion]
  restore: [version: WorkflowVersion]
  update: [version: WorkflowVersion]
  close: []
}>()

/* 发布历史查询：保留服务端按发布时间倒序返回的顺序。 */
const loading = ref(false)
const versions = ref<WorkflowVersion[]>([])

function loadVersions() {
  loading.value = true
  return props.api
    .getWorkflowVersions(props.resourceId)
    .then((result) => {
      versions.value = result
    })
    .finally(() => {
      loading.value = false
    })
}

function handlePreview(version: WorkflowVersion) {
  if (loading.value || props.disabled) return
  emit('preview', version)
}

function handleRestore(version: WorkflowVersion) {
  if (loading.value || props.disabled) return
  emit('restore', version)
}

/* 编辑版本与更新说明 */
const editDialogRef = useTemplateRef<InstanceType<typeof EditPublishVersionDialog>>('editDialogRef')
const descriptionDialogRef = useTemplateRef<InstanceType<typeof UpdateDescriptionDialog>>('descriptionDialogRef')

function handleEdit(version: WorkflowVersion) {
  if (props.disabled) return
  editDialogRef.value?.open(version)
}

function handleShowDescription(version: WorkflowVersion) {
  descriptionDialogRef.value?.open(version.description ?? '')
}

function handleVersionSaved(version: WorkflowVersion) {
  versions.value = versions.value.map((entry) => (entry.id === version.id ? version : entry))
  emit('update', version)
}

onMounted(loadVersions)
</script>

<template>
  <aside class="absolute right-0 top-0 z-20 flex h-full w-80 max-w-full flex-col rounded-tl-xl bg-white shadow-lg">
    <div class="flex-between shrink-0 border-b px-6 py-4">
      <h4>发布历史</h4>
      <!-- 关闭发布历史 -->
      <el-button text :disabled="disabled" @click="emit('close')"><MkIcon :icon="Close" :size="20" /></el-button>
    </div>
    <el-scrollbar v-loading="loading" class="min-h-0 flex-1">
      <div class="space-y-4 p-2 pt-4">
        <MkListItem
          v-for="(version, index) in versions"
          :key="version.id"
          :active="selectedId === version.id"
          class="rounded-xl! px-4! py-3! text-N900!"
          @click="handlePreview(version)"
        >
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <h6 class="truncate" :title="version.name || datetimeFormat(version.create_time)">
                {{ version.name || datetimeFormat(version.create_time) }}
              </h6>
              <el-tag v-if="index === 0" size="small" class="shrink-0">最近发布</el-tag>
            </div>
            <div class="mt-1 flex items-center gap-1 text-sm font-normal text-N600">
              <el-avatar :size="18" class="shrink-0 bg-primary-gradient! text-white!"><MkIcon :icon="UserFilled" :size="12" /></el-avatar>
              <span class="truncate" :title="`${version.publish_user_name || '-'} 发布于 ${datetimeFormat(version.create_time)}`"
                >{{ version.publish_user_name || '-' }} 发布于 {{ datetimeFormat(version.create_time) }}</span
              >
            </div>
          </div>
          <template #action-dropdown>
            <!-- 编辑版本 -->
            <MkDropdownItem :icon="Edit" :disabled="disabled" @click="handleEdit(version)">编辑</MkDropdownItem>
            <!-- 查看更新说明 -->
            <MkDropdownItem :icon="Document" @click="handleShowDescription(version)">更新说明</MkDropdownItem>
            <!-- 恢复此版本 -->
            <MkDropdownItem :icon="RefreshLeft" :disabled="disabled" @click="handleRestore(version)">恢复此版本</MkDropdownItem>
          </template>
        </MkListItem>
        <MkEmpty v-if="!loading && !versions.length" description="暂无发布历史" />
      </div>
    </el-scrollbar>
    <!-- 编辑发布版本 -->
    <EditPublishVersionDialog ref="editDialogRef" :resource-id="resourceId" :api="api" @saved="handleVersionSaved" />
    <!-- 查看更新说明 -->
    <UpdateDescriptionDialog ref="descriptionDialogRef" />
  </aside>
</template>
