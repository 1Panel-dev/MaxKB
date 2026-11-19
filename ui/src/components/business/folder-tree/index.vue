<script setup lang="ts">
import { computed, defineAsyncComponent, nextTick, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { FolderSort } from './types'
import type { FolderItem, FolderSource } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import FolderApi from '@/api/admin/workspace/folder'
import ResourceAuthorizationDrawer from '@/components/business/resource-authorization-drawer/index.vue'
import FolderFormDialog from './FolderFormDialog.vue'
import VirtualizedTree from './VirtualizedTree.vue'
import { FOLDER_SORT } from './types'
import { FOLDER_ENTRY_ID } from '@/constants/folder'
import { useStore } from '@/stores'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { getWorkspaceId } from '@/utils/resource-context'
import { perm } from '@/permission'

const { t } = useI18n({ useScope: 'global' })

const folderPermission = computed(() => {
  switch (props.source) {
    case RESOURCE_TYPE.APPLICATION:
      return perm.application.workspace
    case RESOURCE_TYPE.KNOWLEDGE:
      return perm.knowledge.workspace
    default:
      return perm.tool.workspace
  }
})

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

const currentNodeKey = defineModel<string>({ default: () => FOLDER_ENTRY_ID.ALL })
const route = useRoute()
const router = useRouter()
const routeFolderId = route.query.folderId
if (props.showAll && typeof routeFolderId === 'string' && routeFolderId) currentNodeKey.value = routeFolderId

const emit = defineEmits<{ loaded: [folder?: FolderItem]; select: [folder: FolderItem] }>()

const folderEntryKeys = {
  [RESOURCE_TYPE.APPLICATION]: { all: 'application.categories.all', shared: 'application.categories.shared' },
  [RESOURCE_TYPE.KNOWLEDGE]: { all: 'knowledge.categories.all', shared: 'knowledge.categories.shared' },
  [RESOURCE_TYPE.TOOL]: { all: 'tool.categories.all', shared: 'tool.categories.shared' },
} as const satisfies Record<FolderSource, { all: string; shared: string }>

const folderEntries = computed(() => {
  const keys = folderEntryKeys[props.source]
  return {
    all: {
      id: FOLDER_ENTRY_ID.ALL,
      get name() {
        return props.rootLabel || t(keys.all)
      },
    },
    shared: {
      id: FOLDER_ENTRY_ID.SHARED,
      get name() {
        return t(keys.shared)
      },
    },
  }
})

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
  if (props.showAll && route.query.folderId !== undefined) {
    void router.replace({ query: { ...route.query, folderId: undefined } })
  }
  emit('select', folder)
}

/* 排序 */
const { user } = useStore()
const workspaceId = getWorkspaceId()
const CUSTOM_FOLDER_SORT = `${user.userInfo?.id}-${workspaceId}-${props.source}-folder-custom-sort`
const FOLDER_SORT_TYPE = `${user.userInfo?.id}-${workspaceId}-${props.source}-folder-sort-type`

const sortOptions: { labelKey: string; value: FolderSort; divided?: boolean }[] = [
  { labelKey: 'folder.sort.createdAtAsc', value: FOLDER_SORT.CREATE_TIME_ASC },
  { labelKey: 'folder.sort.createdAtDesc', value: FOLDER_SORT.CREATE_TIME_DESC },
  { labelKey: 'folder.sort.nameAsc', value: FOLDER_SORT.NAME_ASC, divided: true },
  { labelKey: 'folder.sort.nameDesc', value: FOLDER_SORT.NAME_DESC },
  { labelKey: 'folder.sort.custom', value: FOLDER_SORT.CUSTOM, divided: true },
]

const currentSort = ref<FolderSort>(FOLDER_SORT.CREATE_TIME_DESC)
const currentSortIcon = computed(() => {
  if (currentSort.value === FOLDER_SORT.CUSTOM) return 'icon_drag_outlined'
  if (currentSort.value === FOLDER_SORT.CREATE_TIME_ASC || currentSort.value === FOLDER_SORT.NAME_ASC) {
    return 'icon_sort-a-to-z_outlined'
  }
  return 'icon_sort-z-to-a_outlined'
})

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
      MsgSuccess(t('common.messages.moveSuccess'))
      return loadFolders()
    })
    .catch(() => loadFolders())
    .finally(() => {
      loading.value = false
    })
}

/* 文件夹表单 */
const folderFormDialogRef = useTemplateRef<InstanceType<typeof FolderFormDialog>>('folderFormDialogRef')
const formTitleKey = ref('folder.actions.create')

function handleOpenCreateFolder() {
  formTitleKey.value = 'folder.actions.create'
  folderFormDialogRef.value?.open(workspaceId ?? folderEntries.value.all.id)
}

function handleOpenCreateChildFolder(folder: FolderItem) {
  formTitleKey.value = 'folder.actions.createChild'
  folderFormDialogRef.value?.open(folder.id)
}

function handleOpenEditFolder(folder: FolderItem) {
  formTitleKey.value = 'folder.actions.edit'
  folderFormDialogRef.value?.open(folder.id, folder)
}

/* 文件夹资源授权 */
const authorizationWorkspaceId = ref<string>()
const resourceAuthorizationDrawerRef = useTemplateRef<InstanceType<typeof ResourceAuthorizationDrawer>>('resourceAuthorizationDrawerRef')

