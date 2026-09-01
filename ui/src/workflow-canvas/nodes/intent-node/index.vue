<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import { cloneDeep, set } from 'lodash'
import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/NodeContainer.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import { randomId } from '@/utils/common'

defineOptions({ name: 'WorkflowIntentNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()
const flowModel = model as unknown as { refreshBranch?: () => void }

interface IntentNodeBranch {
  id: string
  content: string
  isOther: boolean
}
interface IntentNodeForm {
  model_id: string
  model_id_reference: string[]
  model_id_type: 'custom' | 'reference'
  model_params_setting: Record<string, unknown>
  content_list: string[]
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  branch: IntentNodeBranch[]
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const contentCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('contentCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

function defaultBranch(): IntentNodeBranch[] {
  return [
    { id: randomId(), content: '', isOther: false },
    { id: randomId(), content: '其他', isOther: true },
  ]
}

const formData = computed<IntentNodeForm>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', {
        model_id: '',
        model_id_type: 'custom',
        model_id_reference: [],
        model_params_setting: {},
        content_list: [],
        dialogue_type: 'WORKFLOW',
        dialogue_number: 1,
        branch: defaultBranch(),
      })
    }
    const data = model.properties.node_data as IntentNodeForm
    if (data.model_id_type === undefined) set(data, 'model_id_type', 'custom')
    if (!Array.isArray(data.model_id_reference)) set(data, 'model_id_reference', [])
    if (!data.model_params_setting) set(data, 'model_params_setting', {})
    if (!Array.isArray(data.content_list)) set(data, 'content_list', [])
    if (data.dialogue_type === undefined) set(data, 'dialogue_type', 'WORKFLOW')
    if (data.dialogue_number === undefined || data.dialogue_number === null) {
      set(data, 'dialogue_number', 1)
    }
    if (!Array.isArray(data.branch) || data.branch.length === 0) {
      set(data, 'branch', defaultBranch())
    }
    return data
  },
  set: (value) => (model.properties.node_data = value),
})

function refreshBranch() {
  flowModel.refreshBranch?.()
}

function addBranch() {
  const list = cloneDeep(formData.value.branch)
  const obj: IntentNodeBranch = { id: randomId(), content: '', isOther: false }
  // 插入到最后一个（“其他”）之前
  list.splice(list.length - 1, 0, obj)
  set(formData.value, 'branch', list)
  refreshBranch()
}

function deleteBranch(id: string) {
  const list = cloneDeep(formData.value.branch)
  const item = list.find((branch) => branch.id === id)
  if (!item || item.isOther) return

  const deleteAnchorId = `${model.id}_${id}_right`
  const edgeIds = model.outgoing.edges
    .filter((edge) => edge.sourceAnchorId === deleteAnchorId)
    .map((edge) => edge.id)
  if (edgeIds.length > 0) {
    model.graphModel.eventCenter.emit('delete_edge', edgeIds)
  }

  const newList = list.filter((branch) => branch.id !== id)
  set(formData.value, 'branch', newList)
  refreshBranch()
}

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference'
      ? modelCascaderRef.value?.validate()
      : Promise.resolve(),
    contentCascaderRef.value?.validate(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  set(model, 'validate', validate)
  store.getModelList({ model_type: 'LLM' }).then((data) => {
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
        :rules="{ required: true, message: '请选择或填写 AI 模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>AI 模型</span>
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
          placeholder="请输入 AI 模型 ID"
          :options="modelList"
          :provider-options="providerOptions"
          v-model="formData.model_id"
        ></ModelSelect>
      </el-form-item>

      <el-form-item
        prop="content_list"
        :rules="{ required: true, message: '请选择文本内容', trigger: 'change' }"
        label="输入"
      >
        <NodeCascader
          ref="contentCascaderRef"
          v-model="formData.content_list"
          :node-model="model"
          class="w-full"
          placeholder="选择文本内容"
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

      <el-form-item>
        <template #label>
          <div class="flex-between">
            <div>
              <span>意图分类<span class="text-danger">*</span></span>
            </div>
            <el-button type="primary" size="large" link @click="addBranch">
              <MkIcon :icon="Plus" />
            </el-button>
          </div>
        </template>
        <div class="w-full">
          <div v-for="(item, index) in formData.branch" :key="item.id" class="mb-0">
            <el-form-item
              :prop="`branch.${index}.content`"
              :rules="{ required: true, message: '请输入', trigger: 'blur' }"
            >
              <div class="flex items-center gap-2 w-full">
                <div class="min-w-0 flex-1">
                  <el-input v-model="item.content" :disabled="item.isOther" placeholder="请输入" />
                </div>
                <div class="flex w-8 shrink-0 items-center justify-center">
                  <el-button
                    v-if="!item.isOther"
                    link
                    :disabled="formData.branch.filter((branch) => !branch.isOther).length <= 1"
                    @click="deleteBranch(item.id)"
                  >
                    <MkIcon :icon="Delete" />
                  </el-button>
                </div>
              </div>
            </el-form-item>
          </div>
        </div>
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
// 意图分类内嵌套的分支行收紧间距，给下方“请输入”提示预留空间。
:deep(.el-form-item .el-form-item) {
  margin-bottom: 8px;
}
</style>
