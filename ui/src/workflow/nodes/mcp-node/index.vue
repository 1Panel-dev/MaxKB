<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <div class="border-r-4 p-8-12 mb-8 layout-bg lighter">
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
          <MdEditorMagnify
            @wheel="wheel"
            title="MCP Server Config"
            v-model="form_data.mcp_servers"
            style="height: 150px"
            @submitDialog="submitDialog"
            :placeholder="mcpServerJson"
          />
        </el-form-item>
        <el-form-item>
          <template v-slot:label>
            <div class="flex-between">
              <span>{{ $t('views.applicationWorkflow.nodes.mcpNode.tool') }}</span>
              <el-button type="primary" link @click="getTools()">
                <el-icon class="mr-4">
                  <Plus />
                </el-icon>
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
      <div v-else class="border-r-4 p-8-12 mb-8 layout-bg lighter">
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
                  <TooltipLabel :label="item.label.label" :tooltip="item.label.attrs.tooltip" />
                  <span v-if="item.required" class="danger">*</span>
                </div>
                <el-select
                  :teleported="false"
                  v-model="item.source"
                  size="small"
                  style="width: 85px"
                  @change="form_data.tool_params[form_data.params_nested] = {}"
                >
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.reference')"
                    value="referencing"
                  />
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.custom')"
                    value="custom"
                  />
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
      <div class="p-8-12"  v-if="!form_data.mcp_tool">
        <el-text type="info">{{ $t('common.noData') }}</el-text>
      </div>
      <div v-else class="border-r-4 p-8-12 mb-8 layout-bg lighter">
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
                  <TooltipLabel :label="item.label.label" :tooltip="item.label.attrs.tooltip" />
                  <span v-if="item.required" class="danger">*</span>
                </div>
                <el-select
                  :teleported="false"
                  v-model="item.source"
                  size="small"
                  style="width: 85px"
                >
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.reference')"
                    value="referencing"
                  />
                  <el-option
                    :label="$t('views.applicationWorkflow.nodes.replyNode.replyContent.custom')"
                    value="custom"
                  />
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
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import applicationApi from '@/api/application'
import { t } from '@/locales'
import { MsgError, MsgSuccess } from '@/utils/message'
import TooltipLabel from '@/components/dynamics-form/items/label/TooltipLabel.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'

const props = defineProps<{ nodeModel: any }>()

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
  tool_params: {},
  tool_form_field: [],
  params_nested: ''
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'mcp_servers', val)
}

function getTools() {
  if (!form_data.value.mcp_servers) {
    MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip'))
    return
  }
  try {
    JSON.parse(form_data.value.mcp_servers)
  } catch (e) {
    MsgError(t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip'))
    return
  }
  applicationApi
    .getMcpTools({ mcp_servers: form_data.value.mcp_servers }, loading)
    .then((res: any) => {
      form_data.value.mcp_tools = res.data
      MsgSuccess(t('views.applicationWorkflow.nodes.mcpNode.getToolsSuccess'))
    })
}

function changeTool() {
  form_data.value.mcp_server = form_data.value.mcp_tools.filter(
    (item: any) => item.name === form_data.value.mcp_tool
  )[0].server
  // console.log(form_data.value.mcp_server)

  const args_schema = form_data.value.mcp_tools.filter(
    (item: any) => item.name === form_data.value.mcp_tool
  )[0].args_schema
  form_data.value.tool_form_field = []
  for (const item in args_schema.properties) {
    let params = args_schema.properties[item].properties
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
        console.log(params[item2])
        form_data.value.tool_form_field.push({
          field: item2,
          label: {
            input_type: 'TooltipLabel',
            label: item2,
            attrs: { tooltip: params[item2].description },
            props_info: {}
          },
          input_type: input_type,
          source: 'referencing',
          required: args_schema.properties[item].required?.indexOf(item2) !== -1,
          props_info: {
            rules: [
              {
                required: args_schema.properties[item].required?.indexOf(item2) !== -1,
                message: t('dynamicsForm.tip.requiredMessage'),
                trigger: 'blur'
              }
            ]
          }
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
      console.log(args_schema.properties[item])
      form_data.value.tool_form_field.push({
        field: item,
        label: {
          input_type: 'TooltipLabel',
          label: item,
          attrs: { tooltip: args_schema.properties[item].description },
          props_info: {}
        },
        input_type: input_type,
        source: 'referencing',
        required: args_schema.required?.indexOf(item) !== -1,
        props_info: {
          rules: [
            {
              required: args_schema.required?.indexOf(item) !== -1,
              message: t('dynamicsForm.tip.requiredMessage'),
              trigger: 'blur'
            }
          ]
        }
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
  }
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
              errMessage: item + t('dynamicsForm.tip.requiredMessage')
            })
          }
        } else {
          // 这里是没有嵌套的情况
          if (!form_data.value.tool_params[item]) {
            return Promise.reject({
              node: props.nodeModel,
              errMessage: item + t('dynamicsForm.tip.requiredMessage')
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
        errMessage: t('views.applicationWorkflow.nodes.mcpNode.mcpServerTip')
      })
    }
    if (!form.mcp_tool) {
      return Promise.reject({
        node: props.nodeModel,
        errMessage: t('views.applicationWorkflow.nodes.mcpNode.mcpToolTip')
      })
    }
  }
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }

  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
