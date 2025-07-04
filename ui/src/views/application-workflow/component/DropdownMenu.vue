<template>
  <div v-show="show" class="workflow-dropdown-menu border border-r-6">
    <el-tabs v-model="activeName" class="workflow-dropdown-tabs">
      <div style="display: flex; width: 100%; justify-content: center" class="mb-12">
        <el-input
          v-model="search_text"
          class="mr-12 ml-12"
          :placeholder="$t('views.applicationWorkflow.searchBar.placeholder')"
        >
          <template #suffix>
            <el-icon class="el-input__icon"><search /></el-icon>
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
              <div class="flex-wrap mt-8">
                <template v-for="(item, index) in node.list" :key="index">
                  <el-popover placement="right" :width="280">
                    <template #reference>
                      <div class="list-item flex align-center border border-r-6 mb-12 p-8-12 cursor ml-12"
                        style="width: 39%" @click.stop="clickNodes(item)" @mousedown.stop="onmousedown(item)">
                        <component
                          :is="iconComponent(`${item.type}-icon`)"
                          class="mr-8"
                          :size="32"
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
      <el-tab-pane :label="$t('views.tool.title')" name="tool">
        <el-scrollbar height="400">
          <!-- 共享工具 -->
          <el-collapse expand-icon-position="left" v-if="user.isEE()">
            <el-collapse-item name="shared" :icon="CaretRight">
              <template #title>
                <div class="flex align-center">
                  <AppIcon iconName="app-shared-active" style="font-size: 20px" class="color-primary"></AppIcon>
                  <span class="ml-8 lighter">{{ $t('views.shared.shared_tool') }}</span>
                </div>
              </template>
              <NodeContent :list="sharedToolList" @clickNodes="(val: any) => clickNodes(toolLibNode, val, 'tool')"
                @onmousedown="(val: any) => onmousedown(toolLibNode, val, 'tool')" />
            </el-collapse-item>
          </el-collapse>

          <el-tree :data="toolTreeData" node-key="id"
            :props="{ children: 'children', isLeaf: 'isLeaf', class: getNodeClass }" lazy :load="loadNode">
            <template #default="{ data, node }">
              <NodeContent v-if="!data._fake" :data="data" :node="node"
                @clickNodes="(val: any) => clickNodes(toolLibNode, val, 'tool')"
                @onmousedown="(val: any) => onmousedown(toolLibNode, val, 'tool')" />
            </template>
          </el-tree>
        </el-scrollbar>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.application.title')" name="application">
        <el-scrollbar height="400">
          <el-tree :data="applicationTreeData" node-key="id"
            :props="{ children: 'children', isLeaf: 'isLeaf', class: getNodeClass }" lazy :load="loadNode">
            <template #default="{ data, node }">
              <NodeContent v-if="!data._fake" :data="data" :node="node"
                @clickNodes="(val: any) => clickNodes(applicationNode, val, 'application')"
                @onmousedown="(val: any) => onmousedown(applicationNode, val, 'application')" />
            </template>
          </el-tree>
        </el-scrollbar>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { menuNodes, toolLibNode, applicationNode } from '@/workflow/common/data'
import { iconComponent } from '@/workflow/icons/utils'
import ToolApi from '@/api/tool/tool'
import { isWorkFlow } from '@/utils/application'
import useStore from '@/stores'
import NodeContent from './NodeContent.vue'
import { SourceTypeEnum } from '@/enums/common'
import sharedWorkspaceApi from '@/api/shared-workspace'
import { CaretRight } from '@element-plus/icons-vue'
import ApplicationApi from '@/api/application/application'
const {user} = useStore()
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

const { folder } = useStore()
const emit = defineEmits(['clickNodes', 'onmousedown'])

const loading = ref(false)
const activeName = ref('base')

