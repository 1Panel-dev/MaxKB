<template>
  <el-row :gutter="12">
    <el-col :span="12" v-for="data in data_list">
      <el-card shadow="hover" @click="emit('update:modelValue', data)">
        <slot v-bind="data"></slot>
      </el-card>
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
defineProps<{ modelValue?: any; data_list: Array<any> }>()
const emit = defineEmits(['update:modelValue'])
</script>
<style lang="scss" scoped></style>
