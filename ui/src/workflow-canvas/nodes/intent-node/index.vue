<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import { randomId } from '@/utils/common'

defineOptions({ name: 'WorkflowIntentNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
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
  model_id_type: 'custom' | 'default' | 'reference'
  model_params_setting: Record<string, unknown>
  content_list: string[]
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  branch: IntentNodeBranch[]
}
type IntentModelSetting = Pick<IntentNodeForm, 'model_id' | 'model_id_reference' | 'model_id_type' | 'model_params_setting'>

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

// 节点初始化时补齐默认值和兼容旧数据，computed 只读取表单。
if (!model.properties.node_data) {
  model.properties.node_data = {
    model_id: '',
    model_id_type: 'default',
    model_id_reference: [],
    model_params_setting: {},
    content_list: [],
    dialogue_type: 'WORKFLOW',
    dialogue_number: 1,
    branch: defaultBranch(),
  }
}
const initialNodeData = model.properties.node_data as IntentNodeForm
if (initialNodeData.model_id_type === undefined) initialNodeData.model_id_type = 'custom'
if (!Array.isArray(initialNodeData.model_id_reference)) initialNodeData.model_id_reference = []
if (!initialNodeData.model_params_setting) initialNodeData.model_params_setting = {}
if (!Array.isArray(initialNodeData.content_list)) initialNodeData.content_list = []
if (initialNodeData.dialogue_type === undefined) initialNodeData.dialogue_type = 'WORKFLOW'
if (initialNodeData.dialogue_number === undefined || initialNodeData.dialogue_number === null) {
  initialNodeData.dialogue_number = 1
}
if (!Array.isArray(initialNodeData.branch) || initialNodeData.branch.length === 0) {
  initialNodeData.branch = defaultBranch()
}

const formData = computed<IntentNodeForm>({
  get: () => model.properties.node_data as IntentNodeForm,
  set: (value) => (model.properties.node_data = value),
})

// 默认来源读取应用配置，同时保留节点原来的自定义模型和参数。
const modelSetting = computed<IntentModelSetting>(() => {
  const defaultModel = model.getDefaultModelConfig('LLM')
  const isDefaultModel = formData.value.model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.model_id,
    model_id_reference: formData.value.model_id_reference,
    model_id_type: formData.value.model_id_type,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})

const modelFormProp = computed(() => (formData.value.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'))

function updateModelSetting(setting: Partial<IntentModelSetting>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function changeModelSource(source: IntentNodeForm['model_id_type']) {
  updateModelSetting({ model_id_reference: [], model_id_type: source })
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  const { model_id_type, model_id, model_id_reference } = modelSetting.value
  if (model_id_type === 'reference') {
    callback(model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(model_id ? undefined : new Error(model_id_type === 'default' ? '请在默认模型设置中选择 AI 模型' : '请选择 AI 模型'))
}

function refreshBranch() {
  flowModel.refreshBranch?.()
}

function addBranch() {
  const list = cloneDeep(formData.value.branch)
  const obj: IntentNodeBranch = { id: randomId(), content: '', isOther: false }
  // 插入到最后一个（“其他”）之前
  list.splice(list.length - 1, 0, obj)
  formData.value.branch = list
  refreshBranch()
}

function deleteBranch(id: string) {
  const list = cloneDeep(formData.value.branch)
  const item = list.find((branch) => branch.id === id)
  if (!item || item.isOther) return

  const deleteAnchorId = `${model.id}_${id}_right`
  const edgeIds = model.outgoing.edges.filter((edge) => edge.sourceAnchorId === deleteAnchorId).map((edge) => edge.id)
  if (edgeIds.length > 0) {
    model.graphModel.eventCenter.emit('delete_edge', edgeIds)
  }

  formData.value.branch = list.filter((branch) => branch.id !== id)
  refreshBranch()
}

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference' ? modelCascaderRef.value?.validate() : Promise.resolve(),
    contentCascaderRef.value?.validate(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
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
    <h6 class="mk-title-decoration mb-3">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item class="mk-hide-asterisk" :prop="modelFormProp" :rules="{ validator: validateModel, trigger: 'change' }">
          <template #label>
            <div class="flex-between">
              <span class="mk-required">AI 模型</span>
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
            placeholder="请选择 AI 模型"
            @update:model-value="updateModelSetting({ model_id: $event })"
            @update:model-params="updateModelSetting({ model_params_setting: $event })"
          />
          <NodeCascader
            v-else
            ref="modelCascaderRef"
            :model-value="formData.model_id_reference"
            :node-model="model"
            class="w-full"
            placeholder="请选择变量"
            @update:model-value="updateModelSetting({ model_id_reference: $event })"
          />
        </el-form-item>

        <!-- 输入 -->
        <el-form-item prop="content_list" :rules="{ required: true, message: '请选择', trigger: 'change' }" label="输入">
          <NodeCascader ref="contentCascaderRef" v-model="formData.content_list" :node-model="model" class="w-full" placeholder="请选择" />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item label="历史聊天记录">
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

        <!-- 意图分类 -->

        <div class="flex-between mb-2">
          <span class="mk-required">意图分类</span>
          <el-button type="primary" text class="-mr-1" @click="addBranch">
            <MkIcon name="icon_add_outlined" />
          </el-button>
        </div>
        <template v-for="(item, index) in formData.branch" :key="item.id">
          <el-form-item :prop="`branch.${index}.content`" :rules="{ required: true, message: '请输入', trigger: 'blur' }" class="small">
            <div class="flex items-center gap-2 w-full">
              <div class="min-w-0 flex-1">
                <el-input v-model="item.content" :disabled="item.isOther" placeholder="请输入" />
              </div>
              <div class="flex w-4 shrink-0 items-center justify-center">
                <el-button
                  v-if="!item.isOther"
                  text
                  :disabled="formData.branch.filter((branch) => !branch.isOther).length <= 1"
                  @click="deleteBranch(item.id)"
                >
                  <MkIcon name="icon_delete-trash_outlined" />
                </el-button>
              </div>
            </div>
          </el-form-item>
        </template>
      </el-form>
    </div>
  </NodeContainer>
</template>
<style lang="scss" scoped></style>
