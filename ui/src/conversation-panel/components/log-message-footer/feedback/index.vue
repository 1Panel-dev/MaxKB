<script setup lang="ts">
import type { ChatFeedback } from '@/api/types'

defineOptions({ name: 'LogMessageFeedback' })
defineProps<{ status?: ChatFeedback['vote_status'] }>()
</script>

<template>
  <span v-if="status === '0'">
    <!-- 只读展示满意反馈 -->
    <el-button text disabled>
      <MkIcon name="icon_thumbsup_filled" class="text-[#FFC60A]!" />
    </el-button>
  </span>
  <span v-if="status === '1'">
    <!-- 只读展示不满意反馈 -->
    <el-button text disabled>
      <MkIcon name="icon_thumbdown_filled" class="text-danger!" />
    </el-button>
  </span>
</template>
