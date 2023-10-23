<template>
  <el-table v-bind="$attrs" :max-height="tableHeight">
    <el-table-column prop="name" label="数据集名称" />
    <el-table-column label="管理" align="center">
      <template #header>
        <el-checkbox v-model="allChecked" label="管理" />
      </template>
      <template #default="{ row }">
        <el-checkbox v-model="row.operate['MANAGE']" />
      </template>
    </el-table-column>
    <el-table-column label="使用" align="center">
      <template #header>
        <el-checkbox v-model="allChecked" label="使用" />
      </template>
      <template #default="{ row }">
        <el-checkbox v-model="row.operate['USE']" />
      </template>
    </el-table-column>
  </el-table>
</template>
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

// const emit = defineEmits(['refresh'])

const allChecked = ref(false)

const tableHeight = ref(0)

const loading = ref<boolean>(false)

onMounted(() => {
  tableHeight.value = window.innerHeight - 300
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 300
    })()
  }
})
</script>
<style lang="scss" scope></style>
