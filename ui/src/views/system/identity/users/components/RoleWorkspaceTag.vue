<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  roleNames?: string[]
  roleWorkspace?: Record<string, string[]>
}

const props = defineProps<Props>()

// 将 {普通用户: ["小白跃升坊"]} 转换为 [{roleName: "普通用户", workspace: "小白跃升坊"}]
const tableData = computed(() => {
  if (!props.roleWorkspace) return []

  const result: Array<{ roleName: string; workspace: string }> = []

  Object.entries(props.roleWorkspace).forEach(([roleName, workspaces]) => {
    workspaces.forEach((workspace) => {
      result.push({ roleName, workspace })
    })
  })

  return result
})
</script>

<template>
  <div v-if="roleNames?.length" class="flex items-center gap-1">
    <el-popover v-if="roleNames.length > 1" placement="bottom-start" trigger="hover" :width="600">
      <template #reference>
        <span class="inline-flex items-center gap-1">
          <el-tag type="info">{{ roleNames[0] }}</el-tag>
          <el-tag type="info">+{{ roleNames.length - 1 }}</el-tag>
        </span>
      </template>
      <el-table :data="tableData" max-height="320">
        <el-table-column prop="roleName" label="角色" min-width="180" />
        <el-table-column prop="workspace" label="工作空间" min-width="320" />
      </el-table>
    </el-popover>
    <el-tag v-else type="info">{{ roleNames[0] }}</el-tag>
  </div>
  <span v-else>-</span>
</template>
