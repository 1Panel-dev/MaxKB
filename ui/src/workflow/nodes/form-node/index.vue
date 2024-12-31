<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">节点设置</h5>
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form
        @submit.prevent
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        ref="formNodeFormRef"
        hide-required-asterisk
      >
        <el-form-item
          label="表单输出内容"
          prop="form_content_format"
          :rules="{
            required: true,
            message: '请表单输出内容',
            trigger: 'blur'
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span>表单输出内容<span class="danger">*</span></span>
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  设置执行该节点输出的内容，{{ '{ form }' }}为表单的占位符。
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            title="表单输出内容"
            v-model="form_data.form_content_format"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item label="表单配置" @click.prevent>
          <template #label>
            <div class="flex-between">
              <h5 class="lighter">{{ '表单配置' }}</h5>
              <el-button link type="primary" @click="openAddFormCollect()">
                <el-icon class="mr-4">
                  <Plus />
                </el-icon>
                添加
              </el-button>
            </div></template
          >

          <el-table
            class="border"
            v-if="form_data.form_field_list.length > 0"
            :data="form_data.form_field_list"
          >
            <el-table-column prop="field" label="参数">
              <template #default="{ row }">
                <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="label" label="显示名称">
              <template #default="{ row }">
                <span v-if="row.label && row.label.input_type === 'TooltipLabel'">
                  <span :title="row.label.label" class="ellipsis-1">
                    {{ row.label.label }}
                  </span>
                </span>
                <span v-else>
                  <span :title="row.label" class="ellipsis-1">
                    {{ row.label }}
                  </span></span
                >
              </template>
            </el-table-column>

            <el-table-column label="组件类型" width="110px">
              <template #default="{ row }">
                <el-tag type="info" class="info-tag">{{
                  input_type_list.find((item) => item.value === row.input_type)?.label
                }}</el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="default_value" label="默认值">
              <template #default="{ row }">
                <span :title="row.default_value" class="ellipsis-1">{{
                  getDefaultValue(row)
                }}</span>
              </template>
            </el-table-column>
            <el-table-column label="必填">
              <template #default="{ row }">
                <div @click.stop>
                  <el-switch disabled size="small" v-model="row.required" />
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="left" width="80">
              <template #default="{ row, $index }">
                <span class="mr-4">
                  <el-tooltip effect="dark" content="修改" placement="top">
                    <el-button type="primary" text @click.stop="openEditFormCollect(row, $index)">
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <el-tooltip effect="dark" content="删除" placement="top">
                  <el-button type="primary" text @click="deleteField(row)">
                    <el-icon>
                      <Delete />
                    </el-icon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
    </el-card>
    <AddFormCollect ref="addFormCollectRef" :addFormField="addFormField"></AddFormCollect>
    <EditFormCollect ref="editFormCollectRef" :editFormField="editFormField"></EditFormCollect>
  </NodeContainer>
</template>
<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import AddFormCollect from '@/workflow/common/AddFormCollect.vue'
import EditFormCollect from '@/workflow/common/EditFormCollect.vue'
import { type FormInstance } from 'element-plus'
import { ref, onMounted, computed } from 'vue'
import { input_type_list } from '@/components/dynamics-form/constructor/data'
import { MsgError } from '@/utils/message'
import { set, cloneDeep } from 'lodash'
const props = defineProps<{ nodeModel: any }>()
const formNodeFormRef = ref<FormInstance>()
const editFormField = (form_field_data: any, field_index: number) => {
  const _value = form_data.value.form_field_list.map((item: any, index: number) => {
    if (field_index === index) {
      return cloneDeep(form_field_data)
    }
    return cloneDeep(item)
  })
  form_data.value.form_field_list = _value
  sync_form_field_list()
}
const addFormField = (form_field_data: any) => {
  if (form_data.value.form_field_list.some((field: any) => field.field === form_field_data.field)) {
    MsgError('参数已存在:' + form_field_data.field)
    return
  }
  form_data.value.form_field_list = cloneDeep([...form_data.value.form_field_list, form_field_data])
  sync_form_field_list()
}
const sync_form_field_list = () => {
  const fields = [
    {
      label: '表单全部内容',
      value: 'form_data'
    },
    ...form_data.value.form_field_list.map((item: any) => ({
      value: item.field,
      label: typeof item.label == 'string' ? item.label : item.label.label
    }))
  ]
  set(props.nodeModel.properties.config, 'fields', fields)
}
const addFormCollectRef = ref<InstanceType<typeof AddFormCollect>>()
const editFormCollectRef = ref<InstanceType<typeof EditFormCollect>>()
const openAddFormCollect = () => {
  addFormCollectRef.value?.open()
}
const openEditFormCollect = (form_field_data: any, index: number) => {
  editFormCollectRef.value?.open(cloneDeep(form_field_data), index)
}
const deleteField = (form_field_data: any) => {
  form_data.value.form_field_list = form_data.value.form_field_list.filter(
    (field: any) => field.field !== form_field_data.field
  )
  sync_form_field_list()
}
const form = ref<any>({
  is_result: true,
  form_content_format: `你好，请先填写下面表单内容：
{{form}}
填写后请点击【提交】按钮进行提交。`,
  form_field_list: []
})
const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form.value)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  }
})

const getDefaultValue = (row: any) => {
  if (row.default_value) {
    const default_value = row.option_list
      ?.filter((v: any) => row.default_value.indexOf(v.value) > -1)
      .map((v: any) => v.label)
      .join(',')
    if (default_value) {
      return default_value
    }
    return row.default_value
  }
  if (row.default_value !== undefined) {
    return row.default_value
  }
}

const validate = () => {
  return formNodeFormRef.value?.validate()
}
function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'form_content_format', val)
}
onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  sync_form_field_list()
  props.nodeModel.graphModel.eventCenter.emit('refresh_incoming_node_field')
})
</script>
<style lang="scss" scoped></style>
