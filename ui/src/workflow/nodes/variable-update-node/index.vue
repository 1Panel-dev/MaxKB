<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="variableUpdateNodeFormRef"
      >
        <el-form-item label="变量">
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择变量"
            v-model="form_data.fields"
          />
        </el-form-item>
        <el-form-item label="值">
          <template #label>
            <div class="flex-between">
              <span>值</span>
              <el-select
                :teleported="false"
                v-model="form_data.value_type"
                size="small"
                style="width: 85px"
              >
                <el-option label="引用变量" value="referencing" />
                <el-option label="自定义" value="content" />
              </el-select>
            </div>
          </template>

          <MdEditorMagnify
            v-if="form_data.value_type === 'content'"
            @wheel="wheel"
            title="变量值"
            v-model="form_data.content"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
          <NodeCascader
            v-else
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            placeholder="请选择引用变量"
            v-model="form_data.target_value"
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
import { ref, computed, onMounted } from 'vue'

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
  value_type: 'content',
  content: '',
  fields: [],
  target_value: []
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

const variableUpdateNodeFormRef = ref()
const nodeCascaderRef = ref()
const validate = () => {
  return Promise.all([
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
    variableUpdateNodeFormRef.value?.validate()
  ]).catch((err: any) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
