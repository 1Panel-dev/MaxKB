<template>
  <div
    v-show="show"
    class="workflow-dropdown-menu border border-r-6 white-bg"
    :style="{ width: activeName === 'base' ? '400px' : '640px' }"
  >
    <el-tabs v-model="activeName" class="workflow-dropdown-tabs" @tab-change="handleClick">
      <div
        v-show="activeName === 'base'"
        style="display: flex; width: 100%; justify-content: center"
        class="mb-12 mt-12"
      >
        <el-input
          v-model="search_text"
          class="mr-12 ml-12"
          :placeholder="$t('views.applicationWorkflow.searchBar.placeholder')"
        >
          <template #suffix>
            <el-icon class="el-input__icon">
              <search />
            </el-icon>
          </template>
        </el-input>
      </div>

      <el-tab-pane :label="$t('views.applicationWorkflow.baseComponent')" name="base">
        <el-scrollbar height="400">
          <div v-if="filter_menu_nodes.length > 0">
            <template v-for="(node, index) in filter_menu_nodes" :key="index">
              <el-text type="info" size="small" class="color-secondary ml-12">{{
                node.label
              }}</el-text>
              <div class="flex-wrap" style="gap: 12px; padding: 12px">
                <template v-for="(item, index) in node.list" :key="index">
                  <el-popover placement="right" :width="280" :show-after="500">
                    <template #reference>
                      <div
                        class="list-item flex align-center border border-r-6 p-8-12 cursor"
                        style="width: calc(50% - 6px)"
                        @click.stop="clickNodes(item)"
                        @mousedown.stop="onmousedown(item)"
                      >
                        <component
                          :is="iconComponent(`${item.type}-icon`)"
                          class="mr-8"
                          :size="20"
                        />
                        <div class="lighter">{{ item.label }}</div>
                      </div>
                    </template>
                    <template #default>
                      <div class="flex align-center mb-8">
                        <component
                          :is="iconComponent(`${item.type}-icon`)"
                          class="mr-8"
                          :size="32"
                        />
                        <div class="lighter color-text-primary">{{ item.label }}</div>
                      </div>
                      <el-text type="info" size="small" class="color-secondary lighter">{{
                        item.text
                      }}</el-text>
                    </template>
                  </el-popover>
                </template>
              </div>
            </template>
          </div>
          <div v-else class="ml-16 mt-8">
            <el-text type="info">{{ $t('views.applicationWorkflow.tip.noData') }}</el-text>
          </div>
        </el-scrollbar>
      </el-tab-pane>
      <!-- 工具 -->
      <el-tab-pane :label="$t('views.tool.title')" name="tool">
        <LayoutContainer>
          <template #left>
            <folder-tree
              :source="SourceTypeEnum.TOOL"
              :data="toolTreeData"
              :currentNodeKey="folder.currentFolder?.id"
              @handleNodeClick="folderClickHandle"
              :shareTitle="$t('views.shared.shared_tool')"
              :showShared="permissionPrecise['is_share']()"
              :canOperation="false"
              :treeStyle="{ height: '400px' }"
            />
          </template>
          <el-scrollbar height="450">
            <NodeContent
              :list="toolList"
              @clickNodes="(val: any) => clickNodes(toolLibNode, val, 'tool')"
              @onmousedown="(val: any) => onmousedown(toolLibNode, val, 'tool')"
            />
          </el-scrollbar>
        </LayoutContainer>
      </el-tab-pane>
      <!-- 应用 -->
      <el-tab-pane :label="$t('views.application.title')" name="application">
        <LayoutContainer>
          <template #left>
            <folder-tree
              :source="SourceTypeEnum.APPLICATION"
              :data="applicationTreeData"
              :currentNodeKey="folder.currentFolder?.id"
              @handleNodeClick="folderClickHandle"
              :canOperation="false"
              :treeStyle="{ height: '400px' }"
            />
          </template>
          <el-scrollbar height="450">
            <NodeContent
              :list="applicationList"
              @clickNodes="(val: any) => clickNodes(applicationNode, val, 'application')"
              @onmousedown="(val: any) => onmousedown(applicationNode, val, 'application')"
            />
          </el-scrollbar>
        </LayoutContainer>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed, inject } from 'vue'
import { getMenuNodes, toolLibNode, applicationNode } from '@/workflow/common/data'
import { iconComponent } from '@/workflow/icons/utils'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { isWorkFlow } from '@/utils/application'
import useStore from '@/stores'
import NodeContent from './NodeContent.vue'
import { SourceTypeEnum } from '@/enums/common'
import permissionMap from '@/permission'
import { useRoute } from 'vue-router'
import { WorkflowMode } from '@/enums/application'
const workflowModel = inject('workflowMode') as WorkflowMode
const route = useRoute()
const { user, folder } = useStore()

