<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import { fileTooltip } from '@/workflow-canvas/config/constants'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowVideoUnderstandNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface ReasoningSetting {
  reasoning_content_enable: boolean
  reasoning_content_end: string
  reasoning_content_start: string
}

interface VideoUnderstandNodeForm {
  model_id: string
  model_params_setting: Record<string, unknown>
  model_id_type: 'custom' | 'default' | 'reference'
  model_id_reference: string[]
  model_setting: ReasoningSetting
  prompt: string
  system: string
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  video_list: string[]
  is_result: boolean
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const videoCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('videoCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: VideoUnderstandNodeForm = {
  model_id: '',
  model_params_setting: {},
  model_id_type: 'default',
  model_id_reference: [],
  model_setting: {
    reasoning_content_enable: false,
    reasoning_content_end: '</think>',
    reasoning_content_start: '<think>',
  },
  prompt: '{{开始.question}}',
  system: '',
  dialogue_type: 'NODE',
  dialogue_number: 0,
  video_list: ['start-node', 'video'],
  is_result: true,
}
const savedForm = model.properties.node_data as Partial<VideoUnderstandNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  model_setting: {
    reasoning_content_enable: savedForm?.model_setting?.reasoning_content_enable ?? defaultForm.model_setting.reasoning_content_enable,
    reasoning_content_end: savedForm?.model_setting?.reasoning_content_end ?? defaultForm.model_setting.reasoning_content_end,
    reasoning_content_start: savedForm?.model_setting?.reasoning_content_start ?? defaultForm.model_setting.reasoning_content_start,
  },
  prompt: savedForm?.prompt ?? defaultForm.prompt,
  system: savedForm?.system ?? defaultForm.system,
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  dialogue_number: savedForm?.dialogue_number ?? defaultForm.dialogue_number,
  video_list: savedForm ? (Array.isArray(savedForm.video_list) ? savedForm.video_list : []) : defaultForm.video_list,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<VideoUnderstandNodeForm>({
  get: () => model.properties.node_data as VideoUnderstandNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const modelSetting = computed(() => {
  const defaultModel = model.getDefaultModelConfig('IMAGE')
  const isDefaultModel = formData.value.model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.model_id,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})
const modelFormProp = computed(() => (formData.value.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'))
const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<VideoUnderstandNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function changeModelSource(source: VideoUnderstandNodeForm['model_id_type']) {
  updateNodeData({ model_id_reference: [], model_id_type: source })
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (formData.value.model_id_type === 'reference') {
    callback(formData.value.model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(
    modelSetting.value.model_id
      ? undefined
      : new Error(formData.value.model_id_type === 'default' ? '请在默认模型设置中选择视觉模型' : '请选择视觉模型'),
  )
}

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference' ? modelCascaderRef.value?.validate() : Promise.resolve(),
    videoCascaderRef.value?.validate(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
  store.getModelList({ model_type: 'IMAGE' }).then((data) => {
    modelList.value = data
  })
  store.getProviderList().then((data) => {
    providerOptions.value = data
  })
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-3">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item class="mk-hide-asterisk" :prop="modelFormProp" :rules="{ validator: validateModel, trigger: 'change' }">
          <template #label>
            <div class="flex-between">
              <span class="mk-required">视觉模型</span>
              <el-select :model-value="formData.model_id_type" :teleported="false" class="w-22!" size="small" @update:model-value="changeModelSource">
                <el-option label="默认模型" value="default" />
                <el-option label="引用变量" value="reference" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <ModelSelect
            v-if="formData.model_id_type === 'default'"
            :model-value="modelSetting.model_id"
            :model-params="modelSetting.model_params_setting"
            disabled
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else-if="formData.model_id_type === 'custom'"
            :model-value="formData.model_id"
            :model-params="formData.model_params_setting"
            can-edit-params
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="请选择视觉模型"
            @update:model-value="updateNodeData({ model_id: $event })"
            @update:model-params="updateNodeData({ model_params_setting: $event })"
          />
          <NodeCascader
            v-else
            ref="modelCascaderRef"
            :model-value="formData.model_id_reference"
            :node-model="model"
            class="w-full"
            placeholder="请选择变量"
            @update:model-value="updateNodeData({ model_id_reference: $event })"
          />
        </el-form-item>

        <!-- 系统提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div class="flex items-center gap-1">
                <span>系统提示词</span>
                <el-tooltip content="设定模型扮演的角色或遵循的指令" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </div>
              <div class="-mr-1">
                <!-- // TODO: 生成 统一处理 -->
                <el-button type="primary" text :disabled="!formData.model_id">
                  <MkIcon name="icon_star"></MkIcon>
                </el-button>
              </div>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.system"
            title="系统提示词"
            placeholder="系统提示词，可以引用系统中变量，如 {{开始.question}}"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 用户提示词 -->
        <el-form-item class="mk-hide-asterisk" prop="prompt" :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }">
          <template #label>
            <div class="flex items-center gap-1">
              <span class="mk-required">用户提示词</span>
              <el-tooltip content="用户向模型提出的问题或输入的指令" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </div>
          </template>

          <MdEditorMagnify
            v-model="formData.prompt"
            title="用户提示词"
            placeholder="用户提示词，可以引用系统中变量，如 {{开始.question}}"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item v-if="showSettings">
          <template #label>
            <div class="flex-between">
              <span>历史聊天记录</span>
              <el-select v-model="formData.dialogue_type" :teleported="false" class="w-18!" size="small">
                <el-option label="节点" value="NODE" />
                <el-option label="工作流" value="WORKFLOW" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-model="formData.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            align="left"
            class="w-full!"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>

        <!-- 选择视频 -->
        <el-form-item class="mk-hide-asterisk" prop="video_list" :rules="{ required: true, message: '请选择', trigger: 'change' }">
          <template #label>
            <span class="flex items-center gap-1">
              <span class="mk-required">选择视频</span>
              <el-tooltip placement="right">
                <template #content>
                  <!-- // TODO: ? -->
                  <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </span>
          </template>
          <NodeCascader ref="videoCascaderRef" v-model="formData.video_list" :node-model="model" class="w-full" placeholder="请选择" />
        </el-form-item>

        <!-- 输出思考 -->
        <div class="flex-between mb-4">
          <span>输出思考</span>
          <div class="flex items-center gap-2">
            <!-- // TODO: 输出思考 统一处理 -->
            <el-button type="primary" text v-if="formData.model_setting.reasoning_content_enable">
              <MkIcon name="icon-setting" />
            </el-button>
            <el-switch v-model="formData.model_setting.reasoning_content_enable" size="small" />
          </div>
        </div>

        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex items-center gap-1">
            返回内容
            <el-tooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
