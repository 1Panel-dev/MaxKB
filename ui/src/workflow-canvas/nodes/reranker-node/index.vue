<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import MkFormList from '@/components/mk-form-list/index.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import type { NodeModelData } from '@/workflow-canvas/component/node-model-select/types'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import SearchSetting from './component/SearchSetting.vue'
import type { RerankerSetting } from './types'

defineOptions({ name: 'WorkflowRerankerNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = inject<string>('apiType', 'workspace')
const model = getModel()
const store = useWorkflowStore(apiType)
const formRef = useTemplateRef<FormInstance>('formRef')

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

// 标题栏添加重排内容，深拷贝回写以保持节点历史记录的数据独立。
function addReference() {
  formData.value.reranker_reference_list = [...cloneDeep(formData.value.reranker_reference_list), []]
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
function updateModel(patch: Partial<NodeModelData>) {
  model.properties.node_data = { ...formData.value, ...patch }
}
const settingRows = computed(() => [
  { label: 'Score 高于', value: formData.value.reranker_setting.similarity.toFixed(3) },
  { label: '引用分段数 TOP', value: formData.value.reranker_setting.top_n },
  { label: '最大引用字符数', value: formData.value.reranker_setting.max_paragraph_char_number },
])
async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}
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
        <!-- 重排内容 -->
        <el-form-item
          class="mk-hide-asterisk mb-0!"
          prop="reranker_reference_list"
          :rules="{ type: 'array', required: true, message: '请选择重排内容', trigger: 'change' }"
        >
          <template #label>
            <div class="flex-between">
              <span class="mk-required">重排内容</span>
              <el-button text type="primary" title="添加重排内容" aria-label="添加重排内容" @click="addReference">
                <MkIcon name="icon_add_outlined" />
              </el-button>
            </div>
          </template>

          <MkFormList v-model="formData.reranker_reference_list" :default-item="[]" :first-row-has-label="false" :show-add-button="false">
            <template #default="{ index }">
              <el-form-item
                class="mb-2! min-w-0 flex-1"
                :prop="`reranker_reference_list.${index}`"
                :rules="{ type: 'array', required: true, message: '请选择重排内容', trigger: 'change' }"
              >
                <NodeCascader v-model="formData.reranker_reference_list[index]!" :node-model="model" placeholder="请选择重排内容" />
              </el-form-item>
            </template>
          </MkFormList>
        </el-form-item>
        <!-- 检索参数 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>检索参数</span>
              <SearchSetting v-model="formData.reranker_setting" />
            </div>
          </template>
          <div class="mk-white-card w-full">
            <ul class="space-y-2">
              <li v-for="row in settingRows" :key="row.label" class="flex gap-4">
                <span class="w-28 shrink-0 text-N600">{{ row.label }}</span>
                <span class="min-w-0 flex-1 truncate" :title="String(row.value)">{{ row.value }}</span>
              </li>
            </ul>
          </div>
        </el-form-item>
        <!-- 检索问题 -->
        <el-form-item label="检索问题" prop="question_reference_address" :rules="{ required: true, message: '请选择检索问题', trigger: 'change' }">
          <NodeCascader ref="questionCascaderRef" v-model="formData.question_reference_address" :node-model="model" placeholder="请选择检索问题" />
        </el-form-item>
        <!-- 重排模型 -->
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          :fields="{ source: 'reranker_model_id_type', id: 'reranker_model_id', reference: 'reranker_model_id_reference' }"
          model-type="RERANKER"
          label="重排模型"
          :options="modelOptions"
          :provider-options="providerOptions"
          :can-edit-params="false"
          can-add
          @update="updateModel"
          @refresh="refreshModels"
        />
        <div class="flex-between">
          <span>结果显示在知识来源中</span>
          <el-switch v-model="formData.show_knowledge" size="small" />
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
