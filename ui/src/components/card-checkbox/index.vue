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
          <KnowledgeIcon :type="data.type" />
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

const emit = defineEmits(['update:modelValue', 'change'])

const checked = () => {
  const value = props.modelValue ? props.modelValue : []
  if (props.modelValue.includes(toModelValue.value)) {
    emit(
      'update:modelValue',
      value.filter((item) => item !== toModelValue.value),
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
<style lang="scss"></style>
