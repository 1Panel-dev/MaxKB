<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <div class="border-r-6 p-8-12 mb-8 layout-bg lighter">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="replyNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item label="MCP Server Config">
          <template #label>
            <div class="flex-between">
              <div>
                MCP Server Config
                <span class="color-danger">*</span>
              </div>
              <el-select
                :teleported="false"
                v-model="form_data.mcp_source"
                size="small"
                style="width: 85px"
              >
                <el-option
                  :label="$t('views.applicationWorkflow.nodes.mcpNode.reference')"
                  value="referencing"
                />
                <el-option :label="$t('common.custom')" value="custom" />
              </el-select>
            </div>
          </template>
          <MdEditorMagnify
            v-if="form_data.mcp_source === 'custom'"
            @wheel="wheel"
            title="MCP Server Config"
            v-model="form_data.mcp_servers"
            style="height: 150px"
            @submitDialog="submitDialog"
            :placeholder="mcpServerJson"
          />
          <el-select
            v-else
            v-model="form_data.mcp_tool_id"
            filterable
            @change="mcpToolSelectChange"
          >
            <el-option
              v-for="mcpTool in mcpToolSelectOptions"
              :key="mcpTool.id"
              :label="mcpTool.name"
              :value="mcpTool.id"
            >
              <div class="flex align-center">
                <el-avatar
                  v-if="mcpTool?.icon"
                  shape="square"
                  :size="20"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="resetUrl(mcpTool?.icon)" alt="" />
                </el-avatar>
                <ToolIcon v-else :size="20" :type="mcpTool?.tool_type" class="mr-8" />
                <span>{{ mcpTool.name }}</span>
                <el-tag v-if="mcpTool.scope === 'SHARED'" type="info" class="info-tag ml-8">
                  {{ t('views.shared.title') }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <template v-slot:label>
            <div class="flex-between">
              <span>{{ $t('views.tool.title') }}</span>
              <el-button type="primary" link @click="getTools()">
                <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                {{ $t('views.applicationWorkflow.nodes.mcpNode.getTool') }}
              </el-button>
            </div>
          </template>
          <el-select v-model="form_data.mcp_tool" @change="changeTool" filterable>
            <el-option
              v-for="item in form_data.mcp_tools"
              :key="item.value"
              :label="item.name"
              :value="item.name"
              class="flex align-center"
            >
              <el-tooltip
                effect="dark"
                :content="item.description"
                placement="top-start"
                popper-class="max-w-350"
              >
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>

              <span class="ml-4">{{ item.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    <h5 class="title-decoration-1 mb-8">
      {{ $t('views.applicationWorkflow.nodes.mcpNode.toolParam') }}
    </h5>
    <template v-if="form_data.tool_params[form_data.params_nested]">
      <div class="p-8-12" v-if="!form_data.mcp_tool">
        <el-text type="info">{{ $t('common.noData') }}</el-text>
      </div>
      <div v-else class="border-r-6 p-8-12 mb-8 layout-bg lighter">
        <el-form
          ref="dynamicsFormRef"
          label-position="top"
          v-loading="loading"
          require-asterisk-position="right"
          :hide-required-asterisk="true"
          v-if="form_data.mcp_tool"
          @submit.prevent
        >
          <el-form-item
            v-for="item in form_data.tool_form_field"
            :key="item.field"
            :required="item.required"
          >
            <template #label>
              <div class="flex-between">
                <div>
                  <TooltipLabel v-if="item.label.attrs.tooltip" :label="item.label" :tooltip="item.label.attrs.tooltip" />
                  <span v-else>{{ item.label.label }}</span>
                  <span v-if="item.required" class="color-danger">*</span>
                </div>
                <el-select
                  :teleported="false"
                  v-model="item.source"
                  size="small"
                  style="width: 85px"
                  @change="form_data.tool_params[form_data.params_nested][item.label.label] = ''"
                >
                  <el-option
                    :label="$t('views.applicationWorkflow.variable.Referencing')"
                    value="referencing"
                  />
                  <el-option :label="$t('common.custom')" value="custom" />
                </el-select>
              </div>
            </template>
            <el-input
              v-if="item.source === 'custom' && item.input_type === 'TextInput'"
              v-model="form_data.tool_params[form_data.params_nested][item.label.label]"
            />
            <el-input-number
              v-else-if="item.source === 'custom' && item.input_type === 'NumberInput'"
              v-model="form_data.tool_params[form_data.params_nested][item.label.label]"
            />
            <el-switch
              v-else-if="item.source === 'custom' && item.input_type === 'SwitchInput'"
              v-model="form_data.tool_params[form_data.params_nested][item.label.label]"
            />
            <el-input
              v-else-if="item.source === 'custom' && item.input_type === 'JsonInput'"
              v-model="form_data.tool_params[form_data.params_nested][item.label.label]"
              type="textarea"
            />
            <NodeCascader
              v-if="item.source === 'referencing'"
              ref="nodeCascaderRef2"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
              v-model="form_data.tool_params[form_data.params_nested][item.label.label]"
            />
          </el-form-item>
        </el-form>
      </div>
    </template>
    <template v-else>
      <div class="p-8-12" v-if="!form_data.mcp_tool">
        <el-text type="info">{{ $t('common.noData') }}</el-text>
      </div>
      <div v-else class="border-r-6 p-8-12 mb-8 layout-bg lighter">
        <el-form
          ref="dynamicsFormRef"
          label-position="top"
          v-loading="loading"
          require-asterisk-position="right"
          :hide-required-asterisk="true"
          v-if="form_data.mcp_tool"
          @submit.prevent
        >
          <el-form-item
            v-for="item in form_data.tool_form_field"
            :key="item.field"
            :required="item.required"
          >
            <template #label>
              <div class="flex-between">
                <div>
                  <TooltipLabel v-if="item.label.attrs.tooltip" :label="item.label" :tooltip="item.label.attrs.tooltip" />
                  <span v-else>{{ item.label.label }}</span>
                  <span v-if="item.required" class="color-danger">*</span>
                </div>
                <el-select
                  :teleported="false"
                  v-model="item.source"
                  size="small"
                  style="width: 85px"
                  @change="form_data.tool_params[item.label.label] = ''"
                >
                  <el-option
                    :label="$t('views.applicationWorkflow.variable.Referencing')"
                    value="referencing"
                  />
                  <el-option :label="$t('common.custom')" value="custom" />
                </el-select>
              </div>
            </template>
            <el-input
              v-if="item.source === 'custom' && item.input_type === 'TextInput'"
              v-model="form_data.tool_params[item.label.label]"
            />
            <el-input-number
              v-else-if="item.source === 'custom' && item.input_type === 'NumberInput'"
              v-model="form_data.tool_params[item.label.label]"
            />
            <el-switch
              v-else-if="item.source === 'custom' && item.input_type === 'SwitchInput'"
              v-model="form_data.tool_params[item.label.label]"
            />
            <el-input
              v-else-if="item.source === 'custom' && item.input_type === 'JsonInput'"
              v-model="form_data.tool_params[item.label.label]"
              type="textarea"
            />
            <NodeCascader
              v-if="item.source === 'referencing'"
              ref="nodeCascaderRef2"
              :nodeModel="nodeModel"
              class="w-full"
              :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
              v-model="form_data.tool_params[item.label.label]"
            />
          </el-form-item>
        </el-form>
      </div>
    </template>
    <McpServerInputDialog ref="mcpServerInputDialogRef" @refresh="handleMcpVariables" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, inject, onMounted, ref } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import { t } from '@/locales'
import { MsgError, MsgSuccess } from '@/utils/message'
import TooltipLabel from '@/components/dynamics-form/items/label/TooltipLabel.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import McpServerInputDialog from './component/McpServerInputDialog.vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { resetUrl } from '@/utils/common'

const props = defineProps<{ nodeModel: any }>()

const route = useRoute()
const {
  params: { id },
} = route as any
const getApplicationDetail = inject('getApplicationDetail') as any
const applicationDetail = getApplicationDetail()

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const dynamicsFormRef = ref()
const loading = ref(false)

const mcpServerJson = `{
  "math": {
    "url": "your_server",
    "transport": "sse"
  }
}`

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const form = {
  mcp_tool: '',
  mcp_tools: [],
  mcp_servers: '',
  mcp_server: '',
  mcp_source: 'referencing',
  mcp_tool_id: '',
  tool_params: {},
  tool_form_field: [],
  params_nested: '',
}

const mcpToolSelectOptions = ref<any[]>([])

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'mcp_servers', val)
}

