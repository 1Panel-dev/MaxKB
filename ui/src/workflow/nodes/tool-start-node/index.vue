<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('workflow.variable.global') }}</h5>
    <div
      v-for="(item, index) in nodeModel.properties.config.globalFields"
      :key="index"
      class="flex-between border-r-6 p-8-12 mb-8 layout-bg lighter"
      @mouseenter="showicon = true"
      @mouseleave="showicon = false"
    >
      <span class="break-all">{{ item.label }} {{ '{' + item.value + '}' }}</span>
      <el-tooltip effect="dark" :content="$t('workflow.setting.copyParam')" placement="top">
        <el-button link @click="copyClick(`{{global.${item.value}}}`)" style="padding: 0">
          <AppIcon iconName="app-copy"></AppIcon>
        </el-button>
      </el-tooltip>
    </div>
  </NodeContainer>
</template>
<script setup lang="ts">
import { cloneDeep, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { copyClick } from '@/utils/clipboard'
import { ref, onMounted } from 'vue'
const showicon = ref(false)
const props = defineProps<{ nodeModel: any }>()
const getRefreshFieldList = () => {
  const user_input_fields = props.nodeModel.graphModel.nodes
    .filter((v: any) => v.id === 'tool-base-node')
    .map((v: any) => cloneDeep(v.properties.user_input_field_list))
    .reduce((x: any, y: any) => [...x, ...y], [])
    .map((i: any) => {
      return { label: i.label || i.name, value: i.field }
    })
  return [...user_input_fields]
}
const refreshFieldList = () => {
  const refreshFieldList = getRefreshFieldList()
  set(props.nodeModel.properties.config, 'globalFields', refreshFieldList)
}
props.nodeModel.graphModel.eventCenter.on('refreshFieldList', refreshFieldList)
onMounted(() => {})
</script>
<style lang="scss" scoped></style>
