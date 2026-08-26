<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import { computed } from 'vue'
const props = defineProps<{
  /**
   *表单渲染Item column
   */
  column: MkDynamicFormValue
  /**
   * 这一行数据
   */
  row: MkDynamicFormValue
}>()
function evalF(text: string, row: MkDynamicFormValue) {
  return new Function('row', `"use strict"; return (${text})`)(row)
}
const props_info = computed(() => {
  return props.column.props_info ? props.column.props_info : {}
})
const text_field = computed(() => {
  return props.column.text_field ? props.column.text_field : 'key'
})
const value_field = computed(() => {
  return props.column.value_field ? props.column.value_field : 'value'
})

const value_html = (view_card_item: MkDynamicFormValue) => {
  if (view_card_item.type === 'eval') {
    return evalF(view_card_item.value_field, props.row)
  } else {
    return props.row[view_card_item.value_field]
  }
}

const view_card = computed(() => {
  return props_info.value.view_card ? props_info.value.view_card : []
})
</script>

<template>
  <div class="progress-table-item">
    <el-popover
      placement="top-start"
      :title="row[text_field]"
      :width="200"
      trigger="hover"
      :persistent="false"
    >
      <template #reference>
        <el-progress v-bind="$attrs" :percentage="row[value_field]"></el-progress
      ></template>
      <div>
        <el-row v-for="(item, index) in view_card" :key="index">
          <el-col :span="6">{{ item.title }}</el-col>
          <el-col :span="18"> <span class="value" :innerHTML="value_html(item)"> </span></el-col>
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
