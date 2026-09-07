<template>
  <div class="workflow-loop-body relative overflow-visible p-4">
    <div class="step-container" :class="{ isSelected: nodeSelected, error: nodeStatus !== 200 }">
      <div class="flex-between">
        <div class="flex min-w-0 items-center gap-2">
          <component :is="iconComponent(`${model.type}-icon`)" class="mr-1" :size="24" :item="model.properties.node_data" />
          <h4 class="truncate break-all" :title="String(model.properties.stepName ?? '')">{{ model.properties.stepName }}</h4>
        </div>
        <div class="flex items-center gap-1" @mousedown.stop @keydown.stop @click.stop>
          <el-button text @click="layout">
            <MkIcon name="icon_magnify_outlined" />
          </el-button>
          <el-button text @click="showNode = !showNode">
            <MkIcon name="icon_down_outlined" />
          </el-button>
        </div>
      </div>
      <el-collapse-transition>
        <div v-show="showNode" class="mt-2">
          <div :style="`height:${canvasHeight}px`"><slot /></div>
        </div>
      </el-collapse-transition>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import { iconComponent } from '@/workflow-canvas/icons/utils'

defineOptions({ name: 'WorkflowLoopBodyContainer' })
const props = defineProps<{ nodeModel: BaseNodeModel }>()
const model = computed(() => props.nodeModel)

const nodeSelected = ref(model.value.isSelected)
watch(() => model.value.isSelected, (value) => (nodeSelected.value = value))

const nodeStatus = computed(() => (model.value.properties.status as number | undefined) ?? 200)

const showNode = computed({
  get: () => {
    if (model.value.properties.showNode !== undefined) return model.value.properties.showNode
    set(model.value.properties, 'showNode', true)
    return true
  },
  set: (v) => set(model.value.properties, 'showNode', v),
})

const canvasHeight = ref(1000)

function layout() {
  model.value.loopLayout?.()
}
</script>
<style lang="scss" scoped>
.workflow-loop-body {
  .step-container {
    box-sizing: border-box;
    border-radius: 8px;
    border: 2px solid #fff;
    background: #fff;
    box-shadow: 0 2px 4px 0 rgb(var(--el-text-color-primary-rgb) / 12%);
    &:hover {
      box-shadow: 0 6px 24px 0 rgb(var(--el-text-color-primary-rgb) / 8%);
    }
    &.isSelected {
      border-color: var(--mk-primary);
    }
    &.error {
      border-color: var(--mk-danger);
      border-width: 1px;
    }
  }
}
</style>
