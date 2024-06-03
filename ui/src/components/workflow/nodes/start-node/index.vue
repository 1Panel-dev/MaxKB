<template>
  <NodeContainer :nodeModel="nodeModel" class="start-node" style="width: 320px">
    <h5 class="title-decoration-1 mb-8">全局变量</h5>
    <div class="text-bg p-8-12 mb-8">当前时 {time}</div>
    <h5 class="title-decoration-1 mb-8">参数输出</h5>
    <div class="text-bg p-8-12 mb-8">用户问题 {question}</div>
  </NodeContainer>
</template>
<script setup lang="ts">
import NodeContainer from '@/components/workflow/common/node-container/index.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { MdEditor } from 'md-editor-v3'

const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      props.nodeModel.properties.node_data = {
        name: '',
        desc: '',
        prologue:
          '您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。\n- MaxKB 主要功能有什么？\n- MaxKB 支持哪些大语言模型？\n- MaxKB 支持哪些文档类型？'
      }
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    props.nodeModel.properties.node_data = value
  }
})
const props = defineProps<{ nodeModel: any }>()
const handleFocus = () => {
  props.nodeModel.isSelected = false
}
const aiChatNodeFormRef = ref<FormInstance>()

const validate = () => {
  aiChatNodeFormRef.value?.validate()
}

onMounted(() => {
  props.nodeModel.validate = validate
})
</script>
<style lang="scss" scoped>
.start-node {
  .text-bg {
    background: var(--app-layout-bg-color);
    border-radius: 4px;
  }
}
</style>
