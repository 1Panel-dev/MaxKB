<script setup lang="ts">
import { computed, inject } from 'vue'
import { SHARE_PANEL_KEY } from '../../../main/share-panel/index'

defineOptions({ name: 'ShareMessageRow' })

const props = defineProps<{
  active: boolean
  recordId?: string
}>()
const selectedRecordIds = defineModel<string[]>({ required: true })
const sharePanel = inject(SHARE_PANEL_KEY, null)
const selected = computed(() => Boolean(props.recordId && selectedRecordIds.value.includes(props.recordId)))
const disabled = computed(() => !props.recordId || Boolean(sharePanel?.sharing.value))

// 提问和回答使用同一记录 ID，同步切换整轮选择。
const toggleRecord = () => {
  if (!props.active || disabled.value || !props.recordId) return
  selectedRecordIds.value = selected.value
    ? selectedRecordIds.value.filter((recordId) => recordId !== props.recordId)
    : [...selectedRecordIds.value, props.recordId]
}
</script>

<template>
  <div :class="{ 'flex items-center gap-3': active }">
    <!-- 选择当前问答轮次 -->
    <el-checkbox v-if="active" :model-value="selected" :disabled="disabled" class="mt-3 shrink-0" @change="toggleRecord()" />
    <!-- 分享模式下点击消息区域切换选择 -->
    <div
      class="min-w-0 flex-1"
      :class="active ? ['rounded-xl p-3', disabled ? 'cursor-default' : 'cursor-pointer hover:bg-N900/8', { 'bg-N900/8': selected }] : ''"
      @click="toggleRecord()"
    >
      <div :class="{ 'pointer-events-none select-none': active }">
        <slot />
      </div>
    </div>
  </div>
</template>
