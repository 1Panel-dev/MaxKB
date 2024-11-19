<template>
  <div class="radio_content" v-resize="resize" :style="radioContentStyle">
    <el-card
      v-for="item in option_list"
      :key="item.value"
      class="item"
      shadow="never"
      :class="[modelValue == item[valueField] ? 'active' : '']"
      @click="selected(item[valueField])"
    >
      {{ item[textField] }}
    </el-card>
  </div>
</template>
<script lang="ts" setup>
import { computed, ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
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

const selected = (activeValue: string | number) => {
  emit('update:modelValue', activeValue)
}
const emit = defineEmits(['update:modelValue'])
const width = ref<number>()
const radioContentStyle = computed(() => {
  if (width.value) {
    if (width.value < 350) {
      return { '--maxkb-radio-card-width': '316px' }
    } else if (width.value > 770) {
      return { '--maxkb-radio-card-width': '378px' }
    } else {
      return { '--maxkb-radio-card-width': '100%' }
    }
  }
  return {}
})
const resize = (wh: any) => {
  if (wh.height) {
    width.value = wh.width
  }
}
const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
</script>
<style lang="scss" scoped>
.radio_content {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  width: 100%;
  .active {
    border: 1px solid var(--el-color-primary);
  }
  .item {
    cursor: pointer;
    height: 38px;
    display: flex;
    justify-content: center;
    align-items: center;
    width: var(--maxkb-radio-card-width, 100%);
    margin: 4px;
  }
}
</style>
