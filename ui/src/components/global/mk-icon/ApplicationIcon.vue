<script setup lang="ts">
import { resetUrl } from '@/utils/icon'

defineOptions({ name: 'ApplicationIcon' })

withDefaults(defineProps<{ icon?: string; size?: number | string }>(), { size: 24 })
</script>

<template>
  <el-avatar class="bg-transparent!" shape="square" :size="size">
    <img :src="resetUrl(icon, true)" alt="" />
  </el-avatar>
</template>
