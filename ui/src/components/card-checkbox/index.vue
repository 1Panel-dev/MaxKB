<template>
  <el-row :gutter="12">
    <el-col :span="12" v-for="data in dataList" class="mb-16">
      <el-card
        shadow="hover"
        class="card"
        :class="modelValue.includes(toModelValue(data)) ? 'active' : ''"
        @click="checked(data)"
      >
        <slot v-bind="{ ...data, checked: modelValue.includes(toModelValue(data)) }"></slot>
      </el-card>
    </el-col>
  </el-row>
</template>
<script setup lang="ts">
const props = defineProps<{
  dataList: Array<any>

  modelValue: Array<any>

  valueField?: string
}>()

const toModelValue = (data: any) => {
  return props.valueField ? data[props.valueField] : data
}

const emit = defineEmits(['update:modelValue'])

const checked = (data: any) => {
  const value = props.modelValue ? props.modelValue : []
  if (value.includes(toModelValue(data))) {
    emit(
      'update:modelValue',
      value.filter((item) => item !== toModelValue(data))
    )
  } else {
    emit('update:modelValue', [...value, toModelValue(data)])
  }
}
</script>
<style lang="scss" scoped>
.active {
  --el-card-border-color: rgba(51, 112, 255, 1);
}
.card {
  &:hover {
    cursor: pointer;
  }
}
</style>
