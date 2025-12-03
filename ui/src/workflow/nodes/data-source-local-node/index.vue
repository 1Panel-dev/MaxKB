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
      >
        <el-form-item
          :label="$t('views.workflow.nodes.dataSourceLocalNode.fileFormat.label')"
          :rules="{
            type: 'array',
            required: true,
            message: $t('views.workflow.nodes.dataSourceLocalNode.fileFormat.requiredMessage'),
            trigger: 'change',
          }"
        >
          <el-select
            v-model="form_data.file_type_list"
            :placeholder="$t('views.workflow.nodes.dataSourceLocalNode.fileFormat.requiredMessage')"
            class="w-240"
            clearable
            multiple
            allow-create
            filterable
            default-first-option
          >
            <template #label="{ label, value }">
              <span>{{ label }} </span>
            </template>
            <el-option
              v-for="item in file_type_list_options"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.dataSourceLocalNode.maxFileNumber.label')"
          :rules="{
            type: 'array',
            required: true,
            message: $t('common.inputPlaceholder'),
            trigger: 'change',
          }"
        >
          <el-input-number
            v-model="form_data.file_count_limit"
            :min="1"
            :max="1000"
            :value-on-clear="0"
            controls-position="right"
            class="w-full"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.workflow.nodes.dataSourceLocalNode.maxFileCountNumber.label')"
          :rules="{
            type: 'array',
            required: true,
            message: $t('common.inputPlaceholder'),
            trigger: 'change',
          }"
        >
          <el-input-number
            v-model="form_data.file_size_limit"
            :min="1"
            :max="1000"
            :value-on-clear="0"
            controls-position="right"
            class="w-full"
            :step="1"
            :step-strictly="true"
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

const props = defineProps<{ nodeModel: any }>()

const file_type_list_options = ['TXT', 'DOCX', 'PDF', 'HTML', 'XLS', 'XLSX', 'ZIP', 'CSV']
const form = {
  file_type_list: ['TXT', 'DOCX', 'PDF', 'HTML', 'XLS', 'XLSX', 'ZIP', 'CSV'],
  file_size_limit: 100,
  file_count_limit: 50,
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
