<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">节点设置</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="applicationNodeFormRef"
      >
        <el-form-item
          label="用户问题"
          prop="question_reference_address"
          :rules="{
            message: '请选择检索问题',
            trigger: 'blur',
            required: true
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题"
            v-model="form_data.question_reference_address"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('document_list') || 'document_list' in form_data"
          label="选择文档"
          prop="document_list"
          :rules="{
            message: '请选择检索问题',
            trigger: 'blur',
            required: false
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题"
            v-model="form_data.document_list"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('image_list') || 'image_list' in form_data"
          label="选择图片"
          prop="image_list"
          :rules="{
            message: '请选择检索问题',
            trigger: 'blur',
            required: false
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题"
            v-model="form_data.image_list"
          />
        </el-form-item>
        <div v-for="(field, index) in form_data.api_input_field_list" :key="'api-input-' + index">
          <el-form-item
            :label="field.variable"
            :prop="'api_input_field_list.' + index + '.value'"
            :rules="[
              { required: field.is_required, message: `请输入${field.variable}`, trigger: 'blur' }
            ]"
          >
            <NodeCascader
              ref="nodeCascaderRef"
              :nodeModel="nodeModel"
              class="w-full"
              placeholder="请选择检索问题"
              v-model="form_data.api_input_field_list[index].value"
            />
          </el-form-item>
        </div>

        <div v-for="(field, index) in form_data.user_input_field_list" :key="'user-input-' + index">
          <el-form-item
            :label="field.label"
            :prop="'user_input_field_list.' + index + '.value'"
            :rules="[
              { required: field.required, message: `请输入${field.label}`, trigger: 'blur' }
            ]"
          >
            <NodeCascader
              ref="nodeCascaderRef"
              :nodeModel="nodeModel"
              class="w-full"
              placeholder="请选择检索问题"
              v-model="form_data.user_input_field_list[index].value"
            />
          </el-form-item>
        </div>
        <el-form-item label="返回内容" @click.prevent>
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>返回内容<span class="danger">*</span></span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  关闭后该节点的内容则不输出给用户。
                  如果你想让用户看到该节点的输出内容，请打开开关。
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <el-switch size="small" v-model="form_data.is_result" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import { set, groupBy } from 'lodash'
import { app } from '@/main'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { ref, computed, onMounted } from 'vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'

const form = {
  question_reference_address: ['start-node', 'question'],
  api_input_field_list: [],
  user_input_field_list: [],
  document_list: ['start-node', 'document'],
  image_list: ['start-node', 'image']
}

const applicationNodeFormRef = ref<FormInstance>()

const form_data = computed({
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

const props = defineProps<{ nodeModel: any }>()

const validate = () => {
  return applicationNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>

<style lang="scss" scoped></style>
