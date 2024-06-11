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
              <el-select v-model="form_data.reply_type" size="small" style="width: 85px">
                <el-option label="引用变量" value="referencing" />
                <el-option label="自定义" value="content" />
              </el-select>
            </div>
          </template>
          <MdEditor
            v-if="form_data.reply_type === 'content'"
            class="reply-node-editor"
            style="height: 150px"
            v-model="form_data.content"
            :preview="false"
            :toolbars="[]"
            :footers="footers"
          >
            <template #defFooters>
              <el-button text type="info">
                <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
              </el-button>
            </template>
          </MdEditor>
          <NodeCascader
            v-else
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题输入"
            v-model="form_data.fields"
          />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { MdEditor } from 'md-editor-v3'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ nodeModel: any }>()
const form = {
  reply_type: 'content',
  content: '',
  fields: []
}
const footers: any = [null, '=', 0]

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
// onMounted(() => {
//   set(props.nodeModel, 'validate', validate)
// })
</script>
<style lang="scss" scoped>
.reply-node-editor {
  :deep(.md-editor-footer) {
    border: none !important;
  }
}
</style>
