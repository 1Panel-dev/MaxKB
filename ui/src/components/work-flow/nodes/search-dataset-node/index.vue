<template>
  <NodeContaner :nodeModel="nodeModel">
    <el-form
      :model="chat_data"
      label-position="top"
      require-asterisk-position="right"
      class="mb-24"
      label-width="auto"
      ref="aiChatNodeFormRef"
    >
      <el-form-item label="知识库">
        <el-select v-model="chat_data.model" placeholder="请选择模型">
          <el-option label="Zone one" value="shanghai" />
          <el-option label="Zone two" value="beijing" />
        </el-select>
      </el-form-item>
      <el-form-item label="提示词">
        <el-input v-model="chat_data.name" />
      </el-form-item>
    </el-form>
  </NodeContaner>
</template>
<script setup lang="ts">
import NodeContaner from '@/flow/common/node-container/index.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'

const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    }
    return {}
  },
  set: (value) => {
    props.nodeModel.properties.node_data = value
  }
})
const props = defineProps<{ nodeModel: any }>()

const aiChatNodeFormRef = ref<FormInstance>()

const validate = () => {
  aiChatNodeFormRef.value?.validate()
}

onMounted(() => {
  props.nodeModel.validate = validate
})
</script>
<style lang="scss" scoped></style>
