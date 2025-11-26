<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.workflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="IntentClassifyNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
        prop="document_list"
        :label="$t('common.inputContent')"
        :rules="{
            message: $t('views.workflow.nodes.textToSpeechNode.content.label'),
            trigger: 'change',
            required: true,
        }"
      >
        <template #label>
            <div class="flex-between">
              <div>
                <span
                  >{{ $t('common.inputContent')
                  }}<span class="color-danger">*</span></span
                >
              </div>
            </div>
        </template>
        <NodeCascader
            ref="nodeCascaderRef"
            :nodeModel="nodeModel"
            class="w-full"
            :placeholder="$t('views.workflow.nodes.textToSpeechNode.content.label')"
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
  document_list: [],
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
</script>

<style lang="scss" scoped></style>
