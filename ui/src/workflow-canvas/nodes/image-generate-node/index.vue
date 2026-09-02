<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { set } from 'lodash'
import { QuestionFilled } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'

defineOptions({ name: 'WorkflowImageGenerateNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()

interface ImageGenerateNodeForm {
  model_id: string
  model_id_type: 'custom' | 'reference'
  model_id_reference: string[]
  prompt: string
  negative_prompt: string
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const formData = computed<ImageGenerateNodeForm>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', {
        model_id: '',
        model_id_type: 'custom',
        model_id_reference: [],
        prompt: '{{开始.question}}',
        negative_prompt: '',
        model_params_setting: {},
      })
    }
    const data = model.properties.node_data as ImageGenerateNodeForm
    if (data.model_id_type === undefined) set(data, 'model_id_type', 'custom')
    if (!Array.isArray(data.model_id_reference)) set(data, 'model_id_reference', [])
    if (data.prompt === undefined) set(data, 'prompt', '{{开始.question}}')
    if (data.negative_prompt === undefined) set(data, 'negative_prompt', '')
    if (!data.model_params_setting) set(data, 'model_params_setting', {})
    return data
  },
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference'
      ? modelCascaderRef.value?.validate()
      : Promise.resolve(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  set(model, 'validate', validate)
  store.getModelList({ model_type: 'TTI' }).then((data) => {
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
        :rules="{ required: true, message: '请选择或填写图片生成模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>图片生成模型</span>
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
          placeholder="请输入图片生成模型 ID"
          :options="modelList"
          :provider-options="providerOptions"
          v-model="formData.model_id"
        ></ModelSelect>
      </el-form-item>

      <el-form-item
        label="提示词(正向)"
        prop="prompt"
        :rules="{ required: true, message: '请输入正向提示词', trigger: 'blur' }"
      >
        <template #label>
          <div class="flex items-center gap-1">
            <span>提示词(正向)</span>
            <el-tooltip effect="dark" placement="right" content="正向提示词，用来描述生成图像中期望包含的元素和视觉特点。">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-input
          v-model="formData.prompt"
          :rows="5"
          :placeholder="`正向提示词，可以引用变量，如 {{开始.question}}`"
          type="textarea"
        />
      </el-form-item>

      <el-form-item label="提示词(负向)" prop="negative_prompt">
        <template #label>
          <div class="flex items-center gap-1">
            <span>提示词(负向)</span>
            <el-tooltip effect="dark" placement="right" content="反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-input
          v-model="formData.negative_prompt"
          :rows="4"
          placeholder="请描述不想生成的图片内容，比如：颜色、血腥内容"
          type="textarea"
        />
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
