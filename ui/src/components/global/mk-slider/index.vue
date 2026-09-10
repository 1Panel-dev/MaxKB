<script setup lang="ts">
import { computed } from 'vue'
import { sliderEmits, sliderProps } from 'element-plus'

defineOptions({ name: 'MkSlider' })

/* input-number 的controls始终是true，el-slider上的show-input-controls不需要*/
const props = defineProps({
  ...sliderProps,
  showInput: { type: Boolean, default: true },
})
const emit = defineEmits(sliderEmits)

// 区间和标记步长模式沿用原生滑块，不显示单值输入框。
const showNumberInput = computed(() => props.showInput && !props.range && props.step !== 'mark')

function updateInputValue(value: number | undefined) {
  if (value === undefined) return
  emit('update:modelValue', value)
  emit('input', value)
}

function changeInputValue(value: number | undefined) {
  if (value !== undefined) emit('change', value)
}
</script>

<template>
  <div class="flex w-full items-center gap-4" :class="{ 'flex-col': props.vertical }">
    <el-slider
      v-bind="props"
      :show-input="false"
      :class="{ 'min-w-0 flex-1': !props.vertical }"
      @update:model-value="emit('update:modelValue', $event)"
      @input="emit('input', $event)"
      @change="emit('change', $event)"
    />
    <el-input-number
      v-if="showNumberInput"
      :model-value="typeof props.modelValue === 'number' ? props.modelValue : props.min"
      :min="props.min"
      :max="props.max"
      :step="typeof props.step === 'number' ? props.step : 1"
      :disabled="props.disabled"
      :size="props.inputSize || props.size"
      :controls="true"
      :validate-event="false"
      value-on-clear="min"
      controls-position="right"
      align="left"
      class="w-30! shrink-0"
      @update:model-value="updateInputValue"
      @change="changeInputValue"
    />
  </div>
</template>
