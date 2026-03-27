<template>
  <NodeContainer :node-model="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('workflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="aiChatNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          :label="$t('workflow.nodes.imageUnderstandNode.model.label')"
          :prop="form_data.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'"
          :rules="{
            required: true,
            message:
              form_data.model_id_type === 'reference'
                ? $t('workflow.variable.placeholder')
                : $t('workflow.nodes.imageUnderstandNode.model.requiredMessage'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between w-full">
              <div>
                <span
                >{{
                    t('workflow.nodes.imageUnderstandNode.model.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-select
                v-model="form_data.model_id_type"
                :teleported="false"
                size="small"
                style="width: 85px"
                @change="form_data.model_id_reference = []"
              >
                <el-option :label="$t('workflow.variable.Referencing')" value="reference" />
                <el-option :label="$t('common.custom')" value="custom" />
              </el-select>
            </div>
          </template>
          <div class="flex-between w-full" v-if="form_data.model_id_type !== 'reference'">
            <ModelSelect
              @wheel="wheel"
              :teleported="false"
              v-model="form_data.model_id"
              :placeholder="$t('workflow.nodes.imageUnderstandNode.model.requiredMessage')"
              :options="modelOptions"
              showFooter
              :model-type="'IMAGE'"
            ></ModelSelect>
            <div class="ml-8">
              <el-button
                :disabled="!form_data.model_id"
                @click="openAIParamSettingDialog(form_data.model_id)"
                @refreshForm="refreshParam"
              >
                <el-icon>
                  <Operation />
                </el-icon>
              </el-button>
            </div>
          </div>
          <NodeCascader
            v-else
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('workflow.variable.placeholder')"
            v-model="form_data.model_id_reference"
          />
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
                @click="openGeneratePromptDialog(form_data.model_id)"
                :disabled="!form_data.model_id"
              >
                <AppIcon iconName="app-generate-star"></AppIcon>
              </el-button>
            </div>
          </template>
          <MdEditorMagnify
            :title="$t('views.application.form.roleSettings.label')"
            v-model="form_data.system"
            style="height: 100px"
            @submitDialog="submitSystemDialog"
            :placeholder="`${t('workflow.SystemPromptPlaceholder')}{{${t('workflow.nodes.startNode.label')}.question}}`"
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
                >{{
                    $t('views.application.form.prompt.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>{{ $t('views.application.form.prompt.tooltip') }}</template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            @wheel="wheel"
            :title="$t('views.application.form.prompt.label')"
            v-model="form_data.prompt"
            style="height: 150px"
            @submitDialog="submitDialog"
            :placeholder="`${t('workflow.UserPromptPlaceholder')}{{${t('workflow.nodes.startNode.label')}.question}}`"
          />
        </el-form-item>
        <el-form-item
          v-if="
            [
              WorkflowMode.Application,
              WorkflowMode.ApplicationLoop,
              WorkflowMode.Tool,
              WorkflowMode.ToolLoop,
            ].includes(workflowMode)
          "
        >
          <template #label>
            <div class="flex-between">
              <div>{{ $t('views.application.form.historyRecord.label') }}</div>
              <el-select
                v-model="form_data.dialogue_type"
                type="small"
                style="width: 100px"
                :teleported="false"
              >
                <el-option :label="$t('workflow.node')" value="NODE"/>
                <el-option :label="$t('workflow.workflow')" value="WORKFLOW"/>
              </el-select>
            </div>
          </template>
          <el-input-number
            v-model="form_data.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            class="w-full"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>
        <el-form-item
          :label="$t('workflow.nodes.imageUnderstandNode.image.label')"
          :rules="{
            type: 'array',
            required: true,
            message: $t('workflow.nodes.imageUnderstandNode.image.requiredMessage'),
            trigger: 'change',
          }"
        >
          <template #label
          >{{
              $t('workflow.nodes.imageUnderstandNode.image.label')
            }}<span class="color-danger">*</span></template
          >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('workflow.nodes.imageUnderstandNode.image.requiredMessage')"
            v-model="form_data.image_list"
          />
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
                  v-if="form_data.model_setting.reasoning_content_enable"
                >
                  <AppIcon iconName="app-setting"></AppIcon>
                </el-button>
                <el-switch
                  size="small"
                  v-model="form_data.model_setting.reasoning_content_enable"
                />
              </div>
            </div>
          </template>
        </el-form-item>
        <el-form-item
          :label="$t('workflow.nodes.aiChatNode.returnContent.label')"
          @click.prevent
          v-if="
            [
              WorkflowMode.Application,
              WorkflowMode.ApplicationLoop,
              WorkflowMode.Tool,
              WorkflowMode.ToolLoop,
            ].includes(workflowMode)
          "
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>{{ $t('workflow.nodes.aiChatNode.returnContent.label') }}</span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  {{ $t('workflow.nodes.aiChatNode.returnContent.tooltip') }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-switch size="small" v-model="form_data.is_result"/>
        </el-form-item>
      </el-form>
    </el-card>
    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshParam"/>
    <ReasoningParamSettingDialog
      ref="ReasoningParamSettingDialogRef"
      @refresh="submitReasoningDialog"
    />
    <GeneratePromptDialog @replace="replace" ref="GeneratePromptDialogRef"/>
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import {computed, onMounted, ref, inject} from 'vue'
import {cloneDeep, groupBy, set} from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type {FormInstance} from 'element-plus'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'
import {t} from '@/locales'
import {useRoute} from 'vue-router'
import {loadSharedApi} from '@/utils/dynamics-api/shared-api'
import GeneratePromptDialog from '@/views/application/component/GeneratePromptDialog.vue'
import {WorkflowMode} from '@/enums/application'
import ReasoningParamSettingDialog
  from "@/views/application/component/ReasoningParamSettingDialog.vue";

const workflowMode = (inject('workflowMode') as WorkflowMode) || WorkflowMode.Application
const getResourceDetail = inject('getResourceDetail') as any
const route = useRoute()
const ReasoningParamSettingDialogRef = ref<InstanceType<typeof ReasoningParamSettingDialog>>()
const openReasoningParamSettingDialog = () => {
  ReasoningParamSettingDialogRef.value?.open(form_data.value.model_setting)
}
const {
  params: {id},
} = route as any

const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('shared')) {
    return 'systemShare'
  } else {
    return 'workspace'
  }
})

const props = defineProps<{ nodeModel: any }>()
const modelOptions = ref<any>(null)
const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

const aiChatNodeFormRef = ref<FormInstance>()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    aiChatNodeFormRef.value?.validate(),
  ]).catch((err: any) => {
    return Promise.reject({node: props.nodeModel, errMessage: err})
  })
}

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

const defaultPrompt = `{{${t('workflow.nodes.startNode.label')}.question}}`

const form = {
  model_id: '',
  model_id_type: 'custom',
  model_id_reference: [],
  system: '',
  prompt: defaultPrompt,
  dialogue_number: 0,
  dialogue_type: 'NODE',
  is_result: true,
  temperature: null,
  max_tokens: null,
  image_list: ['start-node', 'image'],
  model_setting: {
    reasoning_content_start: '<think>',
    reasoning_content_end: '</think>',
    reasoning_content_enable: false,
  },
}

const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      if (!props.nodeModel.properties.node_data.model_id_type) {
        set(props.nodeModel.properties.node_data, 'model_id_type', 'custom')
      }
      if (!props.nodeModel.properties.node_data.model_id_reference) {
        set(props.nodeModel.properties.node_data, 'model_id_reference', [])
      }
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

const resource = getResourceDetail()

function getSelectModel() {
  const obj =
    apiType.value === 'systemManage'
      ? {
          model_type: 'IMAGE',
          workspace_id: resource.value?.workspace_id,
        }
      : {
          model_type: 'IMAGE',
        }
  loadSharedApi({ type: 'model', systemType: apiType.value })
    .getSelectModelList(obj)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
    })
}

function submitReasoningDialog(val: any) {
  let model_setting = cloneDeep(props.nodeModel.properties.node_data.model_setting)
  model_setting = {
    ...model_setting,
    ...val,
  }

  set(props.nodeModel.properties.node_data, 'model_setting', model_setting)
}

function submitSystemDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'system', val)
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prompt', val)
}

const openAIParamSettingDialog = (modelId: string) => {
  if (modelId) {
    AIModeParamSettingDialogRef.value?.open(modelId, id, form_data.value.model_params_setting)
  }
}

function refreshParam(data: any) {
  set(props.nodeModel.properties.node_data, 'model_params_setting', data)
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

onMounted(() => {
  getSelectModel()

  set(props.nodeModel, 'validate', validate)
})
</script>

<style scoped lang="scss"></style>
