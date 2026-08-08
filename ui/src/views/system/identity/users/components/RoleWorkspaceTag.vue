<script setup lang="ts">
import { computed } from 'vue'
/**
 * 标签与工作空间的关联关系映射
 * 键为标签名称，值为该标签关联的工作空间名称数组。
 * 「键 + 单个工作空间」展开为一行：键落在第一列，工作空间落在第二列，
 * 两列的标题分别取自 tableRenderParams.property 和 tableRenderParams.value。
 * @example
 * {
 *   '管理员': ['默认工作空间', '管理员工作空间'],
 *   '普通用户': ['默认工作空间']
 * }
 * 配合 { property: '角色', value: '工作空间' } 渲染为：
 *    角色     | 工作空间
 *    管理员   | 默认工作空间,管理员工作空间
 *    普通用户 | 默认工作空间
 */
const props = defineProps<{
  /**
   * 悬浮表格数据由 tagWorkspace 展开而来：
   * tagWorkspace 的「键」渲染为第一列，「值」渲染为第二列。
   * 所以这里的 property 是第一列（标签名）的标题，value 是第二列（工作空间）的标题，两者不可调换。
   *
   * @property {string} property - 第一列的列标题，对应 tagWorkspace 的键（如"角色"、"用户组"）
   * @property {string} value - 第二列的列标题，对应 tagWorkspace 的值（如"工作空间"）
   * @example { property: '角色', value: '工作空间' }
   */
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
      <MkTagGroup :tags="tags" :popoverDisabled="true" class="cursor-pointer"></MkTagGroup>
    </template>
    <div class="px-3 py-2">
      <MkTable :data="tableData" max-height="300">
        <template v-for="(label, prop) in tableRenderParams" :key="prop">
          <el-table-column
            :prop="prop"
            :label="label"
            :show-overflow-tooltip="{
              appendTo: 'body',
            }"
          />
        </template>
      </MkTable>
    </div>
  </el-popover>
</template>
