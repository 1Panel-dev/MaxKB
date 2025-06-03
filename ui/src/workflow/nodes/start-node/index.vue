<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.variable.global') }}</h5>
    <div
      v-for="(item, index) in nodeModel.properties.config.globalFields"
      :key="index"
      class="flex-between border-r-4 p-8-12 mb-8 layout-bg lighter"
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
import { ref, computed, onMounted } from 'vue'
import { t } from '@/locales'
const props = defineProps<{ nodeModel: any }>()

const showicon = ref(false)
const globalFields = [
  { label: t('views.applicationWorkflow.nodes.startNode.currentTime'), value: 'time' },
  {
    label: t('views.application.applicationForm.form.historyRecord.label'),
    value: 'history_context'
  },
  { label: t('chat.chatId'), value: 'chat_id' }
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

  fields = fields.filter(
    (item: any) =>
      item.value !== 'image' &&
      item.value !== 'document' &&
      item.value !== 'audio' &&
      item.value !== 'video' &&
      item.value !== 'other'
  )

  if (form_data.length === 0) {
    set(props.nodeModel.properties.config, 'fields', fields)
    return
  }
  let fileUploadFields = []
  if (form_data[0].document) {
    fileUploadFields.push({ label: t('common.fileUpload.document'), value: 'document' })
  }
  if (form_data[0].image) {
    fileUploadFields.push({ label: t('common.fileUpload.image'), value: 'image' })
  }
  if (form_data[0].audio) {
    fileUploadFields.push({ label: t('common.fileUpload.audio'), value: 'audio' })
  }
  if (form_data[0].video) {
    fileUploadFields.push({ label: t('common.fileUpload.video'), value: 'video' })
  }
  if (form_data[0].other) {
    fileUploadFields.push({ label: t('common.fileUpload.other'), value: 'other' })
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
