<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="chat_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="aiChatNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          :label="$t('views.application.form.aiModel.label')"
          prop="model_id"
          :rules="{
            required: true,
            message: $t('views.application.form.aiModel.placeholder'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                  >{{ $t('views.application.form.aiModel.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>

              <el-button
                :disabled="!chat_data.model_id"
                type="primary"
                link
                @click="openAIParamSettingDialog(chat_data.model_id)"
                @refreshForm="refreshParam"
              >
                <AppIcon iconName="app-setting"></AppIcon>
              </el-button>
            </div>
          </template>
          <ModelSelect
            @change="model_change"
            @wheel="wheel"
            :teleported="false"
            v-model="chat_data.model_id"
            :placeholder="$t('views.application.form.aiModel.placeholder')"
            :options="modelOptions"
            @submitModel="getSelectModel"
            showFooter
            :model-type="'LLM'"
          ></ModelSelect>
        </el-form-item>

        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div class="flex align-center">
                <span>{{ $t('views.application.form.roleSettings.label') }}</span>
                <el-tooltip
                  effect="dark"
                  :content="$t('views.application.form.roleSettings.tooltip')"
                  placement="right"
                >
                  <AppIcon iconName="app-warning" class="app-warning-icon ml-4"></AppIcon>
                </el-tooltip>
              </div>

              <el-button
                type="primary"
                link
                @click="openGeneratePromptDialog(chat_data.model_id)"
                :disabled="!chat_data.model_id"
              >
                <AppIcon iconName="app-generate-star"></AppIcon>
              </el-button>
            </div>
          </template>
          <MdEditorMagnify
            :title="$t('views.application.form.roleSettings.label')"
            v-model="chat_data.system"
            style="height: 100px"
            @submitDialog="submitSystemDialog"
            :placeholder="`${t('views.applicationWorkflow.SystemPromptPlaceholder')}{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.application.form.prompt.label')"
          prop="prompt"
          :rules="{
            required: true,
            message: $t('views.application.form.prompt.requiredMessage'),
            trigger: 'blur',
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('views.application.form.prompt.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>{{ $t('views.application.form.prompt.tooltip') }} </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            :title="$t('views.application.form.prompt.label')"
            v-model="chat_data.prompt"
            style="height: 150px"
            @submitDialog="submitDialog"
            :placeholder="`${t('views.applicationWorkflow.UserPromptPlaceholder')}{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`"
          />
        </el-form-item>
        <el-form-item :label="$t('views.application.form.historyRecord.label')">
          <template #label>
            <div class="flex-between">
              <div>{{ $t('views.application.form.historyRecord.label') }}</div>
              <el-select v-model="chat_data.dialogue_type" type="small" style="width: 100px">
                <el-option :label="$t('views.applicationWorkflow.node')" value="NODE" />
                <el-option :label="$t('views.applicationWorkflow.workflow')" value="WORKFLOW" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-model="chat_data.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            class="w-full"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>

        <!-- MCP-->
        <div class="flex-between mb-16">
          <div class="lighter">MCP</div>
          <div>
            <el-button
              type="primary"
              class="mr-4"
              link
              @click="openMcpServersDialog"
              @refreshForm="refreshParam"
              v-if="chat_data.mcp_enable"
            >
              <AppIcon iconName="app-setting"></AppIcon>
            </el-button>
            <el-switch size="small" v-model="chat_data.mcp_enable" />
          </div>
        </div>
        <div class="w-full mb-16" v-if="chat_data.mcp_tool_ids?.length > 0">
          <template v-for="(item, index) in chat_data.mcp_tool_ids" :key="index">
            <div
              class="flex-between border border-r-6 white-bg mb-4"
              style="padding: 5px 8px"
              v-if="relatedObject(mcpToolSelectOptions, item, 'id')"
            >
              <div class="flex align-center" style="line-height: 20px">
                <el-avatar
                  v-if="relatedObject(mcpToolSelectOptions, item, 'id')?.icon"
                  shape="square"
                  :size="20"
                  style="background: none"
                  class="mr-8"
                >
                  <img
                    :src="resetUrl(relatedObject(mcpToolSelectOptions, item, 'id')?.icon)"
                    alt=""
                  />
                </el-avatar>
                <ToolIcon v-else type="MCP" class="mr-8" :size="20" />

                <div
                  class="ellipsis"
                  :title="relatedObject(mcpToolSelectOptions, item, 'id')?.name"
                >
                  {{
                    relatedObject(mcpToolSelectOptions, item, 'id')?.name ||
                    $t('common.custom') + ' MCP'
                  }}
                </div>
              </div>
              <el-button text @click="removeMcpTool(item)">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
        </div>
        <div
          v-if="chat_data.mcp_servers && chat_data.mcp_servers.length > 0"
          class="flex-between border border-r-6 white-bg mb-4"
          style="padding: 5px 8px"
        >
          <div class="flex align-center" style="line-height: 20px">
            <ToolIcon type="MCP" class="mr-8" :size="20" />
            <div class="ellipsis">
              {{ $t('common.custom') + ' MCP' }}
            </div>
          </div>
          <el-button text @click="chat_data.mcp_servers = ''">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <!-- 工具       -->
        <div class="flex-between mb-16">
          <div class="lighter">{{ $t('views.tool.title') }}</div>
          <div>
            <el-button
              type="primary"
              class="mr-4"
              link
              @click="openToolDialog"
              @refreshForm="refreshParam"
              v-if="chat_data.tool_enable"
            >
              <AppIcon iconName="app-setting"></AppIcon>
            </el-button>
            <el-switch size="small" v-model="chat_data.tool_enable" />
          </div>
        </div>
        <div class="w-full mb-16" v-if="chat_data.tool_ids?.length > 0">
          <template v-for="(item, index) in chat_data.tool_ids" :key="index">
            <div class="flex-between border border-r-6 white-bg mb-4" style="padding: 5px 8px">
              <div class="flex align-center" style="line-height: 20px">
                <el-avatar
                  v-if="relatedObject(toolSelectOptions, item, 'id')?.icon"
                  shape="square"
                  :size="20"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="resetUrl(relatedObject(toolSelectOptions, item, 'id')?.icon)" alt="" />
                </el-avatar>
                <ToolIcon v-else class="mr-8" :size="20" />

                <div class="ellipsis" :title="relatedObject(toolSelectOptions, item, 'id')?.name">
                  {{ relatedObject(toolSelectOptions, item, 'id')?.name }}
                </div>
              </div>
              <el-button text @click="removeTool(item)">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
        </div>
        <el-form-item @click.prevent v-if="chat_data.mcp_enable || chat_data.tool_enable">
          <template #label>
            <div class="flex-between">
              <span class="mr-4">
                {{ $t('views.application.form.mcp_output_enable') }}
              </span>
              <div class="flex">
                <el-switch class="ml-8" size="small" v-model="chat_data.mcp_output_enable" />
              </div>
            </div>
          </template>
        </el-form-item>
        <el-form-item @click.prevent>
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span>{{ $t('views.application.form.reasoningContent.label') }}</span>
              </div>
              <div>
                <el-button
                  type="primary"
                  link
                  @click="openReasoningParamSettingDialog"
                  @refreshForm="refreshParam"
                  class="mr-4"
                  v-if="chat_data.model_setting.reasoning_content_enable"
                >
                  <AppIcon iconName="app-setting"></AppIcon>
                </el-button>
                <el-switch
                  size="small"
                  v-model="chat_data.model_setting.reasoning_content_enable"
                />
              </div>
            </div>
          </template>
        </el-form-item>
        <el-form-item @click.prevent>
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>{{
                  $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.label')
                }}</span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  {{ $t('views.applicationWorkflow.nodes.aiChatNode.returnContent.tooltip') }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-switch size="small" v-model="chat_data.is_result" />
        </el-form-item>
      </el-form>
    </el-card>

    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshParam" />
    <GeneratePromptDialog @replace="replace" ref="GeneratePromptDialogRef" />
    <ReasoningParamSettingDialog
      ref="ReasoningParamSettingDialogRef"
      @refresh="submitReasoningDialog"
    />
    <McpServersDialog ref="mcpServersDialogRef" @refresh="submitMcpServersDialog" />
    <ToolDialog ref="toolDialogRef" @refresh="submitToolDialog" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set, groupBy } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted, inject } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import GeneratePromptDialog from '@/views/application/component/GeneratePromptDialog.vue'
import { t } from '@/locales'
import ReasoningParamSettingDialog from '@/views/application/component/ReasoningParamSettingDialog.vue'
import ToolDialog from '@/views/application/component/ToolDialog.vue'
import McpServersDialog from '@/views/application/component/McpServersDialog.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { useRoute } from 'vue-router'

import { resetUrl } from '@/utils/common'
import { relatedObject } from '@/utils/array.ts'
const getApplicationDetail = inject('getApplicationDetail') as any
const route = useRoute()

const {
  params: { id },
} = route as any

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

function submitSystemDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'system', val)
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prompt', val)
}

const model_change = (model_id?: string) => {
  if (model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshParam({})
  }
}

const defaultPrompt = `${t('views.applicationWorkflow.nodes.aiChatNode.defaultPrompt')}：
{{${t('views.applicationWorkflow.nodes.searchKnowledgeNode.label')}.data}}
${t('views.problem.title')}：
{{${t('views.applicationWorkflow.nodes.startNode.label')}.question}}`

const form = {
  model_id: '',
  system: '',
  prompt: defaultPrompt,
  dialogue_number: 1,
  is_result: true,
  temperature: null,
  max_tokens: null,
  dialogue_type: 'WORKFLOW',
  model_setting: {
    reasoning_content_start: '<think>',
    reasoning_content_end: '</think>',
    reasoning_content_enable: false,
  },
}

const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      if (!props.nodeModel.properties.node_data.model_setting) {
        set(props.nodeModel.properties.node_data, 'model_setting', {
          reasoning_content_start: '<think>',
          reasoning_content_end: '</think>',
          reasoning_content_enable: false,
        })
      }
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
const props = defineProps<{ nodeModel: any }>()

const aiChatNodeFormRef = ref<FormInstance>()

const modelOptions = ref<any>(null)
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const ReasoningParamSettingDialogRef = ref<InstanceType<typeof ReasoningParamSettingDialog>>()
const validate = () => {
  return aiChatNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

const application = getApplicationDetail()

function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'LLM',
          workspace_id: application.value?.workspace_id,
        }
      : {
          model_type: 'LLM',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
}

const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, chat_data.value.model_params_setting)
  }
}

