<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('workflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="KnowledgeWriteRef"
        hide-required-asterisk
      >
        <el-form-item
          prop="document_list"
          :label="$t('common.inputContent')"
          :rules="{
            message: $t('workflow.nodes.textToSpeechNode.content.label'),
            trigger: 'change',
            required: true,
          }"
        >
          <template #label>
            <div class="flex-between">
              <div>
                <span>{{ $t('common.inputContent') }}<span class="color-danger">*</span></span>
              </div>
            </div>
          </template>
          <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('workflow.nodes.textToSpeechNode.content.label')"
            v-model="form_data.document_list"
          />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>

<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import { computed, onMounted, ref } from 'vue'
import { set } from 'lodash'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { isLastNode } from '@/workflow/common/data'

const props = defineProps<{ nodeModel: any }>()
const KnowledgeWriteRef = ref()
const nodeCascaderRef = ref()
const form = {
  document_list: [],
}

const validate = async () => {
  let ps = [
    KnowledgeWriteRef.value?.validate(),
    nodeCascaderRef.value ? nodeCascaderRef.value.validate() : Promise.resolve(''),
  ]
  return Promise.all(ps).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
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
  },
})

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
