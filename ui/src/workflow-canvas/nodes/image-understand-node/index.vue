<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { set } from 'lodash'
import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/NodeContainer.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'

defineOptions({ name: 'WorkflowImageUnderstandNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()

interface ImageUnderstandNodeForm {
  model_id: string
  model_id_type: 'custom' | 'reference'
  model_id_reference: string[]
  model_setting: { reasoning_content_enable: boolean }
  prompt: string
  system: string
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  image_list: string[]
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const imageCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('imageCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const formData = computed<ImageUnderstandNodeForm>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', {
        model_id: '',
        model_id_type: 'custom',
        model_id_reference: [],
        model_setting: { reasoning_content_enable: false },
        prompt: '{{开始.question}}',
        system: '',
        dialogue_type: 'WORKFLOW',
        dialogue_number: 1,
        image_list: [],
      })
    }
    const data = model.properties.node_data as ImageUnderstandNodeForm
    if (data.model_id_type === undefined) set(data, 'model_id_type', 'custom')
    if (!Array.isArray(data.model_id_reference)) set(data, 'model_id_reference', [])
    if (!data.model_setting) set(data, 'model_setting', { reasoning_content_enable: false })
    if (data.prompt === undefined) set(data, 'prompt', '{{开始.question}}')
    if (data.system === undefined) set(data, 'system', '')
    if (data.dialogue_type === undefined) set(data, 'dialogue_type', 'WORKFLOW')
    if (data.dialogue_number === undefined || data.dialogue_number === null) {
      set(data, 'dialogue_number', 1)
    }
    if (!Array.isArray(data.image_list)) set(data, 'image_list', [])
    return data
  },
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference'
      ? modelCascaderRef.value?.validate()
      : Promise.resolve(),
    imageCascaderRef.value?.validate(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  set(model, 'validate', validate)
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
    <h6 class="mb-3">节点设置</h6>
    <el-form
      ref="formRef"
      :model="formData"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item
        :prop="formData.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'"
        :rules="{ required: true, message: '请选择或填写视觉模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>视觉模型</span>
            <el-select
              v-model="formData.model_id_type"
              :teleported="false"
              class="w-30!"
              size="small"
              @change="formData.model_id_reference = []"
            >
              <el-option label="引用变量" value="reference" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </template>
        <NodeCascader
          v-if="formData.model_id_type === 'reference'"
          ref="modelCascaderRef"
          v-model="formData.model_id_reference"
          :node-model="model"
          class="w-full"
          placeholder="请选择变量"
        />
        <ModelSelect
          v-else
          placeholder="请输入视觉模型 ID"
          :options="modelList"
          :provider-options="providerOptions"
          v-model="formData.model_id"
        ></ModelSelect>
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="flex items-center gap-1">
            <span>系统提示词</span>
            <el-tooltip effect="dark" placement="right" content="设定模型扮演的角色或遵循的指令">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-input
          v-model="formData.system"
          :rows="4"
          :placeholder="`系统提示词，可以引用变量，如 {{开始.question}}`"
          type="textarea"
        />
      </el-form-item>

      <el-form-item
        label="用户提示词"
        prop="prompt"
        :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }"
      >
        <template #label>
          <div class="flex items-center gap-1">
            <span>用户提示词</span>
            <el-tooltip effect="dark" placement="right" content="用户向模型提出的问题或输入的指令">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-input
          v-model="formData.prompt"
          :rows="5"
          :placeholder="`用户提示词，可以引用变量，如 {{开始.question}}`"
          type="textarea"
        />
      </el-form-item>

      <el-form-item label="历史聊天记录">
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span class="whitespace-nowrap">历史聊天记录</span>
            <el-select
              v-model="formData.dialogue_type"
              :teleported="false"
              class="w-20"
              size="small"
            >
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
          class="w-full!"
          :step="1"
          :step-strictly="true"
        />
      </el-form-item>

      <el-form-item
        label="选择图片"
        prop="image_list"
        :rules="{ required: true, message: '请选择图片', trigger: 'change' }"
      >
        <NodeCascader
          ref="imageCascaderRef"
          v-model="formData.image_list"
          :node-model="model"
          class="w-full"
          placeholder="选择图片"
        />
      </el-form-item>

      <el-form-item label="返回思考过程">
        <el-switch v-model="formData.model_setting.reasoning_content_enable" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<style lang="scss" scoped>
:deep(.el-form-item__label) {
  width: 100%;
}
:deep(.el-form-item) {
  margin-bottom: 16px;
}
</style>
