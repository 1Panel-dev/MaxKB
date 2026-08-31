<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, useTemplateRef } from 'vue'
import FolderApi from '@/api/admin/workspace/folder'
import type { FolderSource, FolderItem } from '@/api/types'
import { FOLDER_SORT, type FolderSort } from './types'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import VirtualizedTree from './VirtualizedTree.vue'
import FolderFormDialog from './FolderFormDialog.vue'
import { useStore } from '@/stores'
import { getWorkspaceId } from '@/utils/resource-context'

const MoveToDialog = defineAsyncComponent(() => import('./MoveToDialog.vue'))

defineOptions({ name: 'FolderTree' })

const props = withDefaults(
  defineProps<{
    canEdit?: boolean
    disabledFolderIds?: string[]
    draggable?: boolean
    rootLabel?: string
    showAll?: boolean
    showShared?: boolean
    source: FolderSource
  }>(),
  { canEdit: true, disabledFolderIds: () => [], draggable: false, rootLabel: '', showAll: true, showShared: true },
)

const currentNodeKey = defineModel<string>({ default: FOLDER_ENTRY_ID.ALL })

const emit = defineEmits<{ loaded: [folder?: FolderItem]; select: [folder: FolderItem] }>()

const folderEntries = computed(() => FOLDER_ENTRIES[props.source])
const rootFolderEntry = computed(() => ({ ...folderEntries.value.all, name: props.rootLabel || folderEntries.value.all.name }))

interface SelectableFolderItem extends Omit<FolderItem, 'children'> {
  children?: SelectableFolderItem[]
  disabled?: boolean
}

const loading = ref(false)
const folderTreeData = ref<FolderItem[]>([])
const searchKeyword = ref('')

/* 加载文件夹树 */
function loadFolders() {
  loading.value = true
  return FolderApi.getFolderTree(props.source)
    .then((folders) => {
      const rootFolder = folders[0]
      folderTreeData.value = rootFolder?.children ?? []
      if (currentSort.value === FOLDER_SORT.CUSTOM) syncCustomPositions()
    })
    .finally(() => {
      loading.value = false
    })
}

function handleFolderClick(folder: FolderItem) {
  currentNodeKey.value = folder.id
  emit('select', folder)
}

/* 排序 */
const { user } = useStore()
const workspaceId = getWorkspaceId()
const CUSTOM_FOLDER_SORT = `${user.userInfo?.id}-${workspaceId}-${props.source}-folder-custom-sort`
const FOLDER_SORT_TYPE = `${user.userInfo?.id}-${workspaceId}-${props.source}-folder-sort-type`

const sortOptions: { label: string; value: FolderSort; divided?: boolean }[] = [
  { label: '按创建时间升序', value: FOLDER_SORT.CREATE_TIME_ASC },
  { label: '按创建时间降序', value: FOLDER_SORT.CREATE_TIME_DESC },
  { label: '按名称升序', value: FOLDER_SORT.NAME_ASC, divided: true },
  { label: '按名称降序', value: FOLDER_SORT.NAME_DESC },
  { label: '按用户拖拽排序', value: FOLDER_SORT.CUSTOM, divided: true },
]

const currentSort = ref<FolderSort>(FOLDER_SORT.CREATE_TIME_DESC)

const sortTreeData = computed(() => {
  return sortFolders(folderTreeData.value, FOLDER_ENTRY_ID.ALL)
})

const selectableTreeData = computed<SelectableFolderItem[]>(() => {
  const disabledFolderIds = new Set(props.disabledFolderIds)
  if (!disabledFolderIds.size) return sortTreeData.value

  function mapDisabledFolders(folders: FolderItem[]): SelectableFolderItem[] {
    return folders.map((folder) => ({ ...folder, children: mapDisabledFolders(folder.children ?? []), disabled: disabledFolderIds.has(folder.id) }))
  }

  return mapDisabledFolders(sortTreeData.value)
})

