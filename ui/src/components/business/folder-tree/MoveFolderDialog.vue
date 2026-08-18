<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WorkspaceFolder } from '@/api/types'
import type { FolderMoveSubmit } from './types'
import FolderVirtualizedTree from './VirtualizedTree.vue'

defineOptions({ name: 'MoveFolderDialog' })

const props = defineProps<{
  folders: WorkspaceFolder[]
  loading: boolean
}>()

const emit = defineEmits<{
  submit: [form: FolderMoveSubmit]
}>()

interface MoveFolderNode extends Omit<WorkspaceFolder, 'children'> {
  children?: MoveFolderNode[]
  disabled?: boolean
}

const visible = ref(false)
const movingFolder = ref<WorkspaceFolder>()
const selectedTargetId = ref('')
const searchKeyword = ref('')

const canSubmit = computed(
  () => Boolean(selectedTargetId.value) && selectedTargetId.value !== movingFolder.value?.parent_id,
)

const moveFolders = computed<MoveFolderNode[]>(() => {
  const disabledFolderIds = new Set<string>()

  function collectDisabledFolders(folder: WorkspaceFolder) {
    disabledFolderIds.add(folder.id)
    folder.children?.forEach(collectDisabledFolders)
  }

  if (movingFolder.value) collectDisabledFolders(movingFolder.value)

  function mapFolders(folders: WorkspaceFolder[]): MoveFolderNode[] {
    return folders.map((folder) => ({
      ...folder,
      children: mapFolders(folder.children ?? []),
      disabled: disabledFolderIds.has(folder.id),
    }))
  }

  return mapFolders(props.folders)
})

function resetData() {
  movingFolder.value = undefined
  searchKeyword.value = ''
  selectedTargetId.value = ''
}

function open(folder: WorkspaceFolder) {
  resetData()
  movingFolder.value = folder
  visible.value = true
}

function close() {
  visible.value = false
  resetData()
}

function handleTargetSelect(folder: WorkspaceFolder) {
  selectedTargetId.value = folder.id
}

function handleSubmit() {
  if (!movingFolder.value || !canSubmit.value) return
  emit('submit', {
    folder: movingFolder.value,
    targetFolderId: selectedTargetId.value,
  })
}

defineExpose({ close, open })
</script>

<template>
  <MkDialog v-model="visible" title="移动到" width="600" @closed="resetData">
    <div class="flex h-100 flex-col gap-3">
      <MkSearchInput v-model="searchKeyword" class="shrink-0" />
      <div class="min-h-0 flex-1 rounded-md border p-2">
        <FolderVirtualizedTree
          :can-manage="false"
          :current-node-key="selectedTargetId"
          :data="moveFolders"
          :filter-text="searchKeyword"
          @select="handleTargetSelect"
        />
      </div>
    </div>

    <template #footer>
      <el-button :disabled="loading" @click="close">取消</el-button>
      <el-button type="primary" :disabled="!canSubmit" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </MkDialog>
</template>
