<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef, watch } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { FolderItem, ToolItem, ToolType } from '@/api/types'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import ToolApi from '@/api/admin/workspace/tool/tool'
import FolderTree from '@/components/business/folder-tree/index.vue'
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'
import { FOLDER_ENTRY_ID } from '@/constants/folder'
import { isSystemResource, isSystemSharedResource, isWorkspaceResource } from '@/utils/resource-context'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'SelectToolDialog' })

const props = withDefaults(defineProps<{ excludedIds?: string[]; title?: string; toolTypes?: ToolType[]; workspaceId?: string | null }>(), {
  excludedIds: () => [],
  toolTypes: () => [TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW, TOOL_TYPE.INTERNAL],
})

const emit = defineEmits<{ submit: [tool: (Partial<ToolItem> & { id: string })[]] }>()
const visible = ref(false)
const loading = ref(false)
const searchKeyword = ref('')
const appliedSearchKeyword = ref('')
const selectedFolder = ref<FolderItem>()
const currentFolder = computed<FolderItem>(() => selectedFolder.value ?? { id: FOLDER_ENTRY_ID.ALL, name: t('tool.categories.all') })
const toolOptions = ref<ToolItem[]>([])
const selectedTool = ref<(Partial<ToolItem> & { id: string })[]>([])
const toolLayoutRef = useTemplateRef<{ setScrollTop: (scrollTop: number) => void }>('toolLayoutRef')
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')

const isWorkspaceScope = computed(() => isWorkspaceResource())

const selectedToolIds = computed(() => selectedTool.value.map(({ id }) => id))

function toggleTool(tool: ToolItem) {
  selectedTool.value = selectedToolIds.value.includes(tool.id)
    ? selectedTool.value.filter(({ id }) => id !== tool.id)
    : [...selectedTool.value, cloneDeep(tool)]
}

// 每次查询一次加载全部结果。
function refreshTool() {
  toolOptions.value = []
  if (isSystemResource() && !props.workspaceId) return Promise.resolve()
  loading.value = true
  appliedSearchKeyword.value = searchKeyword.value.trim()
  const requestApi = isSystemResource() ? SystemToolApi : isSystemSharedResource() ? SystemSharedToolApi : ToolApi
  const query = {
    tool_type_list: props.toolTypes,
    ...(isSystemResource() ? { workspace_id: props.workspaceId } : {}),
    ...(isWorkspaceScope.value ? { folder_id: currentFolder.value.id } : {}),
    ...(appliedSearchKeyword.value ? { name: appliedSearchKeyword.value } : {}),
  }
  return requestApi
    .getAllTool(query)
    .then((tool) => {
      toolOptions.value = tool.filter(
        (resource) => resource.is_active && props.toolTypes.includes(resource.tool_type) && !props.excludedIds.includes(resource.id),
      )
      // 仅补全已选快照，不因查询结果缺少某个 ID 而删除关联。
      const toolById = new Map(tool.map((tool) => [tool.id, tool]))
      selectedTool.value = selectedTool.value.map((tool) => toolById.get(tool.id) ?? tool)
      return nextTick(() => {
        toolLayoutRef.value?.setScrollTop(0)
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function refreshResources() {
  folderTreeRef.value?.refresh()
  void refreshTool()
}

function selectFolder(folder?: FolderItem) {
  if (!folder || folder.id === currentFolder.value.id) return
  selectedFolder.value = folder
  void refreshTool()
}

function open(tool: (Partial<ToolItem> & { id: string })[]) {
  selectedTool.value = cloneDeep(tool)
  visible.value = true
  void refreshTool()
}

watch(
  () => props.workspaceId,
  () => {
    if (visible.value && isSystemResource()) void refreshTool()
  },
)

function submit() {
  emit('submit', cloneDeep(selectedTool.value))
  visible.value = false
}
function resetData() {
  loading.value = false
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
  selectedFolder.value = undefined
  toolOptions.value = []
  selectedTool.value = []
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" :title="title ?? t('tool.title')" width="1200" @closed="resetData">
    <template #header="{ titleId }">
      <div class="flex-between pr-8">
        <div class="flex-align-center gap-2">
          <h4 :id="titleId">{{ title ?? t('tool.title') }}</h4>
        </div>

        <!-- 刷新工具 -->
        <el-button text class="h-7! w-7! min-w-0! p-1!" @click="refreshResources">
          <MkIcon name="icon_refresh_outlined" :size="20" />
        </el-button>
      </div>
    </template>

    <MkViewLayout ref="toolLayoutRef" :loading="loading" title="">
      <template v-if="isWorkspaceScope" #aside>
        <FolderTree
          ref="folderTreeRef"
          class="pt-4"
          :can-edit="false"
          :show-shared="false"
          :source="RESOURCE_TYPE.TOOL"
          @loaded="selectFolder"
          @select="selectFolder"
        />
      </template>
      <template #default="{ Header }">
        <component :is="Header">
          <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
          <MkSearchInput v-model="searchKeyword" class="w-60! shrink-0" @change="refreshTool" />
        </component>

        <template v-if="!loading">
          <div v-if="toolOptions.length" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <template v-for="tool in toolOptions" :key="tool.id">
              <el-popover
                placement="bottom-start"
                :width="360"
                :show-after="TOOLTIP_SHOW_DELAY"
                :persistent="false"
                popper-class="border-none! rounded-xl!"
              >
                <template #reference>
                  <MkCardCheckbox :model-value="selectedToolIds.includes(tool.id)" :label="tool.name" @update:model-value="toggleTool(tool)">
                    <div class="flex-align-center min-w-0 flex-1 gap-2">
                      <ToolIcon :icon="tool.icon" :type="tool.tool_type" class="shrink-0" />
                      <span class="min-w-0 flex-1 truncate" :title="tool.name">{{ tool.name }}</span>
                    </div>
                  </MkCardCheckbox>
                </template>
                <template #default>
                  <MkResourceCard :title="tool.name" :nick_name="tool.nick_name || '-'" :create_time="tool.create_time">
                    <template #icon><ToolIcon :icon="tool.icon" :type="tool.tool_type" /></template>
                    <p class="line-clamp-2" :title="tool.desc || '-'">{{ tool.desc || '-' }}</p>
                  </MkResourceCard>
                </template>
              </el-popover>
            </template>
          </div>
          <MkEmpty v-else class="mt-24" :type="appliedSearchKeyword ? 'search' : 'default'" />
        </template>
      </template>
    </MkViewLayout>
    <template #footer>
      <div class="flex-between">
        <div class="flex-align-center gap-2">
          <span class="text-N600">{{ t('common.labels.selected') }} {{ selectedTool.length }}</span>
          <!-- 清空已选工具 -->
          <el-button v-if="selectedTool.length" link type="primary" @click="selectedTool = []">{{ t('common.actions.clear') }}</el-button>
        </div>
        <div>
          <!-- 取消工具选择 -->
          <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
          <!-- 确认工具选择 -->
          <el-button type="primary" @click="submit">{{ t('common.actions.confirm') }}</el-button>
        </div>
      </div>
    </template>
  </MkDialog>
</template>
