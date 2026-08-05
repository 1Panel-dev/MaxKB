<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  void router.replace({ name: 'workspace-home', params: { workspaceId: 'default' } })
}
</script>

<template>
  <main class="flex-center min-h-screen">
    <el-result icon="warning" title="404" sub-title="页面不存在或已被删除">
      <template #extra>
        <el-button type="primary" @click="goHome">返回首页</el-button>
      </template>
    </el-result>
  </main>
</template>