async function mcpToolSelectChange() {
  const tool = await loadSharedApi({ type: 'tool', systemType: apiType.value }).getToolById(
    form_data.value.mcp_tool_id,
    loading,
  )
  form_data.value.mcp_servers = tool.data.code
}

function getTools() {
  if (form_data.value.mcp_source === 'referencing' && !form_data.value.mcp_tool_id) {
    MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpToolTip'))
    return
  }
  if (form_data.value.mcp_source === 'referencing' && form_data.value.mcp_tool_id) {
    if (!mcpToolSelectOptions.value.find((item) => item.id === form_data.value.mcp_tool_id)) {
      MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpToolTip'))
      return
    }
  }
  if (form_data.value.mcp_source === 'custom' && !form_data.value.mcp_servers) {
    MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip'))
    return
  }
  try {
    JSON.parse(form_data.value.mcp_servers)
    const vars = extractPlaceholders(form_data.value.mcp_servers)
    if (vars.length > 0) {
      mcpServerInputDialogRef.value.open(vars)
      return
    }
  } catch (e) {
    MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip'))
    return
  }
  // 一切正常，获取tool
  _getTools(form_data.value.mcp_servers)
}

function _getTools(mcp_servers: any) {
  loadSharedApi({ type: 'application', systemType: apiType.value })
    .getMcpTools(id, mcp_servers, loading)
    .then((res: any) => {
      form_data.value.mcp_tools = res.data
      MsgSuccess(t('views.applicationWorkflow.nodes.mcpNode.getToolsSuccess'))
      // 修改了json，刷新mcp_server
      form_data.value.mcp_server = form_data.value.mcp_tools.find(
        (item: any) => item.name === form_data.value.mcp_tool,
      )?.server
    })
}

