<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowQuestionNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface QuestionNodeForm {
  model_id: string
  model_id_reference: string[]
  model_id_type: 'custom' | 'default' | 'reference'
  system: string
  prompt: string
  dialogue_number: number
  is_result: boolean
  model_params_setting: Record<string, unknown>
  dialogue_type: 'NODE' | 'WORKFLOW'
}

const formRef = useTemplateRef<FormInstance>('formRef')

const store = useWorkflowStore(resourceScope)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: QuestionNodeForm = {
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  system: t('workflow.questionOptimization.systemPrompt.defaultValue'),
  prompt: START_NODE_REFERENCES.question,
  dialogue_number: 1,
  is_result: false,
  model_params_setting: {},
  dialogue_type: 'NODE',
}
const savedForm = model.properties.node_data as Partial<QuestionNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  system: savedForm?.system ?? defaultForm.system,
  prompt: savedForm?.prompt ?? defaultForm.prompt,
  dialogue_number: savedForm?.dialogue_number ?? defaultForm.dialogue_number,
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<QuestionNodeForm>({
  get: () => model.properties.node_data as QuestionNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<QuestionNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  model.validate = validate
  store.getModelListWithShared({ model_type: 'LLM' }).then((data) => {
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
          model-type="LLM"
          :label="t('workflow.model.label')"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 系统提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-align-center gap-1">
              <span>{{ t('workflow.systemPrompt.label') }}</span>
              <MkTooltip :content="t('workflow.systemPrompt.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
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
        <el-form-item>
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
