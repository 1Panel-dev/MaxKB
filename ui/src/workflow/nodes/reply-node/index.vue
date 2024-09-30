<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="replyNodeFormRef"
      >
        <el-form-item label="回复内容">
          <template #label>
            <div class="flex-between">
              <span>回复内容</span>
              <el-select
                :teleported="false"
                v-model="form_data.reply_type"
                size="small"
                style="width: 85px"
              >
                <el-option label="引用变量" value="referencing" />
                <el-option label="自定义" value="content" />
              </el-select>
            </div>
          </template>

          <MdEditorMagnify
            v-if="form_data.reply_type === 'content'"
            @wheel="wheel"
            title="回复内容"
            v-model="form_data.content"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
          <NodeCascader
            v-else
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题"
            v-model="form_data.fields"
          />
        </el-form-item>
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
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { ref, computed, onMounted } from 'vue'
import { isLastNode } from '@/workflow/common/data'

const props = defineProps<{ nodeModel: any }>()

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}
const form = {
  reply_type: 'content',
  content: '',
  fields: [],
  is_result: false
}

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

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'content', val)
}

const replyNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    replyNodeFormRef.value?.validate()
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  if (typeof props.nodeModel.properties.node_data?.is_result === 'undefined') {
    if (isLastNode(props.nodeModel)) {
      set(props.nodeModel.properties.node_data, 'is_result', true)
    }
  }

  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
