<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('workflow.nodeSetting') }}</h5>
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
          :label="$t('workflow.nodes.formNode.formContent.label')"
          prop="form_content_format"
          :rules="{
            required: true,
            message: $t('workflow.nodes.formNode.formContent.requiredMessage'),
            trigger: 'blur',
          }"
        >
          <template #label>
            <div class="flex align-center">
              <div class="mr-4">
                <span
                  >{{ $t('workflow.nodes.formNode.formContent.label')
                  }}<span class="color-danger">*</span></span
                >
              </div>
              <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
                <template #content>
                  {{
                    $t('workflow.nodes.formNode.formContent.tooltip', {
                      form: '{ form }',
                    })
                  }}
                </template>
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
          </template>
          <MdEditorMagnify
            :title="$t('workflow.nodes.formNode.formContent.label')"
            v-model="form_data.form_content_format"
            style="height: 150px"
            @submitDialog="submitDialog"
          />
        </el-form-item>
        <el-form-item :label="$t('workflow.nodes.formNode.formSetting')" @click.prevent>
          <template #label>
            <div class="flex-between">
              <h5 class="lighter">
                {{ $t('workflow.nodes.formNode.formSetting') }}
              </h5>
              <el-button link type="primary" @click="openAddFormCollect()">
                <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
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
                <el-tag size="small" type="info" class="info-tag">{{
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
            <el-table-column :label="$t('common.required')" width="55">
              <template #default="{ row }">
                <div @click.stop>
                  <el-switch disabled size="small" v-model="row.required" />
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.operation')" align="left" width="80">
              <template #default="{ row, $index }">
                <span class="mr-4">
                  <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
                    <el-button type="primary" text @click.stop="openEditFormCollect(row, $index)">
                      <AppIcon iconName="app-edit"></AppIcon>
                    </el-button>
                  </el-tooltip>
                </span>
                <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                  <el-button type="primary" text @click="deleteField(row)">
                    <AppIcon iconName="app-delete"></AppIcon>
                  </el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
    </el-card>
    <AddFormCollect
      ref="addFormCollectRef"
      :addFormField="addFormField"
      :nodeModel="nodeModel"
      :currentNodeFields="form_data.form_field_list"
      :enableVisibility="enableVisibility"
    ></AddFormCollect>
    <EditFormCollect
      ref="editFormCollectRef"
      :editFormField="editFormField"
      :nodeModel="nodeModel"
      :currentNodeFields="form_data.form_field_list"
      :enableVisibility="enableVisibility"
    />
  </NodeContainer>
</template>
<script setup lang="ts">
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import AddFormCollect from '@/workflow/common/AddFormCollect.vue'
import EditFormCollect from '@/workflow/common/EditFormCollect.vue'
import { type FormInstance } from 'element-plus'
import { ref, onMounted, computed, provide, inject } from 'vue'
import { input_type_list } from '@/components/dynamics-form/constructor/data'
import { WorkflowMode } from '@/enums/application'
import { MsgError } from '@/utils/message'
import { set, cloneDeep } from 'lodash'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import Sortable from 'sortablejs'
import { t } from '@/locales'
const props = defineProps<{ nodeModel: any }>()
provide('getModel', () => props.nodeModel)
const workflowMode = inject('workflowMode', WorkflowMode.Application) as WorkflowMode
const enableVisibility = computed(
  () => workflowMode === WorkflowMode.Application || workflowMode === WorkflowMode.ApplicationLoop,
)
const getResourceDetail = inject('getResourceDetail') as any
const route = useRoute()
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const resource = getResourceDetail()

provide('getSelectModelList', (params: any) => {
  const obj =
    apiType.value === 'systemManage'
      ? { ...params, workspace_id: resource.value?.workspace_id }
      : { ...params }
  return loadSharedApi({ type: 'model', systemType: apiType.value }).getSelectModelList(obj)
})

provide('getModelParamsForm', (model_id: string) => {
  return loadSharedApi({ type: 'model', systemType: apiType.value }).getModelParamsForm(model_id)
})
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
    MsgError(t('workflow.tip.paramErrorMessage') + form_field_data.field)
    return
  }
  form_data.value.form_field_list = cloneDeep([...form_data.value.form_field_list, form_field_data])
  sync_form_field_list()
}
const sync_form_field_list = () => {
  const fields = [
    {
      label: t('workflow.nodes.formNode.formAllContent'),
      value: 'form_data',
    },
    ...form_data.value.form_field_list.map((item: any) => ({
      value: item.field,
      label: typeof item.label == 'string' ? item.label : item.label.label,
    })),
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
    (field: any) => field.field !== form_field_data.field,
  )
  sync_form_field_list()
}
const form = ref<any>({
  is_result: true,
  form_content_format: `${t('workflow.nodes.formNode.form_content_format1')}
{{form}}
${t('workflow.nodes.formNode.form_content_format2')}`,
  form_field_list: [],
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
  },
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
  const v_list = [formNodeFormRef.value?.validate()]

  const upstreamNodes = props.nodeModel.get_up_node_field_list(true, true)
  if (props.nodeModel.graphModel.get_up_node_field_list) {
    const outer = props.nodeModel.graphModel.get_up_node_field_list(true, true)
    outer.forEach((item: any) => upstreamNodes.push(item))
  }

  for (const field of form_data.value.form_field_list) {
    for (const cond of field.visibility_rules?.conditions || []) {
      if (!cond.field || cond.field.length < 2 || !cond.field[0] || !cond.field[1]) continue
      if (cond.field[0] === props.nodeModel.id) {
        // 同节点：查 form_field_list
        if (!form_data.value.form_field_list.some((f: any) => f.field === cond.field[1])) {
          v_list.push(Promise.reject(t('workflow.variable.NoReferencing')))
        }
      } else {
        // 跨节点：查上游（含循环外层 graph 的节点）
        const nodeEntry = upstreamNodes.find((n: any) => n.value === cond.field[0])
        if (!nodeEntry || !nodeEntry.children?.some((c: any) => c.value === cond.field[1])) {
          v_list.push(Promise.reject(t('workflow.variable.NoReferencing')))
        }
      }
    }
  }

  return Promise.all(v_list).catch((err) =>
    Promise.reject({ node: props.nodeModel, errMessage: err }),
  )
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
      const items = cloneDeep([...form_data.value.form_field_list])
      const [movedItem] = items.splice(evt.oldIndex, 1)
      items.splice(evt.newIndex, 0, movedItem)
      form_data.value.form_field_list = items
      sync_form_field_list()
    },
  })
}
onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  sync_form_field_list()
  props.nodeModel.graphModel.eventCenter.emit('refresh_incoming_node_field')
})
</script>
<style lang="scss" scoped></style>
