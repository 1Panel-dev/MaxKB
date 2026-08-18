<script setup lang="ts">
import { isSystem, isWorkspace } from '@/router/admin/utils'

const route = useRoute()
const router = useRouter()

const agentWorkflowHref = computed(
  () =>
    router.resolve({
      name: 'workflow-agent',
      params: { agentId: route.params.agentId },
    }).href,
)
</script>

<template>
  <div class="px-8 py-7">
    <div class="flex items-center justify-between">
      <h1 class="text-lg">智能体详情</h1>
      <el-button
        tag="a"
        type="primary"
        :href="agentWorkflowHref"
        target="_blank"
        rel="noopener noreferrer"
      >
        编排工作流
      </el-button>
    </div>
    <!-- 根据 isSystem / isWorkspace 处理来源相关的权限、返回地址和操作。 -->
    <span v-if="isSystem(route.meta.scope) || isWorkspace(route.meta.scope)" class="hidden" />
  </div>
</template>
