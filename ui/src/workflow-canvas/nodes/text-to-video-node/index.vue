<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowTextToVideoNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface TextToVideoNodeForm {
  model_id: string
  model_id_type: 'custom' | 'default' | 'reference'
  model_id_reference: string[]
  prompt: string
  negative_prompt: string
  dialogue_number: number
  dialogue_type: 'NODE' | 'WORKFLOW'
  is_result: boolean
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')

const store = useWorkflowStore(resourceScope)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: TextToVideoNodeForm = {
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  prompt: START_NODE_REFERENCES.question,
  negative_prompt: '',
  dialogue_number: 0,
  dialogue_type: 'NODE',
  is_result: true,
  model_params_setting: {},
}
const savedForm = model.properties.node_data as Partial<TextToVideoNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  prompt: savedForm?.prompt ?? defaultForm.prompt,
  negative_prompt: savedForm?.negative_prompt ?? defaultForm.negative_prompt,
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  dialogue_number: savedForm?.dialogue_number ?? defaultForm.dialogue_number,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<TextToVideoNodeForm>({
  get: () => model.properties.node_data as TextToVideoNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<TextToVideoNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}
onMounted(() => {
  model.validate = validate
  store.getModelListWithShared({ model_type: 'TTV' }).then((data) => {
    modelList.value = data
  })
  store.getProviderList().then((data) => {
    providerOptions.value = data
  })
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.node.setting') }}</h6>
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
          model-type="TTV"
          :label="t('workflow.textToVideo.model.label')"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 提示词(正向) -->
        <el-form-item
          class="mk-hide-asterisk"
          prop="prompt"
          :rules="{ whitespace: true, required: true, message: t('workflow.positivePrompt.requiredMessage'), trigger: 'blur' }"
        >
          <template #label>
            <div class="flex-align-center gap-1">
              <span class="mk-required">{{ t('workflow.positivePrompt.label') }}</span>

              <MkTooltip :content="t('workflow.textToVideo.positivePrompt.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>
          <MdEditorMagnify v-model="formData.prompt" :title="t('workflow.positivePrompt.label')" @wheel="handleNodeWheel" />
        </el-form-item>

        <!-- 提示词(负向) -->
        <el-form-item prop="negative_prompt">
          <template #label>
            <div class="flex-align-center gap-1">
              <span>{{ t('workflow.negativePrompt.label') }}</span>
              <MkTooltip :content="t('workflow.negativePrompt.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.negative_prompt"
            :title="t('workflow.negativePrompt.label')"
            :placeholder="t('workflow.negativePrompt.videoPlaceholder')"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

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
