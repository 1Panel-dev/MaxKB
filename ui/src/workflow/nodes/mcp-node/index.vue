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
          <el-select v-model="form_data.mcp_tool" @change="changeTool">
            <el-option
              v-for="item in form_data.mcp_tools"
              :key="item.value"
              :label="item.name"
              :value="item.name"
            >
              <el-tooltip
                class="box-item"
                effect="dark"
                :content="item.description"
                placement="top-start"
              >
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>

              <span>{{ item.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    <h5 class="title-decoration-1 mb-8">
      {{ $t('views.applicationWorkflow.nodes.mcpNode.toolParam') }}
    </h5>
    <div
      class="border-r-4 p-8-12 mb-8 layout-bg lighter"
      v-if="form_data.tool_params[form_data.params_nested]"
    >
      <DynamicsForm
        v-if="form_data.mcp_tool"
        v-model="form_data.tool_params[form_data.params_nested]"
        :model="form_data.tool_params[form_data.params_nested]"
        label-position="top"
        require-asterisk-position="right"
        :render_data="form_data.tool_form_field"
        ref="dynamicsFormRef"
      >
      </DynamicsForm>
    </div>
    <div class="border-r-4 p-8-12 mb-8 layout-bg lighter" v-else>
      <DynamicsForm
        v-if="form_data.mcp_tool"
        v-model="form_data.tool_params"
        :model="form_data.tool_params"
        label-position="top"
        require-asterisk-position="right"
        :render_data="form_data.tool_form_field"
        ref="dynamicsFormRef"
      >
      </DynamicsForm>
    </div>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import applicationApi from '@/api/application'
import { t } from '@/locales'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { MsgError, MsgSuccess } from '@/utils/message'

const props = defineProps<{ nodeModel: any }>()

const dynamicsFormRef = ref()
const loading = ref(false)

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
        form_data.value.tool_form_field.push({
          field: item2,
          label: {
            input_type: 'TooltipLabel',
            label: item2,
            attrs: { tooltip: params[item2].description },
            props_info: {}
          },
          input_type: 'TextInput',
          required: args_schema.properties[item].required?.indexOf(item2) !== -1,
          default_value: '',
          show_default_value: false,
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
      form_data.value.tool_form_field.push({
        field: item,
        label: {
          input_type: 'TooltipLabel',
          label: item,
          attrs: { tooltip: args_schema.properties[item].description },
          props_info: {}
        },
        input_type: 'TextInput',
        required: args_schema.required?.indexOf(item) !== -1,
        default_value: '',
        show_default_value: false,
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
    dynamicsFormRef.value?.render(
      form_data.value.tool_form_field,
      form_data.value.tool_params[form_data.value.params_nested]
    )
  } else {
    form_data.value.tool_params = {}
    dynamicsFormRef.value?.render(form_data.value.tool_form_field, form_data.value.tool_params)
  }
  console.log(form_data.value.tool_params)
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
  let ps = [replyNodeFormRef.value?.validate(), dynamicsFormRef.value?.validate()]
  return Promise.all(ps).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
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
