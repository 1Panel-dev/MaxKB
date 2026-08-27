<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { computed, ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { TableInstance } from 'element-plus'

import _ from 'lodash'
import TableColumn from '@/components/mk-dynamics-form/items/table/TableColumn.vue'
const filterText = ref<string>('')
const props = defineProps<{
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  field: string
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
  // 选中的值
  modelValue?: DynamicFormValue
}>()
const evalF = (text: string, row: DynamicFormValue) => {
  return new Function('row', `"use strict"; return (${text})`)(row)
}
const emit = defineEmits(['update:modelValue', 'change'])

const singleTableRef = ref<TableInstance>()

const localValue = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
    emit('change', props.formField)
  },
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

const options = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const tableData = computed(() => {
  if (options.value) {
    if (filterText.value) {
      return options.value.filter((item: DynamicFormValue) =>
        tableColumns.value.some((c: DynamicFormValue) => {
          let v = ''
          if (c.type === 'eval') {
            v = evalF(c.property, item)
          } else if (c.type === 'component') {
            return false
          } else {
            v = item[c.property]
          }
          return typeof v === 'string' ? v.indexOf(filterText.value) >= 0 : false
        }),
      )
    } else {
      return options.value.filter((item: DynamicFormValue) => item[valueField.value])
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
        const row = options.value.find(
          (f: DynamicFormValue) => f[valueField.value] === props.modelValue,
        )
        if (row) {
          defaultItemValue = row[valueField.value]
        }
      }
      emit('update:modelValue', defaultItemValue)
    } else {
      emit('update:modelValue', undefined)
    }
    emit('change', props.formField)
  },
)

const activeText = computed(() => {
  if (props.modelValue) {
    const row = options.value.find(
      (f: DynamicFormValue) => f[valueField.value] === props.modelValue,
    )
    return row?.[textField.value]
  }
  return props.modelValue
})
</script>

<template>
  <div class="table-radio">
    <div class="header">
      <div class="title">{{ title }}</div>

      <el-input
        v-model="filterText"
        :validate-event="false"
        placeholder="请输入关键词搜索"
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
      @current-change="localValue = $event[valueField]"
    >
      <el-table-column width="50px">
        <template #default="scope">
          <input type="radio" :checked="localValue === scope.row[valueField]" />
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
<style lang="scss" scoped>
.table-radio {
  .header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 16px;
    .title {
      color: var(--el-text-color-primary);
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
