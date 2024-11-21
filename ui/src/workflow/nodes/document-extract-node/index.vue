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
        ref="DatasetNodeFormRef"
      >
        <el-form-item label="选择文档" :rules="{
            type: 'array',
            required: true,
            message: '请选择文件',
            trigger: 'change'
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
      </el-form>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed } from 'vue'
import { set } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'

const props = defineProps<{ nodeModel: any }>()

const form = {
  document_list: ["start-node", "document"]
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

</script>

<style lang="scss" scoped>

</style>