function sortFolders(folders: FolderItem[], parentId: string, positionCache = readCustomPositions()): FolderItem[] {
  const customPositions = positionCache[parentId] ?? {}
  const compareMethods: Record<FolderSort, (left: FolderItem, right: FolderItem) => number> = {
    [FOLDER_SORT.CREATE_TIME_ASC]: (left, right) => new Date(left.create_time ?? 0).getTime() - new Date(right.create_time ?? 0).getTime(),
    [FOLDER_SORT.CREATE_TIME_DESC]: (left, right) => new Date(right.create_time ?? 0).getTime() - new Date(left.create_time ?? 0).getTime(),
    [FOLDER_SORT.NAME_ASC]: (left, right) => left.name.localeCompare(right.name),
    [FOLDER_SORT.NAME_DESC]: (left, right) => right.name.localeCompare(left.name),
    [FOLDER_SORT.CUSTOM]: (left, right) =>
      (customPositions[left.id] ?? Number.MAX_SAFE_INTEGER) - (customPositions[right.id] ?? Number.MAX_SAFE_INTEGER),
  }

  return [...folders]
    .sort(compareMethods[currentSort.value])
    .map((folder) => ({ ...folder, children: sortFolders(folder.children ?? [], folder.id, positionCache) }))
}

function readCustomPositions(): Record<string, Record<string, number>> {
  const savedPositions = localStorage.getItem(CUSTOM_FOLDER_SORT)
  return savedPositions ? (JSON.parse(savedPositions) as Record<string, Record<string, number>>) : {}
}

function writeCustomPositions(positionCache: Record<string, Record<string, number>>) {
  localStorage.setItem(CUSTOM_FOLDER_SORT, JSON.stringify(positionCache))
}

function collectCustomPositions(parentId: string, folders: FolderItem[], positionCache: Record<string, Record<string, number>>) {
  const savedPositions = positionCache[parentId] ?? {}
  const orderedFolders = [...folders].sort(
    (left, right) => (savedPositions[left.id] ?? Number.MAX_SAFE_INTEGER) - (savedPositions[right.id] ?? Number.MAX_SAFE_INTEGER),
  )

  positionCache[parentId] = Object.fromEntries(orderedFolders.map((folder, index) => [folder.id, index + 1]))
  orderedFolders.forEach((folder) => {
    collectCustomPositions(folder.id, folder.children ?? [], positionCache)
  })
}

function syncCustomPositions() {
  const positionCache = readCustomPositions()
  collectCustomPositions(FOLDER_ENTRY_ID.ALL, folderTreeData.value, positionCache)
  writeCustomPositions(positionCache)
}

function handleSortSelect(sort: FolderSort) {
  currentSort.value = sort
  localStorage.setItem(FOLDER_SORT_TYPE, sort)
  if (sort === FOLDER_SORT.CUSTOM) syncCustomPositions()
}

/* 拖拽 */
function findSiblingFolders(parentId: string, folders = folderTreeData.value, currentParentId: string = FOLDER_ENTRY_ID.ALL): FolderItem[] {
  if (currentParentId === parentId) return sortFolders(folders, currentParentId)

  for (const folder of folders) {
    const siblingFolders = findSiblingFolders(parentId, folder.children ?? [], folder.id)
    if (siblingFolders.length) return siblingFolders
  }
  return []
}

function saveSiblingOrder(draggingFolder: FolderItem, targetFolder: FolderItem, dropType: 'after' | 'before' | 'inner', parentId: string) {
  const siblingIds = findSiblingFolders(parentId)
    .map(({ id }) => id)
    .filter((id) => id !== draggingFolder.id)
  const targetIndex = dropType === 'inner' ? siblingIds.length : siblingIds.indexOf(targetFolder.id)
  const insertIndex = dropType === 'after' ? targetIndex + 1 : targetIndex

  siblingIds.splice(Math.max(0, insertIndex), 0, draggingFolder.id)
  const positionCache = readCustomPositions()
  positionCache[parentId] = Object.fromEntries(siblingIds.map((id, index) => [id, index + 1]))
  writeCustomPositions(positionCache)
}

function handleFolderDrop(draggingFolder: FolderItem, targetFolder: FolderItem, dropType: 'after' | 'before' | 'inner') {
  const currentParentId = draggingFolder.parent_id ?? FOLDER_ENTRY_ID.ALL
  const targetParentId = (dropType === 'inner' ? targetFolder.id : targetFolder.parent_id) ?? FOLDER_ENTRY_ID.ALL

  if (currentParentId === targetParentId) {
    saveSiblingOrder(draggingFolder, targetFolder, dropType, targetParentId)
    return
  }

  loading.value = true
  return FolderApi.putFolder(draggingFolder.id, props.source, { parent_id: targetParentId })
    .then(() => {
      MsgSuccess('移动成功')
      return loadFolders()
    })
    .catch(() => loadFolders())
    .finally(() => {
      loading.value = false
    })
}