const GeneratePromptDialogRef = ref<InstanceType<typeof GeneratePromptDialog>>()
const openGeneratePromptDialog = (modelId: string) => {
  if (modelId) {
    GeneratePromptDialogRef.value?.open(modelId, id)
  }
}
const replace = (v: any) => {
  set(props.nodeModel.properties.node_data, 'system', v)
}
const openReasoningParamSettingDialog = () => {
  ReasoningParamSettingDialogRef.value?.open(chat_data.value.model_setting)
}

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
}

function submitReasoningDialog(val: any) {
  let model_setting = cloneDeep(props.nodeModel.properties.node_data.model_setting)
  model_setting = {
    ...model_setting,
    ...val,
  }

  set(props.nodeModel.properties.node_data, 'model_setting', model_setting)
}

const mcpServersDialogRef = ref()
function openMcpServersDialog() {
  const config = {
    mcp_servers: chat_data.value.mcp_servers,
    mcp_tool_ids: chat_data.value.mcp_tool_ids,
    mcp_source: chat_data.value.mcp_source,
  }
  mcpServersDialogRef.value.open(config, mcpToolSelectOptions.value)
}

function submitMcpServersDialog(config: any) {
  set(props.nodeModel.properties.node_data, 'mcp_servers', config.mcp_servers)
  set(props.nodeModel.properties.node_data, 'mcp_tool_ids', config.mcp_tool_ids)
  set(props.nodeModel.properties.node_data, 'mcp_source', config.mcp_source)
}

