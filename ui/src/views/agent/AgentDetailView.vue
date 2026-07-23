<script setup lang="ts">
import { isSystem, isWorkspace } from '@/router/admin/utils'
const route = useRoute()
</script>

<template>
  <div class="px-8 py-7">
    <h1 class="text-lg">智能体详情</h1>
    <!-- 根据 isSystem / isWorkspace 处理来源相关的权限、返回地址和操作。 -->
    <span v-if="isSystem(route.meta.scope) || isWorkspace(route.meta.scope)" class="hidden" />
  </div>
</template>
