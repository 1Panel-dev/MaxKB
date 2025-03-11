<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
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
          :label="$t('views.applicationWorkflow.nodes.formNode.formContent.label')"
          prop="form_content_format"
          :rules="{
            required: true,
            message: $t('views.applicationWorkflow.nodes.formNode.formContent.requiredMessage'),
            trigger: 'blur'
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('views.applicationWorkflow.nodes.formNode.formContent.label')
                  }}<span class="danger">*</span></span
                >
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  {{
                    $t('views.applicationWorkflow.nodes.formNode.formContent.tooltip', {
                      form: '{ form }'
                    })
                  }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            :title="$t('views.applicationWorkflow.nodes.formNode.formContent.label')"
            v-model="form_data.form_content_format"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.formNode.formSetting')"
          @click.prevent
        >
          <template #label>
            <div class="flex-between">
              <h5 class="lighter">
                {{ $t('views.applicationWorkflow.nodes.formNode.formSetting') }}
              </h5>
              <el-button link type="primary" @click="openAddFormCollect()">
                <el-icon class="mr-4">
                  <Plus />
                </el-icon>
                {{ $t('common.add') }}
              </el-button>
            </div></template
          >

          <el-table
            class="border"
            v-if="form_data.form_field_list.length > 0"
            :data="form_data.form_field_list"
            ref="tableRef"
            row-key="field"
          >
            <el-table-column
              prop="field"
              :label="$t('dynamicsForm.paramForm.field.label')"
              width="95"
            >
              <template #default="{ row }">
                <span :title="row.field" class="ellipsis-1">{{ row.field }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="label" :label="$t('dynamicsForm.paramForm.name.label')">
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

            <el-table-column :label="$t('dynamicsForm.paramForm.input_type.label')" width="110px">
              <template #default="{ row }">
                <el-tag type="info" class="info-tag">{{
                  input_type_list.find((item) => item.value === row.input_type)?.label
                }}</el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="default_value" :label="$t('dynamicsForm.default.label')">
              <template #default="{ row }">
                <span :title="row.default_value" class="ellipsis-1">{{
                  getDefaultValue(row)
                }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.required')" width="85">
              <template #default="{ row }">
                <div @click.stop>
                  <el-switch disabled size="small" v-model="row.required" />
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.operation')" align="left" width="90">
              <template #default="{ row, $index }">
                <span class="mr-4">
                  <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
                    <el-button type="primary" text @click.stop="openEditFormCollect(row, $index)">
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                </span>
                <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
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
import Sortable from 'sortablejs'
import { t } from '@/locales'
const props = defineProps<{ nodeModel: any }>()
const formNodeFormRef = ref<FormInstance>()
const tableRef = ref()
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
    MsgError(t('views.applicationWorkflow.tip.paramErrorMessage') + form_field_data.field)
    return
  }
  form_data.value.form_field_list = cloneDeep([...form_data.value.form_field_list, form_field_data])
  sync_form_field_list()
}
const sync_form_field_list = () => {
  const fields = [
    {
      label: t('views.applicationWorkflow.nodes.formNode.formAllContent'),
      value: 'form_data'
    },
    ...form_data.value.form_field_list.map((item: any) => ({
      value: item.field,
      label: typeof item.label == 'string' ? item.label : item.label.label
    }))
  ]
  set(props.nodeModel.properties.config, 'fields', fields)
  props.nodeModel.clear_next_node_field(false)
  onDragHandle()
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
  form_content_format: `${t('views.applicationWorkflow.nodes.formNode.form_content_format1')}
{{form}}
${t('views.applicationWorkflow.nodes.formNode.form_content_format2')}`,
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

// 表格排序拖拽
function onDragHandle() {
  if (!tableRef.value) return

  // 获取表格的 tbody DOM 元素
  const wrapper = tableRef.value.$el as HTMLElement
  const tbody = wrapper.querySelector('.el-table__body-wrapper tbody')
  if (!tbody) return
  // 初始化 Sortable
  Sortable.create(tbody as HTMLElement, {
    animation: 150,
    ghostClass: 'ghost-row',
    onEnd: (evt) => {
      if (evt.oldIndex === undefined || evt.newIndex === undefined) return
      // 更新数据顺序
      const items = [...form_data.value.form_field_list]
      const [movedItem] = items.splice(evt.oldIndex, 1)
      items.splice(evt.newIndex, 0, movedItem)
      form_data.value.form_field_list = items
      sync_form_field_list()
    }
  })
}
onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  sync_form_field_list()
  props.nodeModel.graphModel.eventCenter.emit('refresh_incoming_node_field')
})
</script>
<style lang="scss" scoped></style>
