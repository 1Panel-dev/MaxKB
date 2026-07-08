<template>
  <el-table
    :max-height="tableHeight"
    v-bind="$attrs"
    ref="appTableRef"
    :height="tableHeight + 'px'"
    v-el-table-infinite-scroll="load"
    :infinite-scroll-disabled="disabled"
  >
    <slot></slot>
  </el-table>
</template>
<script setup lang="ts">
import { ref, nextTick, watch, computed, onMounted } from 'vue'
import { default as vElTableInfiniteScroll } from 'el-table-infinite-scroll'
defineOptions({ name: 'AppTableInfiniteScroll' })

const props = defineProps({
  paginationConfig: {
    type: Object,
    required: true,
    default: () => ({
      current_page: 1,
      page_size: 50,
      total: 0,
    }),
  }, // option: { current_page , page_size, total  }
  maxTableHeight: {
    type: Number,
    default: 300,
  },
})
const emit = defineEmits(['changePage'])

const appTableRef = ref()

const tableHeight = ref<number | string>('')
const disabled = ref(false)

const load = () => {
  if (disabled.value) return

  // props.paginationConfig.current_page++;
  if (
    props.paginationConfig.current_page * props.paginationConfig.page_size <=
    props.paginationConfig.total
  ) {
    emit('changePage')
  }

  if (
    props.paginationConfig.current_page * props.paginationConfig.page_size ===
    props.paginationConfig.total
  ) {
    disabled.value = true
  }
}
defineExpose({})

onMounted(() => {
  tableHeight.value = window.innerHeight - props.maxTableHeight
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - props.maxTableHeight
    })()
  }
})
</script>

<style lang="scss" scoped></style>
