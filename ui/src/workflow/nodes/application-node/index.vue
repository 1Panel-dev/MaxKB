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
            ref="applicationNodeFormRef"
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
            message: '请选择文档',
            trigger: 'blur',
            required: false
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择文档"
            v-model="form_data.document_list"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('image_list') || 'image_list' in form_data"
          label="选择图片"
          prop="image_list"
          :rules="{
            message: '请选择图片',
            trigger: 'blur',
            required: false
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择图片"
            v-model="form_data.image_list"
          />
        </el-form-item>

        <el-form-item
          v-if="form_data.hasOwnProperty('audio_list') || 'audio_list' in form_data"
          label="选择语音文件"
          prop="audio_list"
          :rules="{
            message: '请选择语音文件',
            trigger: 'blur',
            required: false
          }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择语音文件"
            v-model="form_data.audio_list"
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
import { set, groupBy, create } from 'lodash'
import { app } from '@/main'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { ref, computed, onMounted, onActivated } from 'vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import applicationApi from '@/api/application'
import { isWorkFlow } from '@/utils/application'

const form = {
  question_reference_address: ['start-node', 'question'],
  api_input_field_list: [],
  user_input_field_list: [],
  document_list: ['start-node', 'document'],
  image_list: ['start-node', 'image'],
  audio_list: ['start-node', 'audio']
}

const {
  params: { id }
} = app.config.globalProperties.$route as any

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

function handleFileUpload(type: string, isEnabled: boolean) {
  const listKey = `${type}_list`
  if (isEnabled) {
    if (!props.nodeModel.properties.node_data[listKey]) {
      set(props.nodeModel.properties.node_data, listKey, [])
    }
  } else {
    // eslint-disable-next-line vue/no-mutating-props
    delete props.nodeModel.properties.node_data[listKey]
  }
}

const update_field = () => {
  if (!props.nodeModel.properties.node_data.application_id) {
    set(props.nodeModel.properties, 'status', 500)
    return
  }
  applicationApi
    .getApplicationById(id, props.nodeModel.properties.node_data.application_id)
    .then((ok) => {
      const old_api_input_field_list = props.nodeModel.properties.node_data.api_input_field_list
      const old_user_input_field_list = props.nodeModel.properties.node_data.user_input_field_list
      if (isWorkFlow(ok.data.type)) {
        const nodeData = ok.data.work_flow.nodes[0].properties.node_data
        const new_api_input_field_list = ok.data.work_flow.nodes[0].properties.api_input_field_list
        const new_user_input_field_list =
          ok.data.work_flow.nodes[0].properties.user_input_field_list
        const merge_api_input_field_list = new_api_input_field_list.map((item: any) => {
          const find_field = old_api_input_field_list.find(
            (old_item: any) => old_item.variable == item.variable
          )
          if (find_field) {
            return {
              ...item,
              value: find_field.value,
              label:
                typeof item.label === 'object' && item.label != null ? item.label.label : item.label
            }
          } else {
            return item
          }
        })
        console.log(merge_api_input_field_list)
        set(
          props.nodeModel.properties.node_data,
          'api_input_field_list',
          merge_api_input_field_list
        )
        const merge_user_input_field_list = new_user_input_field_list.map((item: any) => {
          const find_field = old_user_input_field_list.find(
            (old_item: any) => old_item.field == item.field
          )
          if (find_field) {
            return {
              ...item,
              value: find_field.value,
              label:
                typeof item.label === 'object' && item.label != null ? item.label.label : item.label
            }
          } else {
            return item
          }
        })
        set(
          props.nodeModel.properties.node_data,
          'user_input_field_list',
          merge_user_input_field_list
        )
        const fileUploadSetting = nodeData.file_upload_setting
        // 如果是true，说明有文件上传
        if (fileUploadSetting) {
          handleFileUpload('document', fileUploadSetting.document)
          handleFileUpload('image', fileUploadSetting.image)
          handleFileUpload('audio', fileUploadSetting.audio)
        } else {
          ;['document_list', 'image_list', 'audio_list'].forEach((list) => {
            // eslint-disable-next-line vue/no-mutating-props
            delete props.nodeModel.properties.node_data[list]
          })
        }
        set(props.nodeModel.properties, 'status', ok.data.id ? 200 : 500)
      }
    })
    .catch((err) => {
      // set(props.nodeModel.properties, 'status', 500)
    })
}

const props = defineProps<{ nodeModel: any }>()

const validate = () => {
  return applicationNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  update_field()
  set(props.nodeModel, 'validate', validate)
})
</script>

<style lang="scss" scoped></style>