const filter_menu_nodes = computed(() => {
  if (!search_text.value) return menuNodes
  const searchTerm = search_text.value.toLowerCase()

  return menuNodes.reduce((result: any[], item) => {
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
      if (isWorkFlow(data.type)) {
        const nodeData = data.work_flow.nodes[0].properties.node_data
        const fileUploadSetting = nodeData.file_upload_setting
        item['properties']['node_data'] = {
          name: data.name,
          icon: data.icon,
          application_id: data.id,
          api_input_field_list: data.work_flow.nodes[0].properties.api_input_field_list,
          user_input_field_list: data.work_flow.nodes[0].properties.user_input_field_list,
          ...(!fileUploadSetting
            ? {}
            : {
              ...(fileUploadSetting.document ? { document_list: [] } : {}),
              ...(fileUploadSetting.image ? { image_list: [] } : {}),
              ...(fileUploadSetting.audio ? { audio_list: [] } : {}),
            }),
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
          api_input_field_list: data.work_flow.nodes[0].properties.api_input_field_list,
          user_input_field_list: data.work_flow.nodes[0].properties.user_input_field_list,
          ...(!fileUploadSetting
            ? {}
            : {
              ...(fileUploadSetting.document ? { document_list: [] } : {}),
              ...(fileUploadSetting.image ? { image_list: [] } : {}),
              ...(fileUploadSetting.audio ? { audio_list: [] } : {}),
            }),
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

function getNodeClass(data: any) {
  return data._fake ? 'tree-node--hidden' : ''
}

const loadNode = async (node: any, resolve: (children: any[]) => void) => {
  if (node.level === 0) return resolve([])
  try {
    let folders
    if (activeName.value === 'tool') {
      const res = await ToolApi.getToolList({ folder_id: node.data.id })
      node.data.cardList = res.data.tools
      folders = res.data?.folders
    } else {
      const res = await ApplicationApi.getAllApplication({ folder_id: node.data.id })
      node.data.cardList = res.data.filter(item => item.resource_type === "application")
      folders = res.data.filter(item => item.resource_type === "folder")
    }
    const children = folders.map(f => ({
      ...f,
      children: [],
      isLeaf: false,
    }))

    if (folders.length === 0 && node.data.cardList.length > 0) {
      // 插一个假子节点，确保树节点是“可折叠”的
      children.push({
        id: `__placeholder__${node.data.id}`,
        isLeaf: true,
        _fake: true,
      })
    }

    resolve(children)
  } catch (e: any) {
    resolve([]) // 失败也要 resolve，否则树会卡住
  }
}

const toolTreeData = ref<any[]>([])
function getToolFolder() {
  folder.asyncGetFolder(SourceTypeEnum.TOOL, {}, loading).then((res: any) => {
    toolTreeData.value = res.data
  })
}

const sharedToolList = ref<any[]>([])
async function getShareTool() {
  try {
    const res = await sharedWorkspaceApi.getToolList(loading)
    sharedToolList.value = res.data
  } catch (error: any) {
    console.error(error)
  }
}

const applicationTreeData = ref<any[]>([])
function getApplicationFolder() {
  folder.asyncGetFolder(SourceTypeEnum.APPLICATION, {}, loading).then((res: any) => {
    applicationTreeData.value = res.data
  })
}

onMounted(() => {
  if (user.isEE()) {
      getShareTool()
  }
  getToolFolder()
  getApplicationFolder()
})
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
  width: 400px;
  box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
  background: #ffffff;
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
    &:hover {
      border-color: var(--el-color-primary);
    }
  }

  :deep(.el-collapse) {
    border-top-width: 0;
    .el-collapse-item__header {
      height: 40px;
      gap: 0;
      .el-collapse-item__arrow {
        font-size: 16px;
        color: var(--app-text-color-secondary);
        padding: 6px;
      }
    }
    .el-collapse-item__content {
      padding: 0 12px 16px 12px;
      .list {
        margin-top: 0;
        transform: none;
      }
    }
  }

  :deep(.el-tree-node):focus>.el-tree-node__content {
    background: transparent;
  }
  :deep(.el-tree-node__content) {
    height: auto;
    align-items: baseline;
    &:hover {
      background: transparent;
    }
  }

  :deep(.tree-node--hidden) {
    display: none !important;
  }
}
</style>
