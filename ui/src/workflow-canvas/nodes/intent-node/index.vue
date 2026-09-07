<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
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

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

function defaultBranch(): IntentNodeBranch[] {
  return [
    { id: randomId(), content: '', isOther: false },
    { id: randomId(), content: '其他', isOther: true },
  ]
}

const defaultForm: IntentNodeForm = {
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  model_params_setting: {},
  content_list: [],
  dialogue_type: 'WORKFLOW',
  dialogue_number: 1,
  branch: defaultBranch(),
}
const savedForm = model.properties.node_data as Partial<IntentNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  content_list: Array.isArray(savedForm?.content_list) ? savedForm.content_list : [],
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  dialogue_number: savedForm?.dialogue_number ?? defaultForm.dialogue_number,
  branch: Array.isArray(savedForm?.branch) && savedForm.branch.length ? savedForm.branch : defaultBranch(),
}

const formData = computed<IntentNodeForm>({
  get: () => model.properties.node_data as IntentNodeForm,
  set: (value) => (model.properties.node_data = value),
})

function updateModelSetting(setting: Partial<IntentModelSetting>) {
  model.properties.node_data = { ...formData.value, ...setting }
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

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="LLM"
          label="AI 模型"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateModelSetting"
        />

        <!-- 输入 -->
        <el-form-item prop="content_list" :rules="{ required: true, message: '请选择', trigger: 'change' }" label="输入">
          <NodeCascader ref="contentCascaderRef" v-model="formData.content_list" :node-model="model" placeholder="请选择" />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item>
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
