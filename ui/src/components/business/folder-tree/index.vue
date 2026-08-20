<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import type { FolderSource, FolderItem } from '@/api/types'
import FolderApi from '@/api/admin/workspace/folder'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import MkListItem from '@/components/mk-search-list/mk-list-item.vue'
import FolderFormDialog from './FolderFormDialog.vue'
import MoveFolderDialog from './MoveFolderDialog.vue'
import VirtualizedTree from './VirtualizedTree.vue'
import { FOLDER_SORT, type FolderFormSubmit, type FolderMoveSubmit, type FolderSort } from './types'

defineOptions({ name: 'FolderTree' })

const route = useRoute()
const {
  params: { workspaceId },
} = route

const props = withDefaults(
  defineProps<{
    canEdit?: boolean
    hideRoot?: boolean
    source: FolderSource
  }>(),
  {
    canEdit: true,
    hideRoot: true,
  },
)

const emit = defineEmits<{
  created: [folder: FolderItem]
  deleted: [folder: FolderItem, selectionAffected: boolean]
  loaded: [folders: FolderItem[]]
  moved: [folder: FolderItem]
  select: [folder: FolderItem]
  updated: [folder: FolderItem]
}>()

defineSlots<{
  beforeTree?: () => unknown
}>()

const ALL_FOLDER: FolderItem = {
  name: '全部模型',
  id: 'default',
}
const SHARED_FOLDER: FolderItem = {
  id: 'shared',
  name: '共享模型',
}

const currentNodeKey = defineModel<string>({ default: '' })
const folderFormDialogRef =
  useTemplateRef<InstanceType<typeof FolderFormDialog>>('folderFormDialogRef')
const moveFolderDialogRef =
  useTemplateRef<InstanceType<typeof MoveFolderDialog>>('moveFolderDialogRef')
const loading = ref(false)
const saving = ref(false)
const folderTree = ref<FolderItem[]>([])
const searchKeyword = ref('')
const currentSort = ref<FolderSort>(FOLDER_SORT.CREATE_TIME_DESC)

const sortOptions: { label: string; value: FolderSort }[] = [
  { label: '创建时间升序', value: FOLDER_SORT.CREATE_TIME_ASC },
  { label: '创建时间降序', value: FOLDER_SORT.CREATE_TIME_DESC },
  { label: '名称升序', value: FOLDER_SORT.NAME_ASC },
  { label: '名称降序', value: FOLDER_SORT.NAME_DESC },
]

const visibleFolders = computed(() => {
  const rootFolder = folderTree.value.find(({ id }) => id === workspaceId) ?? folderTree.value[0]
  const folders =
    props.hideRoot && rootFolder?.id === workspaceId
      ? (rootFolder.children ?? [])
      : folderTree.value

  return sortFolders(folders)
})

