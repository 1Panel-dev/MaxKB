<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import type { FolderSource, WorkspaceFolder } from '@/api/types'
import FolderApi from '@/api/admin/workspace/folder'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import FolderFormDialog from './FolderFormDialog.vue'
import MoveFolderDialog from './MoveFolderDialog.vue'
import FolderVirtualizedTree from './VirtualizedTree.vue'
import { FOLDER_SORT, type FolderFormSubmit, type FolderMoveSubmit, type FolderSort } from './types'

defineOptions({ name: 'FolderTree' })

const props = withDefaults(
  defineProps<{
    canManage?: boolean
    hideRoot?: boolean
    source: FolderSource
    workspaceId: string
  }>(),
  {
    canManage: true,
    hideRoot: true,
  },
)

const emit = defineEmits<{
  created: [folder: WorkspaceFolder]
  deleted: [folder: WorkspaceFolder, selectionAffected: boolean]
  loaded: [folders: WorkspaceFolder[]]
  moved: [folder: WorkspaceFolder]
  select: [folder: WorkspaceFolder]
  updated: [folder: WorkspaceFolder]
}>()

defineSlots<{
  beforeTree?: () => unknown
}>()

const currentNodeKey = defineModel<string>({ default: '' })
const folderFormDialogRef =
  useTemplateRef<InstanceType<typeof FolderFormDialog>>('folderFormDialogRef')
const moveFolderDialogRef =
  useTemplateRef<InstanceType<typeof MoveFolderDialog>>('moveFolderDialogRef')
const loading = ref(false)
const saving = ref(false)
const folderTree = ref<WorkspaceFolder[]>([])
const searchKeyword = ref('')
const currentSort = ref<FolderSort>(FOLDER_SORT.CREATE_TIME_DESC)

const sortOptions: { label: string; value: FolderSort }[] = [
  { label: '创建时间升序', value: FOLDER_SORT.CREATE_TIME_ASC },
  { label: '创建时间降序', value: FOLDER_SORT.CREATE_TIME_DESC },
  { label: '名称升序', value: FOLDER_SORT.NAME_ASC },
  { label: '名称降序', value: FOLDER_SORT.NAME_DESC },
]

const visibleFolders = computed(() => {
  const rootFolder =
    folderTree.value.find(({ id }) => id === props.workspaceId) ?? folderTree.value[0]
  const folders =
    props.hideRoot && rootFolder?.id === props.workspaceId
      ? (rootFolder.children ?? [])
      : folderTree.value

  return sortFolders(folders)
})

function sortFolders(folders: WorkspaceFolder[]): WorkspaceFolder[] {
  const compareMethods: Record<
    FolderSort,
    (left: WorkspaceFolder, right: WorkspaceFolder) => number
  > = {
    [FOLDER_SORT.CREATE_TIME_ASC]: (left, right) =>
      new Date(left.create_time ?? 0).getTime() - new Date(right.create_time ?? 0).getTime(),
    [FOLDER_SORT.CREATE_TIME_DESC]: (left, right) =>
      new Date(right.create_time ?? 0).getTime() - new Date(left.create_time ?? 0).getTime(),
    [FOLDER_SORT.NAME_ASC]: (left, right) => left.name.localeCompare(right.name),
    [FOLDER_SORT.NAME_DESC]: (left, right) => right.name.localeCompare(left.name),
  }

  return [...folders].sort(compareMethods[currentSort.value]).map((folder) => ({
    ...folder,
    children: sortFolders(folder.children ?? []),
  }))
}

function containsFolder(folder: WorkspaceFolder, folderId: string): boolean {
  return (
    folder.id === folderId ||
    Boolean(folder.children?.some((child) => containsFolder(child, folderId)))
  )
}

