<script setup lang="ts">
import type { ChatFeedback } from '@/api/types'

defineProps<{
  currentStatus: ChatFeedback['vote_status']
  submitting: boolean
}>()
const emit = defineEmits<{ select: [status: '0' | '1'] }>()
</script>

<template>
  <div class="flex-align-center gap-1">
    <!-- 打开满意反馈，再次点击已评价按钮可撤销 -->
    <MkTooltip v-if="currentStatus === '-1' || currentStatus === '0'" :content="currentStatus === '0' ? '取消赞同' : '赞同'">
      <el-button text :disabled="submitting" @click="emit('select', '0')">
        <MkIcon v-if="currentStatus === '0'" name="icon_thumbsup_filled" class="text-[#FFC60A]!" />
        <MkIcon v-else name="icon_thumbsup_outlined" />
      </el-button>
    </MkTooltip>
    <!-- 打开不满意反馈，再次点击已评价按钮可撤销 -->
    <MkTooltip v-if="currentStatus === '-1' || currentStatus === '1'" :content="currentStatus === '1' ? '取消反对' : '反对'">
      <el-button text :disabled="submitting" @click="emit('select', '1')">
        <MkIcon v-if="currentStatus === '1'" name="icon_thumbdown_filled" class="text-danger!" />
        <MkIcon v-else name="icon_thumbdown_outlined" />
      </el-button>
    </MkTooltip>
  </div>
</template>
