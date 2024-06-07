<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      @submit.prevent
      :model="chat_data"
      label-position="top"
      require-asterisk-position="right"
      class="mb-24"
      label-width="auto"
      ref="baseNodeFormRef"
    >
      <el-form-item
        label="应用名称"
        prop="name"
        :rules="{
          message: '应用名称不能为空',
          trigger: 'blur',
          required: true
        }"
      >
        <el-input
          v-model="chat_data.name"
          maxlength="64"
          placeholder="请输入应用名称"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="应用描述">
        <el-input
          v-model="chat_data.desc"
          placeholder="请输入应用描述"
          :rows="3"
          type="textarea"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="开场白">
        <MdEditor
          style="height: 150px"
          v-model="chat_data.prologue"
          :preview="false"
          :toolbars="[]"
          :footers="[]"
        />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { MdEditor } from 'md-editor-v3'
const props = defineProps<{ nodeModel: any }>()

const form = {
  name: '',
  desc: '',
  prologue:
    '您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。\n- MaxKB 主要功能有什么？\n- MaxKB 支持哪些大语言模型？\n- MaxKB 支持哪些文档类型？'
}
const chat_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  }
})

const baseNodeFormRef = ref<FormInstance>()

const validate = () => {
  baseNodeFormRef.value?.validate()
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