/* 文件夹树 */
function loadFolders() {
  loading.value = true
  return FolderApi.getFolderTree(props.workspaceId, props.source)
    .then((folders) => {
      folderTree.value = folders
      emit('loaded', folders)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleFolderSelect(folder: WorkspaceFolder) {
  currentNodeKey.value = folder.id
  emit('select', folder)
}

function handleSortSelect(sort: FolderSort) {
  currentSort.value = sort
  localStorage.setItem(`folder-sort:${props.workspaceId}:${props.source}`, sort)
}

/* 文件夹表单 */
function handleOpenCreateFolder(parentId = props.workspaceId) {
  folderFormDialogRef.value?.open(parentId)
}

function handleOpenCreateChildFolder(folder: WorkspaceFolder) {
  folderFormDialogRef.value?.open(folder.id)
}

function handleOpenEditFolder(folder: WorkspaceFolder) {
  folderFormDialogRef.value?.open(folder.parent_id ?? props.workspaceId, folder)
}

function handleFolderSubmit({ folderId, payload }: FolderFormSubmit) {
  saving.value = true
  const request = folderId
    ? FolderApi.putFolder(props.workspaceId, props.source, folderId, payload)
    : FolderApi.postFolder(props.workspaceId, props.source, {
        ...payload,
        name: payload.name ?? '',
      })

  return request
    .then((folder) => {
      MsgSuccess(folderId ? '保存成功' : '创建成功')
      folderFormDialogRef.value?.close()
      return loadFolders().then(() => {
        if (folderId) emit('updated', folder)
        else emit('created', folder)
      })
    })
    .finally(() => {
      saving.value = false
    })
}

/* 文件夹移动与删除 */
function handleOpenMoveFolder(folder: WorkspaceFolder) {
  moveFolderDialogRef.value?.open(folder)
}

function handleMoveFolder({ folder, targetFolderId }: FolderMoveSubmit) {
  saving.value = true
  return FolderApi.putFolder(props.workspaceId, props.source, folder.id, {
    parent_id: targetFolderId,
  })
    .then((updatedFolder) => {
      MsgSuccess('移动成功')
      moveFolderDialogRef.value?.close()
      return loadFolders().then(() => emit('moved', updatedFolder))
    })
    .finally(() => {
      saving.value = false
    })
}

function handleFolderDrop(
  draggingFolder: WorkspaceFolder,
  targetFolder: WorkspaceFolder,
  dropType: 'after' | 'before' | 'inner',
) {
  const targetParentId =
    dropType === 'inner' ? targetFolder.id : (targetFolder.parent_id ?? props.workspaceId)

  if (draggingFolder.parent_id === targetParentId) return loadFolders()

  saving.value = true
  return FolderApi.putFolder(props.workspaceId, props.source, draggingFolder.id, {
    parent_id: targetParentId,
  })
    .then((updatedFolder) => {
      MsgSuccess('移动成功')
      return loadFolders().then(() => emit('moved', updatedFolder))
    })
    .catch(() => loadFolders())
    .finally(() => {
      saving.value = false
    })
}

function handleDeleteFolder(folder: WorkspaceFolder) {
  MsgConfirm(`确认删除文件夹“${folder.name}”？`, '文件夹内的资源也会被删除，请谨慎操作。')
    .then(() => {
      saving.value = true
      const selectionAffected = containsFolder(folder, currentNodeKey.value)
      return FolderApi.deleteFolder(props.workspaceId, props.source, folder.id).then(() => {
        if (selectionAffected) currentNodeKey.value = ''
        MsgSuccess('删除成功')
        return loadFolders().then(() => emit('deleted', folder, selectionAffected))
      })
    })
    .catch(() => {})
    .finally(() => {
      saving.value = false
    })
}

watch(
  () => [props.workspaceId, props.source] as const,
  () => {
    const storedSort = localStorage.getItem(`folder-sort:${props.workspaceId}:${props.source}`)
    if (Object.values(FOLDER_SORT).includes(storedSort as FolderSort)) {
      currentSort.value = storedSort as FolderSort
    }
    loadFolders()
  },
  { immediate: true },
)

defineExpose({ openCreate: handleOpenCreateFolder, refresh: loadFolders })
</script>

<template>
  <div v-loading="loading" class="flex min-h-0 flex-1 flex-col">
    <div class="flex shrink-0 items-center gap-2 px-4 pb-2">
      <MkSearchInput v-model="searchKeyword" class="min-w-0 flex-1" />
      <MkDropdown trigger="click" placement="bottom-end">
        <el-button aria-label="文件夹排序" class="shrink-0 px-2!">
          <MkIcon name="icon_moments-categories_outlined" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu class="w-48">
            <MkDropdownItem
              v-for="option in sortOptions"
              :key="option.value"
              selectable
              :selected="currentSort === option.value"
              @click="handleSortSelect(option.value)"
            >
              {{ option.label }}
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </div>

    <slot name="beforeTree" />

    <div class="min-h-0 flex-1 px-4 pb-4">
      <FolderVirtualizedTree
        :can-manage="canManage"
        :current-node-key="currentNodeKey"
        :data="visibleFolders"
        :draggable="canManage"
        :filter-text="searchKeyword"
        :protected-node-id="workspaceId"
        @create="handleOpenCreateChildFolder"
        @delete="handleDeleteFolder"
        @edit="handleOpenEditFolder"
        @move="handleOpenMoveFolder"
        @node-drop="handleFolderDrop"
        @select="handleFolderSelect"
      />
    </div>

    <FolderFormDialog ref="folderFormDialogRef" :loading="saving" @submit="handleFolderSubmit" />
    <MoveFolderDialog
      ref="moveFolderDialogRef"
      :folders="folderTree"
      :loading="saving"
      @submit="handleMoveFolder"
    />
  </div>
</template>
