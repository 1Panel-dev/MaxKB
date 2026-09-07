<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import SelectModel from '@/components/business/select-model/index.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import ParamSettingDialog from './component/ParamSettingDialog.vue'
import type { RerankerSetting } from './types'

defineOptions({ name: 'WorkflowRerankerNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = inject<string>('apiType', 'workspace')
const model = getModel()
const store = useWorkflowStore(apiType)
const formRef = useTemplateRef<FormInstance>('formRef')
const questionCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('questionCascaderRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const paramSettingDialogRef = useTemplateRef<InstanceType<typeof ParamSettingDialog>>('paramSettingDialogRef')

interface RerankerForm {
  reranker_reference_list: string[][]
  reranker_model_id: string
  reranker_model_id_type: 'default' | 'custom' | 'reference'
  reranker_model_id_reference: string[]
  question_reference_address: string[]
  reranker_setting: RerankerSetting
  show_knowledge: boolean
}

// 一次性补齐旧数据，缺少模型来源的旧节点保留自定义语义。
const defaultForm: RerankerForm = {
  reranker_reference_list: [[]],
  reranker_model_id: '',
  reranker_model_id_type: 'default',
  reranker_model_id_reference: [],
  question_reference_address: [],
  reranker_setting: { top_n: 3, similarity: 0, max_paragraph_char_number: 5000 },
  show_knowledge: false,
}
const savedForm = model.properties.node_data as Partial<RerankerForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  reranker_reference_list: Array.isArray(savedForm?.reranker_reference_list)
    ? savedForm.reranker_reference_list
    : defaultForm.reranker_reference_list,
  reranker_model_id_type: savedForm ? (savedForm.reranker_model_id_type ?? 'custom') : defaultForm.reranker_model_id_type,
  reranker_model_id_reference: Array.isArray(savedForm?.reranker_model_id_reference) ? savedForm.reranker_model_id_reference : [],
  question_reference_address: Array.isArray(savedForm?.question_reference_address) ? savedForm.question_reference_address : [],
  reranker_setting: { ...defaultForm.reranker_setting, ...savedForm?.reranker_setting },
  show_knowledge: savedForm?.show_knowledge ?? false,
}
const formData = computed(() => model.properties.node_data as RerankerForm)

// 重排内容允许删除到空列表，交由必填规则提示。
function addReference() {
  formData.value.reranker_reference_list = [...cloneDeep(formData.value.reranker_reference_list), []]
}
function removeReference(index: number) {
  formData.value.reranker_reference_list = cloneDeep(formData.value.reranker_reference_list.filter((_, referenceIndex) => referenceIndex !== index))
}

// 模型来源与重排参数
const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const getRerankerModels = inject<() => Promise<ModelItem[]>>('getRerankerModels', () => store.getModelList({ model_type: 'RERANKER' }))
function refreshModels() {
  return getRerankerModels().then((models) => {
    modelOptions.value = models
  })
}
const defaultModelSetting = computed(() => model.getDefaultModelConfig('RERANKER'))
function changeModelSource() {
  formData.value.reranker_model_id_reference = []
  formRef.value?.clearValidate(['reranker_model_id', 'reranker_model_id_reference'])
}
function openParamSetting() {
  paramSettingDialogRef.value?.open(formData.value.reranker_setting)
}
function updateParamSetting(setting: RerankerSetting) {
  formData.value.reranker_setting = cloneDeep(setting)
}
function validate() {
  return Promise.all([questionCascaderRef.value?.validate(), modelCascaderRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}
const anchorGuard = createAnchorGuard(model)
onBeforeUnmount(() => anchorGuard.reset())
onMounted(() => {
  model.validate = validate
  refreshModels()
  store.getProviderList().then((providers) => {
    providerOptions.value = providers
  })
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item
          class="mk-hide-asterisk"
          prop="reranker_reference_list"
          :rules="{ type: 'array', required: true, message: '请选择重排内容', trigger: 'change' }"
        >
          <template #label>
            <div class="flex-between">
              <span class="mk-required">重排内容</span>
              <el-button link type="primary" title="添加重排内容" @click="addReference"><MkIcon name="icon_add_outlined" /></el-button>
            </div>
          </template>
          <div class="flex w-full flex-col gap-2">
            <div v-for="(_, index) in formData.reranker_reference_list" :key="index" class="flex items-start gap-2">
              <el-form-item
                class="min-w-0 flex-1"
                :prop="`reranker_reference_list.${index}`"
                :rules="{ type: 'array', required: true, message: '请选择重排内容', trigger: 'change' }"
              >
                <NodeCascader v-model="formData.reranker_reference_list[index]!" :node-model="model" placeholder="请选择重排内容" />
              </el-form-item>
              <el-button text title="删除重排内容" @click="removeReference(index)"
                ><MkIcon name="icon_delete-trash_outlined" class="text-N600"
              /></el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>检索参数</span>
              <el-button text type="primary" title="参数设置" @click="openParamSetting"><MkIcon name="icon-setting" /></el-button>
            </div>
          </template>
          <div class="grid w-full grid-cols-2 gap-y-1">
            <span class="text-N600">Score 高于</span><span>{{ formData.reranker_setting.similarity.toFixed(3) }}</span>
            <span class="text-N600">引用分段数 TOP</span><span>{{ formData.reranker_setting.top_n }}</span>
            <span class="text-N600">最大引用字符数</span><span>{{ formData.reranker_setting.max_paragraph_char_number }}</span>
          </div>
        </el-form-item>
        <el-form-item label="检索问题" prop="question_reference_address" :rules="{ required: true, message: '请选择检索问题', trigger: 'change' }">
          <NodeCascader ref="questionCascaderRef" v-model="formData.question_reference_address" :node-model="model" placeholder="请选择检索问题" />
        </el-form-item>
        <el-form-item
          class="mk-hide-asterisk"
          :prop="formData.reranker_model_id_type === 'reference' ? 'reranker_model_id_reference' : 'reranker_model_id'"
          :rules="{
            required: formData.reranker_model_id_type !== 'default',
            message: formData.reranker_model_id_type === 'reference' ? '请选择引用变量' : '请选择重排模型',
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between">
              <span class="mk-required">重排模型</span>
              <el-select
                v-model="formData.reranker_model_id_type"
                :teleported="false"
                class="w-22!"
                size="small"
                @change="changeModelSource"
                @visible-change="anchorGuard.setOverlayVisible('model-source', $event)"
                @wheel="handleNodeWheel"
              >
                <el-option label="默认模型" value="default" /><el-option label="引用变量" value="reference" /><el-option
                  label="自定义"
                  value="custom"
                />
              </el-select>
            </div>
          </template>
          <SelectModel
            v-if="formData.reranker_model_id_type === 'custom'"
            v-model="formData.reranker_model_id"
            :options="modelOptions"
            :provider-options="providerOptions"
            can-add
            :teleported="false"
            @visible-change="anchorGuard.setOverlayVisible('model', $event)"
            @wheel="handleNodeWheel"
            placeholder="请选择重排模型"
            @refresh="refreshModels"
          />
          <SelectModel
            v-else-if="formData.reranker_model_id_type === 'default'"
            :model-value="defaultModelSetting?.model_id ?? ''"
            :options="modelOptions"
            :provider-options="providerOptions"
            disabled
            placeholder="未配置默认模型"
          />
          <NodeCascader
            v-else
            ref="modelCascaderRef"
            v-model="formData.reranker_model_id_reference"
            :node-model="model"
            placeholder="请选择引用变量"
          />
        </el-form-item>
        <div class="flex-between">
          <span>结果显示在知识来源中</span>
          <el-switch v-model="formData.show_knowledge" size="small" />
        </div>
      </el-form>
    </div>
    <ParamSettingDialog ref="paramSettingDialogRef" @submit="updateParamSetting" />
  </NodeContainer>
</template>
