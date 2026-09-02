<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import ApplicationApi from '@/api/admin/workspace/application/application'
import SharedApi from '@/api/admin/workspace/shared'
import ToolApi from '@/api/admin/workspace/tool/tool'
import { APPLICATION_TYPE, RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import type { ApplicationDetail, ApplicationType, FolderItem, ToolItem, ToolType } from '@/api/types'
import FolderTree from '@/components/business/folder-tree/index.vue'
import { FOLDER_ENTRY_ID } from '@/constants'
import { applicationNode, toolLibNode, toolWorkflowLibNode } from '@/workflow-canvas/config/node-data'
import type { NodeMenuItem, NodeMenuResourceSource } from './types'

defineOptions({ name: 'ResourceNodeMenu' })

const props = defineProps<{ source: NodeMenuResourceSource }>()
const emit = defineEmits<{
  dragstart: [node: NodeMenuItem, event: PointerEvent]
  select: [node: NodeMenuItem]
}>()

interface ResourceMenuItem {
  applicationType?: ApplicationType
  desc?: string | null
  icon?: string
  id: string
  name: string
  node: NodeMenuItem
  toolType?: ToolType
}

const SUPPORTED_TOOL_TYPES: ToolType[] = [TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW]
const route = useRoute()
const currentFolderId = ref(FOLDER_ENTRY_ID.ALL)
const loading = ref(false)
const resourceItems = ref<ResourceMenuItem[]>([])
const searchKeyword = ref('')
const isToolMenu = computed(() => props.source === RESOURCE_TYPE.TOOL)
const currentApplicationId = computed(() => {
  const applicationId = route.params.applicationId
  return Array.isArray(applicationId) ? applicationId[0] : applicationId
})

const filteredResourceItems = computed(() => {
  const keyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!keyword) return resourceItems.value
  return resourceItems.value.filter((resource) => resource.name.toLocaleLowerCase().includes(keyword))
})

function createToolNode(tool: ToolItem): NodeMenuItem {
  const node = cloneDeep(tool.tool_type === TOOL_TYPE.WORKFLOW ? toolWorkflowLibNode : toolLibNode) as NodeMenuItem
  const inputFields = (tool.input_field_list ?? []).map((field) => ({ ...field, value: field.source === 'reference' ? [] : '' }))

  node.properties = {
    ...node.properties,
    stepName: tool.name,
    node_data: { ...cloneDeep(tool), input_field_list: inputFields, tool_lib_id: tool.id },
  }
  return node
}

function createApplicationNode(application: ApplicationDetail): NodeMenuItem {
  const node = cloneDeep(applicationNode) as NodeMenuItem
  node.properties = {
    ...node.properties,
    stepName: application.name,
    node_data: { application_id: application.id, icon: application.icon, name: application.name },
  }
  return node
}

function loadTools(folder?: FolderItem) {
  const isSharedFolder = folder?.id === FOLDER_ENTRY_ID.SHARED
  const requestApi = isSharedFolder ? SharedApi : ToolApi
  const folderQuery = {
    tool_type_list: SUPPORTED_TOOL_TYPES,
    ...(!isSharedFolder ? { folder_id: folder?.id || FOLDER_ENTRY_ID.ALL } : {}),
  }

  return requestApi.getAllTool(folderQuery).then((tools) => {
    resourceItems.value = tools
      .filter((tool) => tool.is_active)
      .map((tool) => ({
        desc: tool.desc,
        icon: tool.icon,
        id: tool.id,
        name: tool.name,
        node: createToolNode(tool),
        toolType: tool.tool_type,
      }))
  })
}

function loadApplications(folder?: FolderItem) {
  const folderQuery = { folder_id: folder?.id || FOLDER_ENTRY_ID.ALL }

  return ApplicationApi.getAllApplication({ ...folderQuery, publish_status: 'published' }).then((res) => {
    resourceItems.value = res
      .filter((application) => application.id !== currentApplicationId.value)
      .map((application) => ({
        applicationType: application.type,
        desc: application.desc,
        icon: application.icon,
        id: application.id,
        name: application.name,
        node: createApplicationNode(application),
      }))
  })
}

function loadResources(folder?: FolderItem) {
  loading.value = true
  const request = isToolMenu.value ? loadTools(folder) : loadApplications(folder)
  return request.finally(() => {
    loading.value = false
  })
}

function handleNodeDragStart(event: PointerEvent, node: NodeMenuItem) {
  if (event.button === 0) emit('dragstart', node, event)
}

onMounted(() => {
  void loadResources()
})
</script>

<template>
  <div class="flex h-[450px] min-h-0">
    <aside class="flex w-60 shrink-0 border-r pt-3">
      <FolderTree v-model="currentFolderId" :can-edit="false" :show-shared="isToolMenu" :source="source" @select="loadResources" />
    </aside>

    <section v-loading="loading" class="flex min-w-0 flex-1 flex-col">
      <div class="shrink-0 p-3">
        <MkSearchInput v-model="searchKeyword" placeholder="按名称搜索" />
      </div>

      <el-scrollbar class="min-h-0 flex-1">
        <div v-if="filteredResourceItems.length" class="grid grid-cols-2 gap-3 px-3 pb-3">
          <el-popover
            v-for="resource in filteredResourceItems"
            :key="resource.id"
            placement="right"
            :width="280"
            :show-after="500"
            :persistent="false"
          >
            <template #reference>
              <button
                type="button"
                class="flex h-10 min-w-0 cursor-grab items-center gap-2 rounded-md border border-N300 px-3 text-left text-N900 hover:border-primary hover:text-primary active:cursor-grabbing"
                @click="emit('select', resource.node)"
                @pointerdown="handleNodeDragStart($event, resource.node)"
              >
                <ToolIcon v-if="isToolMenu" :icon="resource.icon" :size="20" :type="resource.toolType" />
                <ApplicationIcon v-else :icon="resource.icon" :size="20" />
                <span class="min-w-0 flex-1 truncate" :title="resource.name">{{ resource.name }}</span>
              </button>
            </template>

            <div class="flex min-w-0 items-center gap-2">
              <ToolIcon v-if="isToolMenu" :icon="resource.icon" :size="24" :type="resource.toolType" />
              <ApplicationIcon v-else :icon="resource.icon" :size="24" />
              <h6 class="min-w-0 flex-1 break-all">{{ resource.name }}</h6>
              <el-tag
                v-if="resource.applicationType"
                size="small"
                :type="resource.applicationType === APPLICATION_TYPE.WORK_FLOW ? 'warning' : 'primary'"
              >
                {{ resource.applicationType === APPLICATION_TYPE.WORK_FLOW ? '高级智能体' : '简易智能体' }}
              </el-tag>
            </div>
            <p v-if="resource.desc" class="mt-2 text-sm text-N600">{{ resource.desc }}</p>
          </el-popover>
        </div>
        <MkEmpty v-else :type="searchKeyword ? 'search' : 'default'" :image-size="72" />
      </el-scrollbar>
    </section>
  </div>
</template>
