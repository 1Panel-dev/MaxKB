<template>
  <div class="table-radio">
    <div class="header">
      <div class="title">{{ title }}</div>

      <el-input
        v-model="filterText"
        :validate-event="false"
        placeholder="请输入关键字搜索"
        class="input-with-select"
        style="--el-color-danger: #c0c4cc"
        clearable
      >
        <template #prepend>
          <el-button :icon="Search" />
        </template>
      </el-input>
    </div>

    <el-table
      ref="singleTableRef"
      :data="tableData"
      highlight-current-row
      style="width: 100%; height: 100%; --el-bg-color: #f5f6f7"
      @current-change="_data = $event[valueField]"
    >
      <el-table-column width="50px">
        <template #default="scope">
          <input type="radio" :checked="_data === scope.row[valueField]" />
        </template>
      </el-table-column>
      <el-table-column
        v-for="(column, index) in tableColumns"
        v-bind="column"
        :label="column.label"
        :key="index"
      >
        <template #default="scope">
          <template v-if="column.type === 'component'">
            <TableColumn :column="column" :row="scope.row"></TableColumn>
          </template>
          <template v-else-if="column.type === 'eval'">
            <span v-html="evalF(column.property, scope.row)"></span
          ></template>
          <template v-else>
            <span>{{ scope.row[column.property] }}</span></template
          >
        </template>
      </el-table-column>
    </el-table>
    <div class="msg" v-show="props.modelValue">
      {{ activeMsg }}
      <span class="active">
        {{ activeText }}
      </span>
    </div>
  </div>
</template>
<script setup lang="ts">
import type { FormField } from '@/components/dynamics-form/type'
import { computed, ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { ElTable } from 'element-plus'

import _ from 'lodash'
import TableColumn from '@/components/dynamics-form/items/table/TableColumn.vue'
const filterText = ref<string>('')
const props = defineProps<{
  formValue?: any
  formfieldList?: Array<FormField>
  field: string
  otherParams: any
  formField: FormField
  view?: boolean
  // 选中的值
  modelValue?: any
}>()
const rowTemp = ref<any>()
const evalF = (text: string, row: any) => {
  rowTemp.value = row
  return eval(text)
}
const emit = defineEmits(['update:modelValue', 'change'])

const singleTableRef = ref<InstanceType<typeof ElTable>>()

const _data = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
    emit('change', props.formField)
  }
})

const propsInfo = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})

const activeMsg = computed(() => {
  return propsInfo.value.active_msg ? propsInfo.value.active_msg : ''
})
const title = computed(() => {
  return propsInfo.value.title ? propsInfo.value.title : ''
})
const tableColumns = computed(() => {
  return propsInfo.value.table_columns ? propsInfo.value.table_columns : []
})

const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const tableData = computed(() => {
  if (option_list.value) {
    if (filterText.value) {
      return option_list.value.filter((item: any) =>
        tableColumns.value.some((c: any) => {
          let v = ''
          if (c.type === 'eval') {
            v = evalF(c.property, item)
          } else if (c.type === 'component') {
            return false
          } else {
            v = item[c.property]
          }
          return typeof v == 'string' ? v.indexOf(filterText.value) >= 0 : false
        })
      )
    } else {
      return option_list.value.filter((item: any) => item[valueField.value])
    }
  }
  return []
})

/**
 * 监听表格数据，设置默认值
 */
watch(
  () => tableData.value,
  () => {
    if (tableData.value && tableData.value.length > 0) {
      const defaultItem = _.head(tableData.value)
      let defaultItemValue = _.get(defaultItem, valueField.value)
      if (props.modelValue) {
        const row = option_list.value.find((f: any) => f[valueField.value] === props.modelValue)
        if (row) {
          defaultItemValue = row[valueField.value]
        }
      }
      emit('update:modelValue', defaultItemValue)
    } else {
      emit('update:modelValue', undefined)
    }
    emit('change', props.formField)
  }
)

const activeText = computed(() => {
  if (props.modelValue) {
    const row = option_list.value.find((f: any) => f[valueField.value] === props.modelValue)
    return row[textField.value]
  }
  return props.modelValue
})
</script>
<style lang="scss" scoped>
.table-radio {
  .header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 16px;
    .title {
      color: #1f2329;
      font-weight: 400;
      font-size: 14px;
      line-height: 22px;
    }
    .input-with-select {
      width: 45%;
    }
  }
  .msg {
    margin-top: 12px;
    color: rgba(100, 106, 115, 1);
    .active {
      margin-left: 3px;
      color: var(--el-color-primary);
    }
  }
}
</style>
