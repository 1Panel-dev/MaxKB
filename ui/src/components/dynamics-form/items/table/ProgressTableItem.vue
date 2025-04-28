<template>
  <div class="progress-table-item">
    <el-popover placement="top-start" :title="row[text_field]" :width="200" trigger="hover">
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
<script setup lang="ts">
import { computed, ref } from 'vue'
const props = defineProps<{
  /**
   *表单渲染Item column
   */
  column: any
  /**
   * 这一行数据
   */
  row: any
}>()
const rowRef = ref<any>()

function evalF(text: string, row: any) {
  rowRef.value = row
  return eval(text)
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

const value_html = (view_card_item: any) => {
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
<style lang="scss" scoped>
@mixin valueScss() {
  color: rgba(31, 35, 41, 1);
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
