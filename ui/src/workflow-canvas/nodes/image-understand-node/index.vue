<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import ThinkingSetting from '@/workflow-canvas/component/ThinkingSetting.vue'
import { fileTooltip } from '@/workflow-canvas/config/constants'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode, type ReasoningSettingData } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowImageUnderstandNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface ImageUnderstandNodeForm {
  model_id: string
  model_params_setting: Record<string, unknown>
  model_id_type: 'custom' | 'default' | 'reference'
  model_id_reference: string[]
  model_setting: ReasoningSettingData
  prompt: string
  system: string
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  image_list: string[]
  is_result: boolean
}

const formRef = useTemplateRef<FormInstance>('formRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: ImageUnderstandNodeForm = {
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
  image_list: ['start-node', 'image'],
  is_result: true,
}
const savedForm = model.properties.node_data as Partial<ImageUnderstandNodeForm> | undefined
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
  image_list: savedForm ? (Array.isArray(savedForm.image_list) ? savedForm.image_list : []) : defaultForm.image_list,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<ImageUnderstandNodeForm>({
  get: () => model.properties.node_data as ImageUnderstandNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<ImageUnderstandNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="IMAGE"
          label="视觉模型"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

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
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>

        <!-- 选择图片 -->
        <el-form-item class="mk-hide-asterisk" prop="image_list" :rules="{ required: true, message: '请选择', trigger: 'change' }">
          <template #label>
            <span class="flex items-center gap-1">
              <span class="mk-required">选择图片</span>
              <el-tooltip placement="right">
                <template #content>
                  <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </span>
          </template>
          <NodeCascader ref="imageCascaderRef" v-model="formData.image_list" :node-model="model" placeholder="请选择" />
        </el-form-item>

        <!-- 输出思考 -->
        <div class="flex-between mb-4">
          <span>输出思考</span>
          <div class="flex items-center gap-2">
            <ThinkingSetting v-model="formData.model_setting" v-if="formData.model_setting.reasoning_content_enable" />
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
