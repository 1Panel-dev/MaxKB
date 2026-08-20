<script setup lang="ts">
import { set } from 'lodash'
import type { FormInstance } from 'element-plus'
import NodeContainer from '@/workflow-canvas/core/NodeContainer.vue'
import type { BaseNodeModel } from '@logicflow/core'

defineOptions({ name: 'WorkflowBaseNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()
interface BaseNodeForm {
  desc: string
  name: string
  prologue: string
}

const formRef = useTemplateRef<FormInstance>('formRef')

const formData = computed<BaseNodeForm>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', { name: '', desc: '', prologue: '' })
    }
    return model.properties.node_data as BaseNodeForm
  },
  set: (value) => set(model.properties, 'node_data', value),
})

function validate() {
  return formRef.value
    ?.validate()
    .catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => set(model, 'validate', validate))
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form
      ref="formRef"
      :model="formData"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item
        label="名称"
        prop="name"
        :rules="{ required: true, message: '请输入智能体名称', trigger: 'blur' }"
      >
        <el-input
          v-model="formData.name"
          maxlength="64"
          placeholder="请输入智能体名称"
          show-word-limit
          @blur="formData.name = formData.name?.trim()"
        />
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="formData.desc"
          maxlength="256"
          placeholder="描述该智能体的应用场景及用途"
          :rows="3"
          show-word-limit
          type="textarea"
        />
      </el-form-item>
      <el-form-item label="开场白">
        <el-input v-model="formData.prologue" :rows="5" type="textarea" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
