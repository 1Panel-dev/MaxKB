<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="px-8 py-7 max-[680px]:px-3.5 max-[680px]:py-5">
    <div class="mb-[18px] flex items-center justify-between max-[680px]:flex-col max-[680px]:items-start max-[680px]:gap-4">
      <h1 class="text-lg">{{ route.meta.title }}</h1>
      <div v-if="route.name === 'system-users'" class="flex gap-3">
        <el-input placeholder="请输入" />
        <el-button type="primary">创建用户</el-button>
      </div>
    </div>
  </div>
</template>
