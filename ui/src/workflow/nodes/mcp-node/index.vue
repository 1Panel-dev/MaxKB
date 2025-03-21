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
            v-model="form_data.mcpServers"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item>
          <template v-slot:label>
            <div class="flex-between">
              <span>工具</span>
              <el-button type="primary" link @click="getTools()">获取工具</el-button>
            </div>
          </template>
          <el-select
            v-model="form_data.mcpTool"
            placeholder="请选择工具"
            @change="changeTool"
          >
            <el-option
              v-for="item in form_data.mcpTools"
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
    <h5 class="title-decoration-1 mb-8">工具参数</h5>
    <div class="border-r-4 p-8-12 mb-8 layout-bg lighter">
      <DynamicsForm
        v-if="form_data.mcpTool"
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
import { MsgSuccess } from '@/utils/message'

const props = defineProps<{ nodeModel: any }>()

const dynamicsFormRef = ref()


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
  mcpTool: '',
  mcpServers: '',
  tool_params: {},
  tool_form_field: []
}


function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'mcpServers', val)
}

function getTools() {
  applicationApi.getMcpTools({ mcp_servers: form_data.value.mcpServers }).then((res: any) => {
    form_data.value.mcpTools = res.data
    MsgSuccess(t('views.applicationWorkflow.nodes.mcpNode.getToolsSuccess'))
  })
}

function changeTool() {
  const params = form_data.value.mcpTools.filter((item: any) => item.name === form_data.value.mcpTool)[0].args.params
  form_data.value.tool_form_field = []
  for (const item in params.properties) {
    form_data.value.tool_form_field.push({
      field: item,
      label: {
        input_type: 'TooltipLabel',
        label: item,
        attrs: { tooltip: params.properties[item].description },
        props_info: {}
      },
      input_type: 'TextInput',
      required: params.required.indexOf(item) !== -1,
      default_value: '',
      show_default_value: false,
      props_info: {
        rules: [
          {
            required: params.required.indexOf(item) !== -1,
            message: t('dynamicsForm.tip.requiredMessage'),
            trigger: 'blur'
          }
        ]
      }
    })
  }
  //
  dynamicsFormRef.value?.render(form_data.value.tool_form_field, form_data.value.tool_params)
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
const nodeCascaderRef = ref()
const nodeCascaderRef2 = ref()

const validate = async () => {
  // console.log(replyNodeFormRef.value.validate())
  let ps = [
    replyNodeFormRef.value?.validate(),
    ...nodeCascaderRef.value.map((item: any) => item.validate())
  ]
  if (nodeCascaderRef2.value) {
    ps = [...ps, ...nodeCascaderRef.value.map((item: any) => item.validate())]
  }
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
