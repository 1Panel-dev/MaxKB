<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        @mousedown.stop
        @keydown.stop
        @click.stop
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
              <el-button text type="info" @click="openDialog">
                <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
              </el-button>
            </template>
          </MdEditor>
          <NodeCascader
            v-else
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择检索问题输入"
            v-model="form_data.fields"
          />
        </el-form-item>
      </el-form>
    </el-card>
    <!-- 回复内容弹出层 -->
    <el-dialog v-model="dialogVisible" title="回复内容" append-to-body>
      <MdEditor v-model="cloneContent" :preview="false" :toolbars="[]" :footers="[]"> </MdEditor>
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> 确认 </el-button>
        </div>
      </template>
    </el-dialog>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
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

const dialogVisible = ref(false)
const cloneContent = ref('')

function openDialog() {
  cloneContent.value = form_data.value.content
  dialogVisible.value = true
}

function submitDialog() {
  set(props.nodeModel.properties.node_data, 'content', cloneContent.value)
  dialogVisible.value = false
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
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped>
.reply-node-editor {
  :deep(.md-editor-footer) {
    border: none !important;
  }
}
</style>
