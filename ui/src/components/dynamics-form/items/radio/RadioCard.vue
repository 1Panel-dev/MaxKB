<template>
  <div class="radio-card" :style="radioContentStyle">
    <el-row :gutter="12" class="w-full">
      <template v-for="(item, index) in option_list" :key="index">
        <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12">
          <el-card
            :key="item.value"
            class="item break-all"
            shadow="never"
            style="--el-card-padding: 12px 16px"
            :class="[
              inputDisabled ? 'is-disabled' : '',
              modelValue == item[valueField] ? 'active' : '',
            ]"
            @click="inputDisabled ? () => {} : selected(item[valueField])"
            :innerHTML="item[textField] ? item[textField] : '\u200D'"
          >
          </el-card>
        </el-col>
      </template>
    </el-row>
  </div>
</template>
<script lang="ts" setup>
import { computed, ref, inject } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import { useFormDisabled, formItemContextKey } from 'element-plus'

const inputDisabled = useFormDisabled()

const props = defineProps<{
  formValue?: any
  formfieldList?: Array<FormField>
  field: string
  otherParams: any
  formField: FormField
  view?: boolean
  // 选中的值
  modelValue?: any
  disabled?: boolean
}>()
const elFormItem = inject(formItemContextKey, void 0)
const selected = (activeValue: string | number) => {
  emit('update:modelValue', activeValue)
  if (elFormItem?.validate) {
    elFormItem.validate('change')
  }
}
const emit = defineEmits(['update:modelValue', 'change'])
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
.radio-card {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  width: 100%;

  .is-disabled {
    border: 1px solid var(--el-card-border-color);
    background-color: var(--el-fill-color-light);
    color: var(--el-text-color-placeholder);
    cursor: not-allowed;
    &:hover {
      cursor: not-allowed;
    }
  }
  .active {
    border: 1px solid var(--el-color-primary);
    color: var(--el-color-primary);
  }
  .item {
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    width: var(--maxkb-radio-card-width, 100%);
    margin: 4px;
  }
}
</style>
