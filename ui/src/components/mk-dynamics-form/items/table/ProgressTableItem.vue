<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed } from 'vue'
const props = defineProps<{
  /**
   *表单渲染Item column
   */
  column: DynamicFormValue
  /**
   * 这一行数据
   */
  row: DynamicFormValue
}>()
function evalF(text: string, row: DynamicFormValue) {
  return new Function('row', `"use strict"; return (${text})`)(row)
}
const fieldProps = computed(() => {
  return props.column.props_info ? props.column.props_info : {}
})
const textField = computed(() => {
  return props.column.text_field ? props.column.text_field : 'key'
})
const valueField = computed(() => {
  return props.column.value_field ? props.column.value_field : 'value'
})

const getCardValue = (viewCardItem: DynamicFormValue) => {
  if (viewCardItem.type === 'eval') {
    return evalF(viewCardItem.value_field, props.row)
  } else {
    return props.row[viewCardItem.value_field]
  }
}

const viewCards = computed(() => {
  return fieldProps.value.view_card ? fieldProps.value.view_card : []
})
</script>

<template>
  <div class="progress-table-item">
    <el-popover
      placement="top-start"
      :title="row[textField]"
      :width="200"
      trigger="hover"
      :persistent="false"
    >
      <template #reference>
        <el-progress v-bind="$attrs" :percentage="row[valueField]"></el-progress
      ></template>
      <div>
        <el-row v-for="(item, index) in viewCards" :key="index">
          <el-col :span="6">{{ item.title }}</el-col>
          <el-col :span="18"> <span class="value" :innerHTML="getCardValue(item)"> </span></el-col>
        </el-row>
      </div>
    </el-popover>
  </div>
</template>
<style lang="scss" scoped>
@mixin valueScss() {
  color: var(--el-text-color-primary);
  font-weight: 500;
  font-size: 12px;
  line-height: 22px;
  height: 22px;
}
.progress-table-item {
  .value {
    float: right;
    @include valueScss;
  }
}
</style>
