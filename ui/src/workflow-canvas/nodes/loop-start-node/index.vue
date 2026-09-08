<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form-item>
        <LoopFieldTable :node-model="model" />
      </el-form-item>
    </div>
    <template v-if="loopInputFields.length">
      <h6 class="mk-title-decoration mb-2 mt-4">循环变量</h6>
      <div class="mk-gray-card space-y-4">
        <template v-for="(item, index) in loopInputFields" :key="index">
          <div class="group flex-between">
            <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
            <el-tooltip effect="dark" content="复制参数" placement="top">
              <el-button class="group-hover-visible" link @click="copyText(`{{loop.${item.value}}}`)">
                <MkIcon name="icon_copy_outlined" />
              </el-button>
            </el-tooltip>
          </div>
        </template>
      </div>
    </template>
  </NodeContainer>
</template>
<script setup lang="ts">
import { computed, inject } from 'vue'
import type { BaseNodeModel } from '@logicflow/core'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import LoopFieldTable from './component/LoopFieldTable.vue'
import { copyText } from '@/utils/clipboard'
import { isLoopBuiltinField } from './constant'

defineOptions({ name: 'WorkflowLoopStartNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()

interface LoopInputField {
  field?: string
  label?: string
  variable?: string
}

const loopInputFields = computed(() => {
  const list = (model.properties as { loop_input_field_list?: LoopInputField[] }).loop_input_field_list ?? []
  return list
    .map((item) => ({ label: item.label ?? item.field ?? '', value: item.field ?? item.variable ?? '' }))
    .filter((field) => Boolean(field.value) && !isLoopBuiltinField(field.value))
})
</script>