const menuNodes = getMenuNodes(workflowModel || WorkflowMode.Application)
const search_text = ref<string>('')
const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  id: {
    type: String,
    default: '',
  },
  workflowRef: Object,
})

const emit = defineEmits(['clickNodes', 'onmousedown'])

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['tool'][apiType.value]
})

const loading = ref(false)
const activeName = ref('base')

const filter_menu_nodes = computed(() => {
  if (!search_text.value) return menuNodes || []
  const searchTerm = search_text.value.toLowerCase()

  return (menuNodes || []).reduce((result: any[], item) => {
    const filteredList = item.list.filter((listItem) =>
      listItem.label.toLowerCase().includes(searchTerm),
    )

    if (filteredList.length) {
      result.push({ ...item, list: filteredList })
    }

    return result
  }, [])
})
function clickNodes(item: any, data?: any, type?: string) {
  if (data) {
    item['properties']['stepName'] = data.name
    if (type == 'tool') {
      item['properties']['node_data'] = {
        ...data,
        tool_lib_id: data.id,
        input_field_list: data.input_field_list.map((field: any) => ({
          ...field,
          value: field.source == 'reference' ? [] : '',
        })),
      }
    }
    if (type == 'application') {
      item['properties']['node_data'] = {
        name: data.name,
        icon: data.icon,
        application_id: data.id,
      }
    }
  }
  props.workflowRef?.addNode(item)

  emit('clickNodes', item)
}

function onmousedown(item: any, data?: any, type?: string) {
  if (data) {
    item['properties']['stepName'] = data.name
    if (type == 'tool') {
      item['properties']['node_data'] = {
        ...data,
        tool_lib_id: data.id,
        input_field_list: data.input_field_list.map((field: any) => ({
          ...field,
          value: field.source == 'reference' ? [] : '',
        })),
      }
    }
    if (type == 'application') {
      if (isWorkFlow(data.type)) {
        const nodeData = data.work_flow.nodes[0].properties.node_data
        const fileUploadSetting = nodeData.file_upload_setting
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
        }
      } else {
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
        }
      }
    }
  }
  props.workflowRef?.onmousedown(item)
  emit('onmousedown', item)
}

const toolTreeData = ref<any[]>([])
const toolList = ref<any[]>([])

async function getToolFolder() {
  const res: any = await folder.asyncGetFolder(SourceTypeEnum.TOOL, {}, loading)
  toolTreeData.value = res.data
  folder.setCurrentFolder(res.data?.[0] || {})
}

async function getToolList() {
  const res = await loadSharedApi({
    type: 'tool',
    isShared: folder.currentFolder?.id === 'share',
    systemType: 'workspace',
  }).getToolList({
    folder_id: folder.currentFolder?.id || user.getWorkspaceId(),
    tool_type: 'CUSTOM',
  })
  toolList.value = res.data?.tools || res.data || []
  toolList.value = toolList.value?.filter((item: any) => item.is_active)
}

const applicationTreeData = ref<any[]>([])
const applicationList = ref<any[]>([])

function getApplicationFolder() {
  folder.asyncGetFolder(SourceTypeEnum.APPLICATION, {}, loading).then((res: any) => {
    applicationTreeData.value = res.data
    folder.setCurrentFolder(res.data?.[0] || {})
  })
}

async function getApplicationList() {
  const res = await loadSharedApi({
    type: 'application',
    systemType: 'workspace',
  }).getAllApplication({
    folder_id: folder.currentFolder?.id || user.getWorkspaceId(),
  })
  applicationList.value = res.data.filter(
    (item: any) => item.resource_type === 'application' && item.id !== props.id && item.is_publish,
  )
}

function folderClickHandle(row: any) {
  folder.setCurrentFolder(row)
  if (activeName.value === 'tool') {
    getToolList()
  } else {
    getApplicationList()
  }
}

async function handleClick(val: string) {
  console.log(val)
  if (val === 'tool') {
    await getToolFolder()
    getToolList()
  } else if (val === 'application') {
    getApplicationFolder()
    getApplicationList()
  }
}

onMounted(() => {})
</script>
<style lang="scss" scoped>
.workflow-dropdown-menu {
  -moz-user-select: none; /* Firefox */
  -webkit-user-select: none; /* WebKit内核 */
  -ms-user-select: none; /* IE10及以后 */
  -khtml-user-select: none; /* 早期浏览器 */
  -o-user-select: none; /* Opera */
  user-select: none; /* CSS3属性 */
  position: absolute;
  top: 49px;
  right: 16px;
  z-index: 99;
  width: 600px;
  box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
  padding-bottom: 8px;

  .title {
    padding: 12px 12px 4px;
  }
  .workflow-dropdown-item {
    &:hover {
      background: var(--app-text-color-light-1);
    }
  }

  .list-item {
    box-sizing: border-box;
    &:hover {
      border-color: var(--el-color-primary);
    }
  }

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
}
</style>
