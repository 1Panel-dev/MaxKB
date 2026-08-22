<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import FolderApi from '@/api/admin/workspace/folder'
import type { FolderSource, FolderItem } from '@/api/types'
import { FOLDER_SOURCE } from '@/api/enums'
import { FOLDER_SORT, type FolderSort } from './types'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import { MsgSuccess } from '@/utils/message'
import MkListItem from '@/components/mk-search-list/mk-list-item.vue'
import VirtualizedTree from './VirtualizedTree.vue'
import { useStore } from '@/stores'
import { getWorkspaceId } from '@/utils/workspace-context'

defineOptions({ name: 'FolderTree' })

const props = withDefaults(
  defineProps<{
    canEdit?: boolean
    source: FolderSource
    draggable?: boolean
  }>(),
  {
    canEdit: true,
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

const folderEntries = computed(() => FOLDER_ENTRIES[props.source])
const currentNodeKey = ref<string>(FOLDER_ENTRY_ID.ALL)

const workspaceId = getWorkspaceId()
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
      emit('loaded', folders)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleFolderClick(folder: FolderItem) {
  currentNodeKey.value = folder.id
  emit('select', folder)
}

// 排序
const { user } = useStore()
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

function sortFolders(
  folders: FolderItem[],
  parentId: string,
  positionCache = readCustomPositions(),
): FolderItem[] {
  const customPositions = positionCache[parentId] ?? {}
  const compareMethods: Record<FolderSort, (left: FolderItem, right: FolderItem) => number> = {
    [FOLDER_SORT.CREATE_TIME_ASC]: (left, right) =>
      new Date(left.create_time ?? 0).getTime() - new Date(right.create_time ?? 0).getTime(),
    [FOLDER_SORT.CREATE_TIME_DESC]: (left, right) =>
      new Date(right.create_time ?? 0).getTime() - new Date(left.create_time ?? 0).getTime(),
    [FOLDER_SORT.NAME_ASC]: (left, right) => left.name.localeCompare(right.name),
    [FOLDER_SORT.NAME_DESC]: (left, right) => right.name.localeCompare(left.name),
    [FOLDER_SORT.CUSTOM]: (left, right) =>
      (customPositions[left.id] ?? Number.MAX_SAFE_INTEGER) -
      (customPositions[right.id] ?? Number.MAX_SAFE_INTEGER),
  }

  return [...folders].sort(compareMethods[currentSort.value]).map((folder) => ({
    ...folder,
    children: sortFolders(folder.children ?? [], folder.id, positionCache),
  }))
}

function readCustomPositions(): Record<string, Record<string, number>> {
  const savedPositions = localStorage.getItem(CUSTOM_FOLDER_SORT)
  return savedPositions
    ? (JSON.parse(savedPositions) as Record<string, Record<string, number>>)
    : {}
}

function writeCustomPositions(positionCache: Record<string, Record<string, number>>) {
  localStorage.setItem(CUSTOM_FOLDER_SORT, JSON.stringify(positionCache))
}

function collectCustomPositions(
  parentId: string,
  folders: FolderItem[],
  positionCache: Record<string, Record<string, number>>,
) {
  const savedPositions = positionCache[parentId] ?? {}
  const orderedFolders = [...folders].sort(
    (left, right) =>
      (savedPositions[left.id] ?? Number.MAX_SAFE_INTEGER) -
      (savedPositions[right.id] ?? Number.MAX_SAFE_INTEGER),
  )

  positionCache[parentId] = Object.fromEntries(
    orderedFolders.map((folder, index) => [folder.id, index + 1]),
  )
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

// 拖拽
function findSiblingFolders(
  parentId: string,
  folders = folderTreeData.value,
  currentParentId: string = FOLDER_ENTRY_ID.ALL,
): FolderItem[] {
  if (currentParentId === parentId) return sortFolders(folders, currentParentId)

  for (const folder of folders) {
    const siblingFolders = findSiblingFolders(parentId, folder.children ?? [], folder.id)
    if (siblingFolders.length) return siblingFolders
  }
  return []
}

function saveSiblingOrder(
  draggingFolder: FolderItem,
  targetFolder: FolderItem,
  dropType: 'after' | 'before' | 'inner',
  parentId: string,
) {
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

function handleFolderDrop(
  draggingFolder: FolderItem,
  targetFolder: FolderItem,
  dropType: 'after' | 'before' | 'inner',
) {
  const currentParentId = draggingFolder.parent_id ?? FOLDER_ENTRY_ID.ALL
  const targetParentId =
    (dropType === 'inner' ? targetFolder.id : targetFolder.parent_id) ?? FOLDER_ENTRY_ID.ALL

  if (currentParentId === targetParentId) {
    saveSiblingOrder(draggingFolder, targetFolder, dropType, targetParentId)
    return
  }

  loading.value = true
  return FolderApi.putFolder(draggingFolder.id, props.source, {
    parent_id: targetParentId,
  })
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
// const folderFormDialogRef =
//   useTemplateRef<InstanceType<typeof FolderFormDialog>>('folderFormDialogRef')
// const moveFolderDialogRef =
//   useTemplateRef<InstanceType<typeof MoveFolderDialog>>('moveFolderDialogRef')

// const submiting = ref(false)
// function handleOpenCreateFolder(parentId = workspaceId) {
//   folderFormDialogRef.value?.open(parentId)
// }

// function handleOpenCreateChildFolder(folder: FolderItem) {
//   folderFormDialogRef.value?.open(folder.id)
// }

// function handleOpenEditFolder(folder: FolderItem) {
//   folderFormDialogRef.value?.open(folder.parent_id ?? workspaceId, folder)
// }

// function handleFolderSubmit({ folderId, payload }: FolderFormSubmit) {
//   submiting.value = true
//   const request = folderId
//     ? FolderApi.putFolder(workspaceId, props.source, folderId, payload)
//     : FolderApi.postFolder(workspaceId, props.source, {
//         ...payload,
//         name: payload.name ?? '',
//       })

//   return request
//     .then((folder) => {
//       MsgSuccess(folderId ? '保存成功' : '创建成功')
//       folderFormDialogRef.value?.close()
//       return loadFolders().then(() => {
//         if (folderId) emit('updated', folder)
//         else emit('created', folder)
//       })
//     })
//     .finally(() => {
//       submiting.value = false
//     })
// }

// /* 文件夹移动与删除 */
// function handleOpenMoveFolder(folder: FolderItem) {
//   moveFolderDialogRef.value?.open(folder)
// }

// function handleMoveFolder({ folder, targetFolderId }: FolderMoveSubmit) {
//   submiting.value = true
//   return FolderApi.putFolder(workspaceId, props.source, folder.id, {
//     parent_id: targetFolderId,
//   })
//     .then((updatedFolder) => {
//       MsgSuccess('移动成功')
//       moveFolderDialogRef.value?.close()
//       return loadFolders().then(() => emit('moved', updatedFolder))
//     })
//     .finally(() => {
//       submiting.value = false
//     })
// }

// function handleDeleteFolder(folder: FolderItem) {
//   MsgConfirm(`确认删除文件夹“${folder.name}”？`, '文件夹内的资源也会被删除，请谨慎操作。')
//     .then(() => {
//       submiting.value = true
//       return FolderApi.deleteFolder(props.source, folder.id).then(() => {
//         MsgSuccess('删除成功')
//         return loadFolders().then(() => emit('deleted', folder))
//       })
//     })
//     .catch(() => {})
//     .finally(() => {
//       submiting.value = false
//     })
// }

onMounted(() => {
  const savedSort = localStorage.getItem(FOLDER_SORT_TYPE)
  if (Object.values(FOLDER_SORT).includes(savedSort as FolderSort)) {
    currentSort.value = savedSort as FolderSort
  }
  loadFolders()
})

defineExpose({ refresh: loadFolders })
</script>

<template>
  <div v-loading="loading" class="flex min-h-0 flex-1 flex-col">
    <div class="flex shrink-0 items-center gap-2 px-4 pb-2">
      <MkSearchInput v-model="searchKeyword" class="min-w-0 flex-1" />
      <MkDropdown trigger="click" placement="bottom-end">
        <el-button class="shrink-0 min-w-8! w-8!">
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

    <div class="px-4 mb-1">
      <MkListItem
        v-if="source !== FOLDER_SOURCE.APPLICATION"
        :active="currentNodeKey === folderEntries.shared.id"
        @click="handleFolderClick(folderEntries.shared)"
      >
        <MkIcon
          :name="
            currentNodeKey === folderEntries.shared.id
              ? 'icon_folder-share_filled'
              : 'icon_folder_outlined'
          "
          :size="18"
          class="mr-2"
        />
        <span>{{ folderEntries.shared.name }}</span>
      </MkListItem>

      <el-divider class="my-1!" />

      <MkListItem
        :active="currentNodeKey === folderEntries.all.id"
        @click="handleFolderClick(folderEntries.all)"
      >
        <MkIcon
          :name="
            currentNodeKey === folderEntries.all.id ? 'icon_card_filled' : 'icon_card_outlined'
          "
          :size="18"
          class="mr-2"
        />
        <span>{{ folderEntries.all.name }}</span>
      </MkListItem>
    </div>

    <div class="min-h-0 flex-1">
      <VirtualizedTree
        :currentNodeKey="currentNodeKey"
        :canEdit="canEdit"
        :data="sortTreeData"
        :filter-text="searchKeyword"
        @node-drop="handleFolderDrop"
        @node-click="handleFolderClick"
        :draggable="draggable"
        class="pl-4 pr-1"
      >
        <template #default="{ node }">
          <MkIcon name="icon_file-folder_colorful" class="mr-2" :size="18" />
          <span class="min-w-0 flex-1 truncate" :title="node.name">
            {{ node.name }}
          </span>
        </template>

        <template v-if="canEdit" #action-dropdown>
          <!-- <MkDropdownMenu>
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
          </MkDropdownMenu> -->
        </template>
      </VirtualizedTree>
    </div>

    <!-- <FolderFormDialog ref="folderFormDialogRef" :loading="loading" @submit="handleFolderSubmit" />
    <MoveFolderDialog
      ref="moveFolderDialogRef"
      :folders="folderTree"
      :loading="loading"
      @submit="handleMoveFolder"
    /> -->
  </div>
</template>