const mcpServerInputDialogRef = ref()
// 提取 JSON 中所有占位符（{{...}}）的变量路径
function extractPlaceholders(input: unknown): string[] {
  const re = /\{\{\s*([a-zA-Z_][\w.]*)\s*\}\}/g // 捕获 {{ path.like.this }}
  const found = new Set<string>()

  const visit = (v: unknown) => {
    if (typeof v === 'string') {
      let m: RegExpExecArray | null
      while ((m = re.exec(v)) !== null) found.add(m[1])
    } else if (Array.isArray(v)) {
      v.forEach(visit)
    } else if (v && typeof v === 'object') {
      Object.values(v as Record<string, unknown>).forEach(visit)
    }
  }

  // 如果传入的是 JSON 字符串，尝试解析，否则按字符串/对象处理
  if (typeof input === 'string') {
    try {
      visit(JSON.parse(input))
    } catch {
      visit(input)
    }
  } else {
    visit(input)
  }

  return [...found]
}

function handleMcpVariables(vars: any) {
  let mcp_servers = form_data.value.mcp_servers
  for (const item in vars) {
    mcp_servers = mcp_servers.replace(`{{${item}}}`, vars[item])
  }

  // 一切正常，获取tool
  _getTools(mcp_servers)
}

function changeTool() {
  form_data.value.mcp_server = form_data.value.mcp_tools.find(
    (item: any) => item.name === form_data.value.mcp_tool,
  )?.server

  const args_schema = form_data.value.mcp_tools.find(
    (item: any) => item.name === form_data.value.mcp_tool,
  )?.args_schema
  form_data.value.tool_form_field = []
  for (const item in args_schema?.properties) {
    const params = args_schema?.properties[item].properties
    if (params) {
      form_data.value.params_nested = item
      for (const item2 in params) {
        let input_type = 'TextInput'
        if (params[item2].type === 'string') {
          input_type = 'TextInput'
        } else if (params[item2].type === 'number') {
          input_type = 'NumberInput'
        } else if (params[item2].type === 'boolean') {
          input_type = 'SwitchInput'
        } else if (params[item2].type === 'array') {
          input_type = 'JsonInput'
        } else if (params[item2].type === 'object') {
          input_type = 'JsonInput'
        }
        form_data.value.tool_form_field.push({
          field: item2,
          label: {
            input_type: 'TooltipLabel',
            label: item2,
            attrs: { tooltip: params[item2].description },
            props_info: {},
          },
          input_type: input_type,
          source: 'referencing',
          required: args_schema.properties[item].required?.indexOf(item2) !== -1,
          props_info: {
            rules: [
              {
                required: args_schema.properties[item].required?.indexOf(item2) !== -1,
                message: t('dynamicsForm.tip.requiredMessage'),
                trigger: 'blur',
              },
            ],
          },
        })
      }
    } else {
      form_data.value.params_nested = ''
      let input_type = 'TextInput'
      if (args_schema.properties[item].type === 'string') {
        input_type = 'TextInput'
      } else if (args_schema.properties[item].type === 'number') {
        input_type = 'NumberInput'
      } else if (args_schema.properties[item].type === 'boolean') {
        input_type = 'SwitchInput'
      } else if (args_schema.properties[item].type === 'array') {
        input_type = 'JsonInput'
      } else if (args_schema.properties[item].type === 'object') {
        input_type = 'JsonInput'
      }
      form_data.value.tool_form_field.push({
        field: item,
        label: {
          input_type: 'TooltipLabel',
          label: item,
          attrs: { tooltip: args_schema.properties[item].description },
          props_info: {},
        },
        input_type: input_type,
        source: 'referencing',
        required: args_schema.required?.indexOf(item) !== -1,
        props_info: {
          rules: [
            {
              required: args_schema.required?.indexOf(item) !== -1,
              message: t('dynamicsForm.tip.requiredMessage'),
              trigger: 'blur',
            },
          ],
        },
      })
    }
  }
  //
  if (form_data.value.params_nested) {
    form_data.value.tool_params = { [form_data.value.params_nested]: {} }
  } else {
    form_data.value.tool_params = {}
  }
}

