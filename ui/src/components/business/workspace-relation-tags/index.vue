<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'WorkspaceRelationTags' })

const props = defineProps<{
  tableRenderParams: Record<'property' | 'value', string>
  tags?: string[]
  tagWorkspace?: Record<string, string[]>
}>()

const tableData = computed(() => {
  return Object.entries(props.tagWorkspace ?? {}).map(([tagName, workspaces]) => ({
    property: tagName,
    value: workspaces[0] === 'None' ? '-' : workspaces.join(', '),
  }))
})
</script>

<template>
  <el-popover placement="bottom" trigger="hover" :width="420" :persistent="false">
    <template #reference>
      <MkTagGroup :tags="tags" popover-disabled class="cursor-pointer" />
    </template>
    <div class="p-6">
      <MkTable :data="tableData" max-height="300">
        <template v-for="(label, prop) in tableRenderParams" :key="prop">
          <el-table-column
            :label="label"
            :prop="prop"
            :show-overflow-tooltip="{ appendTo: 'body' }"
          />
        </template>
      </MkTable>
    </div>
  </el-popover>
</template>
