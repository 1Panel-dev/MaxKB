<script setup lang="ts">
defineOptions({ name: 'MkCardCheckbox' })

const props = defineProps<{ disabled?: boolean; label: string }>()
const checked = defineModel<boolean>({ default: false })
const emit = defineEmits<{ change: [checked: boolean] }>()
defineSlots<{ default(): unknown }>()

// 卡片与复选框共用选择入口，避免一次点击切换两次。
function toggle() {
  if (props.disabled) return
  const nextChecked = !checked.value
  checked.value = nextChecked
  emit('change', nextChecked)
}
</script>

<template>
  <el-card
    class="min-w-0"
    :class="{ 'border-primary!': checked, 'cursor-pointer': !props.disabled }"
    :shadow="props.disabled ? 'never' : 'hover'"
    @click="toggle"
  >
    <div class="flex-between gap-3">
      <div class="min-w-0 flex-1">
        <slot />
      </div>
      <el-checkbox :model-value="checked" :disabled="props.disabled" :aria-label="props.label" class="shrink-0" @click.stop @change="toggle" />
    </div>
  </el-card>
</template>