const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  },
})

const replyNodeFormRef = ref()

const validate = async () => {
  // 对动态表单，只验证必填字段
  if (dynamicsFormRef.value) {
    const requiredFields = form_data.value.tool_form_field
      .filter((item: any) => item.required)
      .map((item: any) => item.label.label)

    if (requiredFields.length > 0) {
      for (const item of requiredFields) {
        if (form_data.value.params_nested) {
          if (!form_data.value.tool_params[form_data.value.params_nested][item]) {
            return Promise.reject({
              node: props.nodeModel,
              errMessage: item + t('dynamicsForm.tip.requiredMessage'),
            })
          }
        } else {
          // 这里是没有嵌套的情况
          if (!form_data.value.tool_params[item]) {
            return Promise.reject({
              node: props.nodeModel,
              errMessage: item + t('dynamicsForm.tip.requiredMessage'),
            })
          }
        }
      }
    }
  }
  if (replyNodeFormRef.value) {
    const form = cloneDeep(form_data.value)
    if (!form.mcp_servers) {
      return Promise.reject({
        node: props.nodeModel,
        errMessage: t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip'),
      })
    }
    if (!form.mcp_tool) {
      return Promise.reject({
        node: props.nodeModel,
        errMessage: t('views.applicationWorkflow.nodes.mcpNode.mcpToolTip'),
      })
    }
  }
}

function getMcpToolSelectOptions() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          scope: 'WORKSPACE',
          tool_type: 'MCP',
          workspace_id: applicationDetail.value?.workspace_id,
        }
      : {
          scope: 'WORKSPACE',
          tool_type: 'MCP',
        }

  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getAllToolList(obj, loading)
    .then((res: any) => {
      mcpToolSelectOptions.value = [...res.data.shared_tools, ...res.data.tools].filter(
        (item: any) => item.is_active,
      )
    })
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  if (
    props.nodeModel.properties.node_data.mcp_servers &&
    !props.nodeModel.properties.node_data.mcp_source
  ) {
    set(props.nodeModel.properties.node_data, 'mcp_source', 'custom')
  }
  getMcpToolSelectOptions()
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
