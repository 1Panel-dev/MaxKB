<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <LoopFieldTable :nodeModel="nodeModel"></LoopFieldTable>
    <template v-if="loop_input_fields?.length">
      <h5 class="title-decoration-1 mb-8">
        {{ $t('views.applicationWorkflow.nodes.loopStartNode.loopVariable') }}
      </h5>
      <div
        v-for="(item, index) in loop_input_fields || []"
        :key="index"
        class="flex-between border-r-6 p-8-12 mb-8 layout-bg lighter"
        @mouseenter="showicon = true"
        @mouseleave="showicon = false"
      >
        <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
        <el-tooltip
          effect="dark"
          :content="$t('views.applicationWorkflow.setting.copyParam')"
          placement="top"
          v-if="showicon === true"
        >
          <el-button link @click="copyClick(`{{loop.${item.value}}}`)" style="padding: 0">
            <AppIcon iconName="app-copy"></AppIcon>
          </el-button>
        </el-tooltip>
      </div>
    </template>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import LoopFieldTable from '@/workflow/nodes/loop-start-node/component/LoopFieldTable.vue'
import { ref, onMounted, computed, watch } from 'vue'
import { copyClick } from '@/utils/clipboard'
const props = defineProps<{ nodeModel: any }>()
const loop_input_fields = computed(() => {
  return (
    props.nodeModel.properties.loop_input_field_list
      ? props.nodeModel.properties.loop_input_field_list
      : []
  ).map((i: any) => {
    if (i.label && i.label.input_type === 'TooltipLabel') {
      return { label: i.label.label, value: i.field || i.variable }
    }
    return { label: i.label || i.name, value: i.field || i.variable }
  })
})
watch(loop_input_fields, () => {
  props.nodeModel.graphModel.refresh_loop_fields(cloneDeep(loop_input_fields.value))
})
const showicon = ref(false)

onMounted(() => {
  props.nodeModel.graphModel.refresh_loop_fields(cloneDeep(loop_input_fields.value))
})
</script>
<style lang="scss" scoped></style>