function sortFolders(folders: FolderItem[]): FolderItem[] {
  const compareMethods: Record<FolderSort, (left: FolderItem, right: FolderItem) => number> = {
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

function containsFolder(folder: FolderItem, folderId: string): boolean {
  return (
    folder.id === folderId ||
    Boolean(folder.children?.some((child) => containsFolder(child, folderId)))
  )
}

/* 文件夹树 */
function loadFolders() {
  loading.value = true
  return FolderApi.getFolderTree(props.source)
    .then((folders) => {
      folderTree.value = folders
      emit('loaded', folders)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleFolderSelect(folder: FolderItem) {
  currentNodeKey.value = folder.id
  emit('select', folder)
}

function handleSortSelect(sort: FolderSort) {
  currentSort.value = sort
  localStorage.setItem(`folder-sort:${workspaceId}:${props.source}`, sort)
}

/* 文件夹表单 */
function handleOpenCreateFolder(parentId = workspaceId) {
  folderFormDialogRef.value?.open(parentId)
}

function handleOpenCreateChildFolder(folder: FolderItem) {
  folderFormDialogRef.value?.open(folder.id)
}

function handleOpenEditFolder(folder: FolderItem) {
  folderFormDialogRef.value?.open(folder.parent_id ?? workspaceId, folder)
}

function handleFolderSubmit({ folderId, payload }: FolderFormSubmit) {
  saving.value = true
  const request = folderId
    ? FolderApi.putFolder(workspaceId, props.source, folderId, payload)
    : FolderApi.postFolder(workspaceId, props.source, {
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
function handleOpenMoveFolder(folder: FolderItem) {
  moveFolderDialogRef.value?.open(folder)
}

function handleMoveFolder({ folder, targetFolderId }: FolderMoveSubmit) {
  saving.value = true
  return FolderApi.putFolder(workspaceId, props.source, folder.id, {
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
  draggingFolder: FolderItem,
  targetFolder: FolderItem,
  dropType: 'after' | 'before' | 'inner',
) {
  const targetParentId =
    dropType === 'inner' ? targetFolder.id : (targetFolder.parent_id ?? workspaceId)

  if (draggingFolder.parent_id === targetParentId) return loadFolders()

  saving.value = true
  return FolderApi.putFolder(workspaceId, props.source, draggingFolder.id, {
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

function handleDeleteFolder(folder: FolderItem) {
  MsgConfirm(`确认删除文件夹“${folder.name}”？`, '文件夹内的资源也会被删除，请谨慎操作。')
    .then(() => {
      saving.value = true
      const selectionAffected = containsFolder(folder, currentNodeKey.value)
      return FolderApi.deleteFolder(workspaceId, props.source, folder.id).then(() => {
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

onMounted(() => {
  loadFolders()
})

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

    <div class="px-4">
      <MkListItem
        :active="currentNodeKey === SHARED_FOLDER.id"
        @click="handleFolderSelect(SHARED_FOLDER)"
      >
        <MkIcon
          :name="
            currentNodeKey === SHARED_FOLDER.id
              ? 'icon_folder-share_filled'
              : 'icon_folder_outlined'
          "
          :size="18"
          class="mr-2"
        />
        <span>共享模型</span>
      </MkListItem>

      <el-divider class="my-1!" />

      <MkListItem
        :active="currentNodeKey === ALL_FOLDER.id"
        @click="handleFolderSelect(ALL_FOLDER)"
      >
        <MkIcon
          :name="currentNodeKey === ALL_FOLDER.id ? 'icon_card_filled' : 'icon_card_outlined'"
          :size="18"
          class="mr-2"
        />
        <span>全部模型</span>
      </MkListItem>
    </div>

    <div class="min-h-0 flex-1">
      <VirtualizedTree
        :canEdit="canEdit"
        :data="visibleFolders"
        :filter-text="searchKeyword"
        @node-drop="handleFolderDrop"
        @node-click="handleFolderSelect"
      >
        <template #default="{ node }">
          <MkIcon name="icon_file-folder_colorful" class="mr-2" :size="18" />
          <span class="min-w-0 flex-1 truncate" :title="node.name">
            {{ node.name }}
          </span>
        </template>

        <template v-if="canEdit" #action-dropdown="{ row }">
          <MkDropdownMenu>
            <MkDropdownItem @click="handleOpenEditFolder(row)">
              <template #icon><MkIcon name="icon_add_outlined" /></template>
              <span>创建子文件夹</span>
            </MkDropdownItem>
            <MkDropdownItem @click="handleOpenEditFolder(row)">
              <template #icon><MkIcon name="icon_edit_outlined" /></template>
              <span>编辑</span>
            </MkDropdownItem>
            <MkDropdownItem @click="handleOpenEditFolder(row)">
              <template #icon><MkIcon name="icon_right_outlined" /></template>
              <span>移动到</span>
            </MkDropdownItem>
            <MkDropdownItem divided @click="handleDeleteFolder(row)">
              <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
              <span>删除</span>
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </VirtualizedTree>
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
