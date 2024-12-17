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

const getRefreshFieldList = () => {
  const user_input_fields = props.nodeModel.graphModel.nodes
    .filter((v: any) => v.id === 'base-node')
    .map((v: any) => cloneDeep(v.properties.user_input_field_list))
    .reduce((x: any, y: any) => [...x, ...y], [])
    .map((i: any) => {
      if (i.label && i.label.input_type === 'TooltipLabel') {
        return { label: i.label.label, value: i.field || i.variable }
      }
      return { label: i.label || i.name, value: i.field || i.variable }
    })
  const api_input_fields = props.nodeModel.graphModel.nodes
    .filter((v: any) => v.id === 'base-node')
    .map((v: any) => cloneDeep(v.properties.api_input_field_list))
    .reduce((x: any, y: any) => [...x, ...y], [])
    .map((i: any) => ({ label: i.name || i.variable, value: i.variable }))

  return [...user_input_fields, ...api_input_fields]
}
const refreshFieldList = () => {
  const refreshFieldList = getRefreshFieldList()
  set(props.nodeModel.properties.config, 'globalFields', [...globalFields, ...refreshFieldList])
}
props.nodeModel.graphModel.eventCenter.on('refreshFieldList', refreshFieldList)

const refreshFileUploadConfig = () => {
  let fields = cloneDeep(props.nodeModel.properties.config.fields)
  const form_data = props.nodeModel.graphModel.nodes
    .filter((v: any) => v.id === 'base-node')
    .filter((v: any) => v.properties.node_data.file_upload_enable)
    .map((v: any) => cloneDeep(v.properties.node_data.file_upload_setting))
    .filter((v: any) => v)

  fields = fields.filter((item: any) => item.value !== 'image' && item.value !== 'document' && item.value !== 'audio' && item.value !== 'video')

  if (form_data.length === 0) {
    set(props.nodeModel.properties.config, 'fields', fields)
    return
  }
  let fileUploadFields = []
  if (form_data[0].document) {
    fileUploadFields.push({ label: '文档', value: 'document' })
  }
  if (form_data[0].image) {
    fileUploadFields.push({ label: '图片', value: 'image' })
  }
  if (form_data[0].audio) {
    fileUploadFields.push({ label: '音频', value: 'audio' })
  }
  if (form_data[0].video) {
    fileUploadFields.push({ label: '视频', value: 'video' })
  }

  set(props.nodeModel.properties.config, 'fields', [...fields, ...fileUploadFields])
}
props.nodeModel.graphModel.eventCenter.on('refreshFileUploadConfig', refreshFileUploadConfig)

onMounted(() => {
  refreshFieldList()
  refreshFileUploadConfig()
})
</script>
<style lang="scss" scoped></style>
