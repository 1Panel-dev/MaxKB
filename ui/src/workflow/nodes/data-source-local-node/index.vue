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
          :label="$t('views.workflow.nodes.dataSourceLocalNode.fileFormat.label', '支持的文件格式')"
          :rules="{
            type: 'array',
            required: true,
            message: $t(
              'views.workflow.nodes.dataSourceLocalNode.fileFormat.message',
              '请选择文件格式',
            ),
            trigger: 'change',
          }"
        >
          <el-select
            v-model="form_data.file_type_list"
            :placeholder="
              $t(
                'views.workflow.nodes.dataSourceLocalNode.fileFormat.placeholder',
                '请选择文件格式',
              )
            "
            style="width: 240px"
            clearable
            multiple
            filterable
            allow-create
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
          :label="
            $t('views.workflow.nodes.dataSourceLocalNode.maxFileNumber.label', '每次上传最大文件数')
          "
          :rules="{
            type: 'array',
            required: true,
            message: $t(
              'views.workflow.nodes.dataSourceLocalNode.maxFileNumber.placeholder',
              '请输入最大文件数',
            ),
            trigger: 'change',
          }"
        >
          <el-slider v-model="form_data.file_count_limit" show-input />
        </el-form-item>
        <el-form-item
          :label="
            $t(
              'views.workflow.nodes.dataSourceLocalNode.maxFileNumber.label',
              '上传的每个文档最大(MB)',
            )
          "
          :rules="{
            type: 'array',
            required: true,
            message: $t(
              'views.workflow.nodes.dataSourceLocalNode.maxFileNumber.placeholder',
              '上传的每个文档最大(MB) 必填',
            ),
            trigger: 'change',
          }"
        >
          <el-slider v-model="form_data.file_size_limit" show-input />
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
  file_type_list: [],
  file_size_limit: 50,
  file_count_limit: 100,
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
