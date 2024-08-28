<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-16">节点设置</h5>
    <h5 class="lighter mb-8">输入变量</h5>
    <el-form
      @submit.prevent
      ref="FunctionNodeFormRef"
      :model="chat_data"
      label-position="top"
      require-asterisk-position="right"
      hide-required-asterisk
    >
      <el-card shadow="never" class="card-never mb-16" style="--el-card-padding: 12px">
        <div v-if="chat_data.input_field_list?.length > 0">
          <template v-for="(item, index) in chat_data.input_field_list" :key="item.name">
            <el-form-item
              :label="item.name"
              :prop="'input_field_list.' + index + '.value'"
              :rules="{
                required: item.is_required,
                message: '请输入变量值',
                trigger: 'blur'
              }"
            >
              <template #label>
                <div class="flex-between">
                  <div class="flex">
                    <span class="flex">
                      <auto-tooltip :content="item.name" style="max-width: 130px">
                        {{ item.name }}
                      </auto-tooltip>
                      <span class="danger" v-if="item.is_required">*</span></span
                    >
                    <el-tag type="info" class="info-tag ml-4">{{ item.type }}</el-tag>
                  </div>
                </div>
              </template>
              <NodeCascader
                v-if="item.source === 'reference'"
                ref="nodeCascaderRef"
                :nodeModel="nodeModel"
                class="w-full"
                placeholder="请选择变量"
                v-model="item.value"
              />
              <el-input v-else v-model="item.value" placeholder="请输入变量值" />
            </el-form-item>
          </template>
        </div>

        <el-text type="info" v-else> 暂无数据 </el-text>
      </el-card>
      <el-form-item label="返回内容" @click.prevent>
        <template #label>
          <div class="flex align-center">
            <div class="mr-4">
              <span>返回内容<span class="danger">*</span></span>
            </div>
            <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
              <template #content>
                关闭后该节点的内容则不输出给用户。 如果你想让用户看到该节点的输出内容，请打开开关。
              </template>
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-switch size="small" v-model="chat_data.is_result" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { isLastNode } from '@/workflow/common/data'
import applicationApi from '@/api/application'
import { app } from '@/main'
const props = defineProps<{ nodeModel: any }>()

const nodeCascaderRef = ref()
const {
  params: { id }
} = app.config.globalProperties.$route as any
const form = {
  input_field_list: [],
  is_result: false
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

const FunctionNodeFormRef = ref<FormInstance>()

const validate = () => {
  return FunctionNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

const update_field = () => {
  applicationApi
    .getFunctionLib(id, props.nodeModel.properties.node_data.function_lib_id)
    .then((ok) => {
      const old_input_field_list = props.nodeModel.properties.node_data.input_field_list
      const merge_input_field_list = ok.data.input_field_list.map((item: any) => {
        const find_field = old_input_field_list.find((old_item: any) => old_item.name == item.name)
        if (find_field && find_field.source == item.source) {
          return { ...item, value: JSON.parse(JSON.stringify(find_field.value)) }
        }
        return { ...item, value: item.source == 'reference' ? [] : '' }
      })
      set(props.nodeModel.properties.node_data, 'input_field_list', merge_input_field_list)
      set(props.nodeModel.properties, 'status', 200)
    })
    .catch((err) => {
      set(props.nodeModel.properties, 'status', 500)
    })
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }
  update_field()
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
