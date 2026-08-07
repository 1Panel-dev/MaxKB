<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  firstColumnLabel: string
  firstColumnProp: string
  secondColumnLabel: string
  secondColumnProp: string
  tagNames?: string[]
  tagWorkspace?: Record<string, string[]>
}

const props = defineProps<Props>()

// 将 {普通用户: ["小白跃升坊"]} 转换为表格可消费的动态字段行。
const tableData = computed(() => {
  if (!props.tagWorkspace) return []

  const result: Array<Record<string, string>> = []

  Object.entries(props.tagWorkspace).forEach(([tagName, workspaces]) => {
    workspaces.forEach((workspace) => {
      result.push({
        [props.firstColumnProp]: tagName,
        [props.secondColumnProp]: workspace,
      })
    })
  })

  return result
})
</script>

<template>
  <MkTagGroup :tags="tagNames" trigger-area="all" :popover-width="600">
    <template #popover>
      <el-table :data="tableData" max-height="320">
        <el-table-column :prop="firstColumnProp" :label="firstColumnLabel" min-width="180" />
        <el-table-column :prop="secondColumnProp" :label="secondColumnLabel" min-width="320" />
      </el-table>
    </template>
  </MkTagGroup>
</template>
