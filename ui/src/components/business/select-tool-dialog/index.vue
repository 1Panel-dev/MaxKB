<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SharedApi from '@/api/admin/workspace/shared'
import type { FolderItem, ToolItem, ToolType } from '@/api/types'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants/folder'
import FolderTree from '@/components/business/folder-tree/index.vue'
import MkCardCheckbox from '@/components/mk-card-checkbox/index.vue'

defineOptions({ name: 'SelectToolDialog' })

const props = withDefaults(defineProps<{ excludedIds?: string[]; title?: string; toolTypes?: ToolType[] }>(), {
  excludedIds: () => [],
  title: '工具',
  toolTypes: () => [TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW, TOOL_TYPE.INTERNAL],
})

const emit = defineEmits<{ submit: [tool: (Partial<ToolItem> & { id: string })[]] }>()
const visible = ref(false)
const loading = ref(false)
const searchKeyword = ref('')
const appliedSearchKeyword = ref('')
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.TOOL].all })
const toolOptions = ref<ToolItem[]>([])
const selectedTool = ref<(Partial<ToolItem> & { id: string })[]>([])
const toolLayoutRef = useTemplateRef<{ setScrollTop: (scrollTop: number) => void }>('toolLayoutRef')
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
let dialogVersion = 0

const selectedToolIds = computed(() => selectedTool.value.map(({ id }) => id))

function toggleTool(tool: ToolItem) {
  selectedTool.value = selectedToolIds.value.includes(tool.id)
    ? selectedTool.value.filter(({ id }) => id !== tool.id)
    : [...selectedTool.value, cloneDeep(tool)]
}

// 每次查询一次加载全部结果，忽略切换目录或关闭弹窗前发出的旧请求。
function refreshTool() {
  const version = ++dialogVersion
  loading.value = true
  toolOptions.value = []
  appliedSearchKeyword.value = searchKeyword.value.trim()
  const shared = currentFolder.value.id === FOLDER_ENTRY_ID.SHARED
  const requestApi = shared ? SharedApi : ToolApi
  return requestApi
    .getAllTool({
      tool_type_list: props.toolTypes,
      ...(shared ? {} : { folder_id: currentFolder.value.id }),
      ...(appliedSearchKeyword.value ? { name: appliedSearchKeyword.value } : {}),
    })
    .then((tool) => {
      if (version !== dialogVersion) return
      toolOptions.value = tool.filter(
        (resource) => resource.is_active && props.toolTypes.includes(resource.tool_type) && !props.excludedIds.includes(resource.id),
      )
      // 仅补全已选快照，不因查询结果缺少某个 ID 而删除关联。
      const toolById = new Map(tool.map((tool) => [tool.id, tool]))
      selectedTool.value = selectedTool.value.map((tool) => toolById.get(tool.id) ?? tool)
      return nextTick(() => {
        if (version === dialogVersion) toolLayoutRef.value?.setScrollTop(0)
      })
    })
    .finally(() => {
      if (version === dialogVersion) loading.value = false
    })
}

function refreshResources() {
  folderTreeRef.value?.refresh()
  void refreshTool()
}

function selectFolder(folder?: FolderItem) {
  if (!folder || folder.id === currentFolder.value.id) return
  currentFolder.value = folder
  void refreshTool()
}

function open(tool: (Partial<ToolItem> & { id: string })[]) {
  resetData()
  selectedTool.value = cloneDeep(tool)
  visible.value = true
  void refreshTool()
}

function submit() {
  emit('submit', cloneDeep(selectedTool.value))
  visible.value = false
}
function resetData() {
  dialogVersion++
  loading.value = false
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
  currentFolder.value = { ...FOLDER_ENTRIES[RESOURCE_TYPE.TOOL].all }
  toolOptions.value = []
  selectedTool.value = []
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" :title="title" width="1200" @closed="resetData">
    <template #header="{ titleId }">
      <div class="flex-between pr-8">
        <div class="flex items-center gap-2">
          <h4 :id="titleId">{{ title }}</h4>
        </div>

        <el-button text class="h-7! w-7! min-w-0! p-1!" title="刷新" aria-label="刷新工具" @click="refreshResources">
          <MkIcon name="icon_refresh_outlined" :size="20" />
        </el-button>
      </div>
    </template>

    <MkViewLayout ref="toolLayoutRef" :loading="loading" title="">
      <template #aside>
        <FolderTree ref="folderTreeRef" class="pt-4" :can-edit="false" :source="RESOURCE_TYPE.TOOL" @loaded="selectFolder" @select="selectFolder" />
      </template>
      <template #default="{ Header }">
        <component :is="Header">
          <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
          <MkSearchInput v-model="searchKeyword" class="w-60! shrink-0" @change="refreshTool" />
        </component>

        <template v-if="!loading">
          <div v-if="toolOptions.length" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <template v-for="tool in toolOptions" :key="tool.id">
              <el-popover placement="bottom-start" :width="360" :show-after="500" :persistent="false" popper-class="border-none! rounded-xl!">
                <template #reference>
                  <MkCardCheckbox :model-value="selectedToolIds.includes(tool.id)" :label="tool.name" @update:model-value="toggleTool(tool)">
                    <div class="flex min-w-0 flex-1 items-center gap-2">
                      <ToolIcon :icon="tool.icon" :type="tool.tool_type" class="shrink-0" />
                      <span class="min-w-0 flex-1 truncate" :title="tool.name">{{ tool.name }}</span>
                    </div>
                  </MkCardCheckbox>
                </template>
                <template #default>
                  <MkSourceCard :title="tool.name" :nick_name="tool.nick_name || '-'" :create_time="tool.create_time">
                    <template #icon><ToolIcon :icon="tool.icon" :type="tool.tool_type" /></template>
                    <p class="line-clamp-2" :title="tool.desc || '-'">{{ tool.desc || '-' }}</p>
                  </MkSourceCard>
                </template>
              </el-popover>
            </template>
          </div>
          <MkEmpty v-else class="mt-24" :type="appliedSearchKeyword ? 'search' : 'default'" />
        </template>
      </template>
    </MkViewLayout>
    <template #footer>
      <div class="flex-between -mx-6 border-t px-6 pt-4">
        <div class="flex items-center gap-2">
          <span class="text-N600">已选 {{ selectedTool.length }}</span>
          <el-button v-if="selectedTool.length" link type="primary" @click="selectedTool = []">清空</el-button>
        </div>
        <div>
          <el-button plain @click="visible = false">取消</el-button>
          <el-button type="primary" @click="submit">确定</el-button>
        </div>
      </div>
    </template>
  </MkDialog>
</template>
