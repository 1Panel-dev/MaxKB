<template>
  <el-card
    shadow="hover"
    class="card-checkbox cursor"
    :class="modelValue.includes(toModelValue) ? 'active' : ''"
    @click="checked"
  >
    <div class="flex-between">
      <div class="flex align-center">
        <slot name="icon">
          <AppAvatar v-if="data.type === '1'" class="mr-8 avatar-purple" shape="square" :size="32">
            <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
          </AppAvatar>

          <AppAvatar v-else class="mr-12 avatar-blue" shape="square" :size="32">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
        </slot>
        <slot></slot>
      </div>
      <el-checkbox v-bind:modelValue="modelValue.includes(toModelValue)" @change="checkboxChange">
      </el-checkbox>
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { computed } from 'vue'
defineOptions({ name: 'CardCheckbox' })
const props = defineProps<{
  data: any

  modelValue: Array<any>

  valueField?: string
}>()

const toModelValue = computed(() => (props.valueField ? props.data[props.valueField] : props.data))

// const isChecked = computed({
//   get: () => props.modelValue.includes(toModelValue.value)),
//   set: (val) => val
// })

const emit = defineEmits(['update:modelValue', 'change'])

const checked = () => {
  const value = props.modelValue ? props.modelValue : []
  if (props.modelValue.includes(toModelValue.value)) {
    emit(
      'update:modelValue',
      value.filter((item) => item !== toModelValue.value)
    )
  } else {
    emit('update:modelValue', [...value, toModelValue.value])
  }
  checkboxChange()
}

function checkboxChange() {
  emit('change')
}
</script>
<style lang="scss" scoped>
.card-checkbox {
  &.active {
    border: 1px solid var(--el-color-primary);
  }
  input.checkbox[type='checkbox'] {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    height: 14px;
    width: 14px;
    position: relative;

    &::after {
      position: absolute;
      top: 0;
      background-color: white;
      color: #000;
      height: 13px;
      width: 13px;
      visibility: visible;
      text-align: center;
      box-sizing: border-box;
      border: var(--el-border);
      border-radius: var(--el-border-radius-small);
      box-sizing: content-box;
      content: '';
    }

    &:checked::after {
      content: '✓';
      color: #ffffff;
      border-color: var(--el-color-primary);
      background: var(--el-color-primary);
    }
  }
}
</style>
