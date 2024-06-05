<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">节点设置</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="chat_data"
        label-position="top"
        require-asterisk-position="right"
        class="mb-24"
        label-width="auto"
        ref="aiChatNodeFormRef"
      >
        <el-form-item
          label="模型"
          prop="model"
          :rules="{
            message: '模型不能为空',
            trigger: 'blur',
            required: true
          }"
        >
          <el-select v-model="chat_data.model" placeholder="请选择模型">
            <el-option label="Zone one" value="shanghai" />
            <el-option label="Zone two" value="beijing" />
          </el-select>
        </el-form-item>
        <el-form-item
          label="提示词"
          :rules="{
            message: '提示词不能为空',
            trigger: 'blur',
            required: true
          }"
          prop="name"
        >
          <el-input v-model="chat_data.name" @focus="handleFocus" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/components/workflow/common/node-container/index.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'

const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      props.nodeModel.properties.node_data = { model: '', name: '' }
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
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
