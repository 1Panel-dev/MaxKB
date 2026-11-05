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
  <!-- 单一结构：slot 层级固定，进出分享模式只切换样式与勾选框，消息内容组件不重建，展开状态得以保留 -->
  <div :class="{ 'flex items-center gap-3': active && shareLink }">
    <!-- 选择当前问答轮次 -->
    <el-checkbox
      v-if="active && shareLink"
      :model-value="shareLink.isSelected(recordId)"
      :disabled="shareLink.isDisabled(recordId)"
      class="mt-3 shrink-0"
      @change="shareLink.toggle(recordId)"
    />
    <!-- 分享模式下点击消息区域切换整轮选择 -->
    <div
      class="min-w-0 flex-1"
      :class="
        active && shareLink
          ? [
              'rounded-xl p-3',
              shareLink.isDisabled(recordId) ? 'cursor-default' : 'cursor-pointer hover:bg-N900/8',
              { 'bg-N900/8': shareLink.isSelected(recordId) },
            ]
          : ''
      "
      @click="active && shareLink?.toggle(recordId)"
    >
      <div :class="{ 'pointer-events-none select-none': active && shareLink }">
        <slot />
      </div>
    </div>
  </div>
</template>
