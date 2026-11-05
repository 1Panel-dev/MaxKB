<script setup lang="ts">
import { provide, toRef } from 'vue'
import { SHARE_RECORD_ID_KEY, useShareLinkStoreOptional } from './index'

defineOptions({ name: 'ShareMessageRow' })

const props = defineProps<{
  active: boolean
  recordId?: string
}>()
const shareLink = useShareLinkStoreOptional()
// 消息内容内的分享入口据此预先勾选所属轮次
provide(SHARE_RECORD_ID_KEY, toRef(props, 'recordId'))
</script>

<template>
  <div v-if="active && shareLink" class="flex items-center gap-3">
    <!-- 选择当前问答轮次 -->
    <el-checkbox
      :model-value="shareLink.isSelected(recordId)"
      :disabled="shareLink.isDisabled(recordId)"
      class="mt-3 shrink-0"
      @change="shareLink.toggle(recordId)"
    />
    <!-- 分享模式下点击消息区域切换整轮选择 -->
    <div
      class="min-w-0 flex-1 rounded-xl p-3"
      :class="[shareLink.isDisabled(recordId) ? 'cursor-default' : 'cursor-pointer hover:bg-N900/8', { 'bg-N900/8': shareLink.isSelected(recordId) }]"
      @click="shareLink.toggle(recordId)"
    >
      <div class="pointer-events-none select-none">
        <slot />
      </div>
    </div>
  </div>
  <div v-else>
    <slot />
  </div>
</template>
