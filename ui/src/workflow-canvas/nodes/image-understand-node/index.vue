<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { ReasoningSettingData } from '@/workflow-canvas/types'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import PromptGenerate from '@/workflow-canvas/component/PromptGenerate.vue'
import ThinkingSetting from '@/workflow-canvas/component/ThinkingSetting.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { FILE_REFERENCE_EXAMPLE, START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'WorkflowImageUnderstandNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
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

const store = useWorkflowStore(resourceScope)
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
  prompt: START_NODE_REFERENCES.question,
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

// 提示词生成使用当前生效的模型；引用变量在运行前无法确定模型。
const promptModelId = computed(() => {
  if (formData.value.model_id_type === 'reference') return ''
  return formData.value.model_id_type === 'default' ? (model.getDefaultModelConfig('IMAGE')?.model_id ?? '') : formData.value.model_id
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
  store.getModelListWithShared({ model_type: 'IMAGE' }).then((data) => {
    modelList.value = data
  })
  store.getProviderList().then((data) => {
    providerOptions.value = data
  })
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.nodeSettings.title') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="formRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="IMAGE"
          :label="t('model.types.image.label')"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 系统提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div class="flex-align-center gap-1">
                <span>{{ t('workflow.systemPrompt.label') }}</span>
                <MkTooltip :content="t('workflow.systemPrompt.description')" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </div>
              <div class="-mr-1">
                <!-- 生成系统提示词 -->
                <PromptGenerate :model-id="promptModelId" :model-params-setting="formData.model_params_setting" @replace="formData.system = $event" />
              </div>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.system"
            :title="t('workflow.systemPrompt.label')"
            :placeholder="t('workflow.systemPrompt.placeholder', { reference: START_NODE_REFERENCES.question })"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 用户提示词 -->
        <el-form-item
          class="mk-hide-asterisk"
          prop="prompt"
          :rules="{ whitespace: true, required: true, message: t('workflow.userPrompt.requiredMessage'), trigger: 'blur' }"
        >
          <template #label>
            <div class="flex-align-center gap-1">
              <span class="mk-required">{{ t('workflow.userPrompt.label') }}</span>
              <MkTooltip :content="t('workflow.userPrompt.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>

          <MdEditorMagnify
            v-model="formData.prompt"
            :title="t('workflow.userPrompt.label')"
            :placeholder="t('workflow.userPrompt.placeholder', { reference: START_NODE_REFERENCES.question })"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item v-if="showSettings">
          <template #label>
            <div class="flex-between">
              <span>{{ t('workflow.history.label') }}</span>
              <!-- 选择历史记录来源 -->
              <el-select v-model="formData.dialogue_type" :teleported="false" class="w-18!" size="small">
                <el-option :label="t('workflow.node.title')" value="NODE" />
                <el-option :label="t('workflow.title')" value="WORKFLOW" />
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
        <el-form-item
          class="mk-hide-asterisk"
          prop="image_list"
          :rules="{ required: true, message: t('common.validation.selectRequired'), trigger: 'change' }"
        >
          <template #label>
            <span class="flex-align-center gap-1">
              <span class="mk-required">{{ t('upload.types.image') }}</span>
              <MkTooltip placement="right">
                <template #content>
                  <div class="font-mono whitespace-pre-wrap">{{ `${t('common.labels.example')}：\n${FILE_REFERENCE_EXAMPLE}` }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </span>
          </template>
          <NodeCascader ref="imageCascaderRef" v-model="formData.image_list" :node-model="model" :placeholder="t('common.placeholders.select')" />
        </el-form-item>

        <!-- 输出思考 -->
        <div class="flex-between mb-4">
          <span>{{ t('workflow.thinking.label') }}</span>
          <div class="flex-align-center gap-2">
            <ThinkingSetting v-model="formData.model_setting" v-if="formData.model_setting.reasoning_content_enable" />
            <!-- 切换输出思考 -->
            <el-switch v-model="formData.model_setting.reasoning_content_enable" size="small" />
          </div>
        </div>

        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex-align-center gap-1">
            {{ t('workflow.returnContent.label') }}
            <MkTooltip :content="t('workflow.returnContent.description')" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
          <span>
            <!-- 切换返回内容 -->
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
