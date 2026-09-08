<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { BaseNodeModel } from '@logicflow/core'
import MkFormList from '@/components/mk-form-list/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { compareList } from '@/workflow-canvas/config/constants'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'

defineOptions({ name: 'WorkflowLoopContinueNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

interface LoopCondition {
  field: string[]
  compare: string
  value: string | number
}
interface LoopConditionForm {
  condition: 'and' | 'or'
  condition_list: LoopCondition[]
}

// 初始化保留已有条件，沿用 v2 的空列表默认值与条件协议。
const defaultForm: LoopConditionForm = { condition: 'and', condition_list: [] }
const savedForm = model.properties.node_data as Partial<LoopConditionForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...cloneDeep(savedForm),
  condition: savedForm?.condition ?? defaultForm.condition,
  condition_list: cloneDeep(savedForm?.condition_list ?? defaultForm.condition_list),
}
const formData = computed(() => model.properties.node_data as LoopConditionForm)
const formRef = useTemplateRef<FormInstance>('formRef')
const valueLessComparisons = new Set(['is_null', 'is_not_null', 'is_true', 'is_not_true'])
const createCondition = (): LoopCondition => ({ field: [], compare: '', value: '' })

// 列表增删由 MkFormList 完成，回写独立数据并清理已移除行的浮层状态。
const anchorGuard = createAnchorGuard(model)
const conditions = computed({
  get: () => formData.value.condition_list,
  set: (conditionList: LoopCondition[]) => {
    model.properties.node_data = { ...formData.value, condition_list: cloneDeep(conditionList) }
    anchorGuard.reset()
  },
})

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
})
onBeforeUnmount(() => anchorGuard.reset())
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <div class="mk-gray-card">
        <div v-if="conditions.length > 1" class="mb-2 flex items-center gap-2 text-N600">
          <span>符合以下</span>
          <el-select
            v-model="formData.condition"
            :teleported="false"
            size="small"
            class="w-15!"
            @visible-change="anchorGuard.setOverlayVisible('condition', $event)"
            @wheel="handleNodeWheel"
          >
            <el-option label="所有" value="and" />
            <el-option label="任一" value="or" />
          </el-select>
          <span>条件</span>
        </div>

        <MkFormList v-model="conditions" :default-item="createCondition" :min-rows="0" :first-row-has-label="false" add-text="添加条件">
          <template #default="{ item: condition, index }">
            <el-form-item
              class="small min-w-0 flex-2"
              :prop="`condition_list.${index}.field`"
              :rules="{ type: 'array', required: true, message: '请选择变量', trigger: 'change' }"
            >
              <NodeCascader v-model="condition.field" :node-model="model" placeholder="请选择变量" />
            </el-form-item>
            <el-form-item
              class="small min-w-0 flex-1"
              :prop="`condition_list.${index}.compare`"
              :rules="{ required: true, message: '请选择', trigger: 'change' }"
            >
              <el-select
                v-model="condition.compare"
                :teleported="false"
                placeholder="请选择"
                clearable
                @visible-change="anchorGuard.setOverlayVisible(`${index}:compare`, $event)"
                @wheel="handleNodeWheel"
              >
                <el-option v-for="comparison in compareList" :key="comparison.value" :label="comparison.label" :value="comparison.value" />
              </el-select>
            </el-form-item>
            <div class="min-w-0 flex-1">
              <el-form-item
                v-if="!valueLessComparisons.has(condition.compare)"
                class="small"
                :prop="`condition_list.${index}.value`"
                :rules="{ required: true, message: '请输入比较值', trigger: 'blur' }"
              >
                <el-input v-model="condition.value" placeholder="请输入比较值" />
              </el-form-item>
            </div>
          </template>
        </MkFormList>
      </div>
    </el-form>
  </NodeContainer>
</template>