function handleOpenResourceAuthorization(folder: FolderItem) {
  authorizationWorkspaceId.value = folder.workspace_id
  return nextTick(() => resourceAuthorizationDrawerRef.value?.open(folder.id, folder))
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
  MsgConfirm(`${t('folder.delete.title')}: ${folder.name}?`, t('folder.delete.description'), {
    cancelButtonText: t('common.actions.cancel'),
    confirmButtonText: t('common.actions.delete'),
  })
    .then(() => {
      loading.value = true
      const { positionCache, targetFolder } = getFolderDeleteContext(folder)
      return FolderApi.deleteFolder(folder.id, props.source).then(() => {
        writeCustomPositions(positionCache)
        MsgSuccess(t('common.messages.deleteSuccess'))

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
  if (currentNodeKey.value === FOLDER_ENTRY_ID.ALL && props.showAll) return folderEntries.value.all
  if (currentNodeKey.value === FOLDER_ENTRY_ID.SHARED && props.showShared) return folderEntries.value.shared

  return findFolderById(folderTreeData.value, currentNodeKey.value) ?? (props.showAll ? folderEntries.value.all : sortTreeData.value[0])
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
  moveToDialogRef.value?.open(folder.id ?? FOLDER_ENTRY_ID.ALL)
}

function handleMoveFolder(targetFolderId: string) {
  if (moveSubmitting.value || !movingFolder.value) return
  const folder = movingFolder.value
  moveSubmitting.value = true
  return FolderApi.putFolder(folder.id, props.source, { parent_id: targetFolderId })
    .then((updatedFolder) => {
      MsgSuccess(t('common.messages.moveSuccess'))
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
  <div v-loading="loading" class="flex-column min-h-0 flex-1">
    <div class="flex-align-center shrink-0 gap-2 px-4 pb-2">
      <MkSearchInput v-model="searchKeyword" :placeholder="t('common.placeholders.search')" class="min-w-0 flex-1" />
      <MkDropdown trigger="click" placement="bottom-end">
        <!-- 选择文件夹排序方式 -->
        <el-button plain class="shrink-0 min-w-8! w-8!">
          <MkIcon :name="currentSortIcon" />
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
              {{ t(option.labelKey) }}
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

      <MkListItem v-if="showAll" :active="currentNodeKey === folderEntries.all.id" @click="handleFolderClick(folderEntries.all)">
        <MkIcon :name="currentNodeKey === folderEntries.all.id ? 'icon_card_filled' : 'icon_card_outlined'" :size="18" class="mr-2" />
        <span>{{ folderEntries.all.name }}</span>
      </MkListItem>
    </div>

    <div class="min-h-0 flex-1 pl-4 pr-1 pb-4">
      <VirtualizedTree
        :currentNodeKey="currentNodeKey"
        :canEdit="canEdit"
        :data="selectableTreeData"
        :filter-text="searchKeyword"
        @node-drop="handleFolderDrop"
        @node-click="handleFolderClick"
        :draggable="draggable"
      >
        <template #default="{ node }">
          <MkIcon name="icon_file-folder_colorful" class="mr-2" :size="18" />
          <span class="min-w-0 flex-1 truncate" :title="node.name">
            {{ node.name }}
          </span>
        </template>

        <template v-if="canEdit" #action-dropdown="{ row }">
          <MkDropdownItem v-if="folderPermission.folderCreate(row.id)" @click="handleOpenCreateChildFolder(row)">
            <template #icon><MkIcon name="icon_add-folder_outlined" /></template>
            <span>{{ t('folder.actions.createChild') }}</span>
          </MkDropdownItem>
          <MkDropdownItem v-if="folderPermission.folderEdit(row.id)" @click="handleOpenEditFolder(row)">
            <template #icon><MkIcon name="icon_edit_outlined" /></template>
            <span>{{ t('common.actions.edit') }}</span>
          </MkDropdownItem>
          <MkDropdownItem v-if="folderPermission.folderEdit(row.id)" @click="handleOpenMoveFolder(row)">
            <template #icon><MkIcon name="icon_move2_outlined" /></template>
            <span>{{ t('folder.actions.moveTo') }}</span>
          </MkDropdownItem>
          <MkDropdownItem v-if="folderPermission.folderAuth(row.id)" @click="handleOpenResourceAuthorization(row)">
            <template #icon><MkIcon name="icon_passkeys_outlined" /></template>
            <span>{{ t('authorization.resource.title') }}</span>
          </MkDropdownItem>
          <MkDropdownItem v-if="folderPermission.folderDelete(row.id)" divided @click="handleDeleteFolder(row)">
            <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
            <span>{{ t('common.actions.delete') }}</span>
          </MkDropdownItem>
        </template>
      </VirtualizedTree>
    </div>

    <FolderFormDialog ref="folderFormDialogRef" :title="t(formTitleKey)" :source="props.source" @refresh="handleFolderRefresh" />
    <MoveToDialog v-if="canEdit" ref="moveToDialogRef" :loading="moveSubmitting" :source="props.source" @submit="handleMoveFolder" />
    <ResourceAuthorizationDrawer
      v-if="canEdit"
      ref="resourceAuthorizationDrawerRef"
      :type="source"
      :workspace-id="authorizationWorkspaceId"
      is-folder
    />
  </div>
</template>
