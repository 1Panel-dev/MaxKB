<script setup lang="ts">
import { computed, ref } from 'vue'
import type { WorkspaceFolder } from '@/api/types'
import type { FolderMoveSubmit } from './types.ts'
import FolderTree from './index.vue'

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

// function handleMoveFolder({ folder, targetFolderId }: FolderMoveSubmit) {
//   submiting.value = true
//   return FolderApi.putFolder(workspaceId, props.source, folder.id, {
//     parent_id: targetFolderId,
//   })
//     .then((updatedFolder) => {
//       MsgSuccess('移动成功')
//       visible.value = false
//       return loadFolders().then(() => emit('moved', updatedFolder))
//     })
//     .finally(() => {
//       submiting.value = false
//     })
// }

function open(folder: WorkspaceFolder) {
  movingFolder.value = folder
  visible.value = true
}

function resetData() {
  movingFolder.value = undefined
  searchKeyword.value = ''
  selectedTargetId.value = ''
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="移动到" @closed="resetData">
    <FolderTree
      :current-node-key="selectedTargetId"
      :data="moveFolders"
      @select="handleTargetSelect"
    />
    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!canSubmit" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </MkDialog>
</template>