const toolDialogRef = ref()
function openToolDialog() {
  toolDialogRef.value.open(chat_data.value.tool_ids)
}
function submitToolDialog(config: any) {
  set(props.nodeModel.properties.node_data, 'tool_ids', config.tool_ids)
}
function removeTool(id: any) {
  const list = props.nodeModel.properties.node_data.tool_ids.filter((v: any) => v !== id)
  set(props.nodeModel.properties.node_data, 'tool_ids', list)
}
function removeMcpTool(id: any) {
  const list = props.nodeModel.properties.node_data.mcp_tool_ids.filter((v: any) => v !== id)
  set(props.nodeModel.properties.node_data, 'mcp_tool_ids', list)
}

const toolSelectOptions = ref<any[]>([])
function getToolSelectOptions() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          scope: 'WORKSPACE',
          tool_type: 'CUSTOM',
          workspace_id: application.value?.workspace_id,
        }
      : {
          scope: 'WORKSPACE',
          tool_type: 'CUSTOM',
        }

  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getAllToolList(obj)
    .then((res: any) => {
      toolSelectOptions.value = [...res.data.shared_tools, ...res.data.tools].filter(
        (item: any) => item.is_active,
      )
    })
}

const mcpToolSelectOptions = ref<any[]>([])
function getMcpToolSelectOptions() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          scope: 'WORKSPACE',
          tool_type: 'MCP',
          workspace_id: application.value?.workspace_id,
        }
      : {
          scope: 'WORKSPACE',
          tool_type: 'MCP',
        }

  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getAllToolList(obj)
    .then((res: any) => {
      mcpToolSelectOptions.value = [...res.data.shared_tools, ...res.data.tools].filter(
        (item: any) => item.is_active,
      )
    })
}

onMounted(() => {
  getSelectModel()
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  set(props.nodeModel, 'validate', validate)
  if (!chat_data.value.dialogue_type) {
    chat_data.value.dialogue_type = 'WORKFLOW'
  }

  if (props.nodeModel.properties.node_data?.mcp_tool_id) {
    set(props.nodeModel.properties.node_data, 'mcp_tool_ids', [
      props.nodeModel.properties.node_data?.mcp_tool_id,
    ])
    set(props.nodeModel.properties.node_data, 'mcp_tool_id', undefined)
  }
  if (props.nodeModel.properties.node_data?.mcp_output_enable === undefined) {
    set(props.nodeModel.properties.node_data, 'mcp_output_enable', true)
  }

  getToolSelectOptions()
  getMcpToolSelectOptions()
})
</script>
<style lang="scss" scoped></style>
