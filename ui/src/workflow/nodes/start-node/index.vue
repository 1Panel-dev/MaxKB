<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">全局变量</h5>
    <div
      v-for="(item, index) in nodeModel.properties.config.globalFields"
      :key="index"
      class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
      @mouseenter="showicon = true"
      @mouseleave="showicon = false"
    >
      <span>{{ item.label }} {{ '{' + item.value + '}' }}</span>
      <el-tooltip effect="dark" content="复制参数" placement="top" v-if="showicon === true">
        <el-button
          link
          @click="copyClick('{{' + '全局变量.' + item.value + '}}')"
          style="padding: 0"
        >
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
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ nodeModel: any }>()

const showicon = ref(false)
const globalFields = [
  { label: '当前时间', value: 'time' },
  { label: '历史聊天记录', value: 'history_context' },
  { label: '对话id', value: 'chat_id' }
]
const inputFieldList = ref<any[]>([])

const getRefreshFieldList = () => {
  return props.nodeModel.graphModel.nodes
    .filter((v: any) => v.id === 'base-node')
    .map((v: any) => cloneDeep(v.properties.input_field_list))
    .reduce((x: any, y: any) => [...x, ...y], [])
    .map((i: any) => ({ label: i.name, value: i.variable }))
}
const refreshFieldList = () => {
  const refreshFieldList = getRefreshFieldList()
  set(props.nodeModel.properties.config, 'globalFields', [...globalFields, ...refreshFieldList])
}
props.nodeModel.graphModel.eventCenter.on('refreshFieldList', refreshFieldList)

onMounted(() => {
  refreshFieldList()
})
</script>
<style lang="scss" scoped></style>
