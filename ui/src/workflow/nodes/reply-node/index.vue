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
          <MdEditor
            class=""
            style="height: 150px"
            v-model="form_data.content"
            :preview="false"
            :toolbars="[]"
            :footers="footers"
          >
            <template #defFooters>
              <el-button text>
                <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
              </el-button>
            </template>
          </MdEditor>
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { MdEditor } from 'md-editor-v3'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{ nodeModel: any }>()
const form = {
  content: ''
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
<style lang="scss" scoped></style>