/* 文件夹表单 */
const folderFormDialogRef = useTemplateRef<InstanceType<typeof FolderFormDialog>>('folderFormDialogRef')
const formTitle = ref('')

function handleOpenCreateFolder() {
  formTitle.value = '创建文件夹'
  folderFormDialogRef.value?.open(folderEntries.value.all.id)
}

function handleOpenCreateChildFolder(folder: FolderItem) {
  formTitle.value = '创建子文件夹'
  folderFormDialogRef.value?.open(folder.id)
}

function handleOpenEditFolder(folder: FolderItem) {
  formTitle.value = '编辑文件夹'
  folderFormDialogRef.value?.open(folder.id, folder)
}

// 创建后选中新文件夹；编辑当前文件夹时同步最新信息。
function handleFolderRefresh(folder: FolderItem, isEdit: boolean) {
  return loadFolders().then(() => {
    if (!isEdit || folder.id === currentNodeKey.value) {
      handleFolderClick(folder)
    }
  })
}

/* 删除文件夹：当前选择不受影响时只刷新树。 */

function handleDeleteFolder(folder: FolderItem) {
  MsgConfirm(`确认删除文件夹：${folder.name}？`, '文件夹下的资源会被删除，请谨慎操作。')
    .then(() => {
      loading.value = true
      const { positionCache, targetFolder } = getFolderDeleteContext(folder)
      return FolderApi.deleteFolder(folder.id, props.source).then(() => {
        writeCustomPositions(positionCache)
        MsgSuccess('删除成功')

        // 树重建前先更新激活 ID，让 statHandler 展开目标文件夹的祖先链。
        if (targetFolder) currentNodeKey.value = targetFolder.id
        return loadFolders().then(() => {
          if (targetFolder) {
            handleFolderClick(findFolderById(folderTreeData.value, targetFolder.id) ?? targetFolder)
          }
        })
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function findFolderById(folders: FolderItem[], folderId: string): FolderItem | undefined {
  for (const folder of folders) {
    if (folder.id === folderId) return folder

    const matchedFolder = findFolderById(folder.children ?? [], folderId)
    if (matchedFolder) return matchedFolder
  }
}

function resolveCurrentFolder() {
  if (currentNodeKey.value === FOLDER_ENTRY_ID.ALL && props.showAll) return rootFolderEntry.value
  if (currentNodeKey.value === FOLDER_ENTRY_ID.SHARED && props.showShared) return folderEntries.value.shared

  return findFolderById(folderTreeData.value, currentNodeKey.value) ?? (props.showAll ? rootFolderEntry.value : sortTreeData.value[0])
}

function getFolderDeleteContext(folder: FolderItem) {
  const deletedFolder = findFolderById(folderTreeData.value, folder.id) ?? folder
  const positionCache = readCustomPositions()
  const parentId = deletedFolder.parent_id ?? FOLDER_ENTRY_ID.ALL
  delete positionCache[parentId]?.[deletedFolder.id]

  // 同时清理父级引用和整棵被删子树的缓存分组。
  const subtreeFolders = [deletedFolder]
  while (subtreeFolders.length) {
    const currentFolder = subtreeFolders.pop()
    if (!currentFolder) break
    delete positionCache[currentFolder.id]
    subtreeFolders.push(...(currentFolder.children ?? []))
  }

  if (!findFolderById([deletedFolder], currentNodeKey.value)) return { positionCache }
  if (parentId !== FOLDER_ENTRY_ID.ALL) {
    const targetFolder = findFolderById(folderTreeData.value, parentId) ?? folderEntries.value.all
    return { positionCache, targetFolder }
  }

  // 顶级文件夹按当前展示顺序回退到下一个、上一个或“全部”。
  const siblingFolders = sortTreeData.value
  const folderIndex = siblingFolders.findIndex(({ id }) => id === deletedFolder.id)
  const targetFolder =
    folderIndex < 0 ? folderEntries.value.all : (siblingFolders[folderIndex + 1] ?? siblingFolders[folderIndex - 1] ?? folderEntries.value.all)
  return { positionCache, targetFolder }
}

/* 文件夹移动 */
const moveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('moveToDialogRef')
const moveSubmitting = ref(false)
const movingFolder = ref<FolderItem>()

function handleOpenMoveFolder(folder: FolderItem) {
  movingFolder.value = folder
  moveToDialogRef.value?.open(folder.parent_id ?? FOLDER_ENTRY_ID.ALL)
}

function handleMoveFolder(targetFolderId: string) {
  if (moveSubmitting.value || !movingFolder.value) return
  const folder = movingFolder.value
  moveSubmitting.value = true
  return FolderApi.putFolder(folder.id, props.source, { parent_id: targetFolderId })
    .then((updatedFolder) => {
      MsgSuccess('移动成功')
      moveToDialogRef.value?.close()
      movingFolder.value = undefined
      return loadFolders().then(() => {
        if (updatedFolder.id === currentNodeKey.value) {
          handleFolderClick(findFolderById(folderTreeData.value, updatedFolder.id) ?? updatedFolder)
        }
      })
    })
    .finally(() => {
      moveSubmitting.value = false
    })
}

onMounted(() => {
  const savedSort = localStorage.getItem(FOLDER_SORT_TYPE)
  if (Object.values(FOLDER_SORT).includes(savedSort as FolderSort)) {
    currentSort.value = savedSort as FolderSort
  }
  void loadFolders().then(() => {
    const currentFolder = resolveCurrentFolder()
    if (currentFolder) currentNodeKey.value = currentFolder.id
    emit('loaded', currentFolder)
  })
})

defineExpose({ refresh: loadFolders, openCreate: handleOpenCreateFolder })
</script>

<template>
  <div v-loading="loading" class="flex min-h-0 flex-1 flex-col">
    <div class="flex shrink-0 items-center gap-2 px-4 pb-2">
      <MkSearchInput v-model="searchKeyword" class="min-w-0 flex-1" />
      <MkDropdown trigger="click" placement="bottom-end">
        <el-button plain class="shrink-0 min-w-8! w-8!">
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
              :divided="option.divided"
            >
              {{ option.label }}
            </MkDropdownItem>
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </div>

    <div v-if="showShared || showAll" class="px-4 mb-1">
      <div v-if="showShared">
        <MkListItem :active="currentNodeKey === folderEntries.shared.id" @click="handleFolderClick(folderEntries.shared)">
          <MkIcon :name="currentNodeKey === folderEntries.shared.id ? 'icon_folder-share_filled' : 'icon_folder_outlined'" :size="18" class="mr-2" />
          <span>{{ folderEntries.shared.name }}</span>
        </MkListItem>

        <el-divider class="my-1!" />
      </div>

      <MkListItem v-if="showAll" :active="currentNodeKey === rootFolderEntry.id" @click="handleFolderClick(rootFolderEntry)">
        <MkIcon :name="currentNodeKey === rootFolderEntry.id ? 'icon_card_filled' : 'icon_card_outlined'" :size="18" class="mr-2" />
        <span>{{ rootFolderEntry.name }}</span>
      </MkListItem>
    </div>

    <div class="min-h-0 flex-1">
      <VirtualizedTree
        :currentNodeKey="currentNodeKey"
        :canEdit="canEdit"
        :data="selectableTreeData"
        :filter-text="searchKeyword"
        @node-drop="handleFolderDrop"
        @node-click="handleFolderClick"
        :draggable="draggable"
        class="pl-4 pr-1 pb-4"
      >
        <template #default="{ node }">
          <MkIcon name="icon_file-folder_colorful" class="mr-2" :size="18" />
          <span class="min-w-0 flex-1 truncate" :title="node.name">
            {{ node.name }}
          </span>
        </template>

        <template v-if="canEdit" #action-dropdown="{ row }">
          <MkDropdownItem @click="handleOpenCreateChildFolder(row)">
            <template #icon><MkIcon name="icon_add-folder_outlined" /></template>
            <span>创建子文件夹</span>
          </MkDropdownItem>
          <MkDropdownItem @click="handleOpenEditFolder(row)">
            <template #icon><MkIcon name="icon_edit_outlined" /></template>
            <span>编辑</span>
          </MkDropdownItem>
          <MkDropdownItem @click="handleOpenMoveFolder(row)">
            <template #icon><MkIcon name="icon_move2_outlined" /></template>
            <span>移动到</span>
          </MkDropdownItem>
          <MkDropdownItem divided @click="handleDeleteFolder(row)">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>删除</span>
          </MkDropdownItem>
        </template>
      </VirtualizedTree>
    </div>

    <FolderFormDialog ref="folderFormDialogRef" :title="formTitle" :source="props.source" @refresh="handleFolderRefresh" />
    <MoveToDialog v-if="canEdit" ref="moveToDialogRef" :loading="moveSubmitting" :source="props.source" @submit="handleMoveFolder" />
  </div>
</template>
