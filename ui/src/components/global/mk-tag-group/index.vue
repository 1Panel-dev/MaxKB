<script setup lang="ts">
import type { TagProps } from 'element-plus'

defineOptions({ name: 'MkTagGroup' })

withDefaults(
  defineProps<{
    /** 是否禁用标签组浮层 */
    popoverDisabled?: boolean
    /** 浮层宽度 */
    popoverWidth?: number | string
    /** 标签尺寸 */
    size?: TagProps['size']
    /** 标签文字 */
    tags?: string[]
    /** 浮层触发区域：仅数量标签或整个标签组 */
    triggerArea?: 'all' | 'overflow'
  }>(),
  {
    popoverDisabled: false,
    popoverWidth: 300,
    size: 'default',
    tags: () => [],
    triggerArea: 'overflow',
  },
)

defineSlots<{
  /** 自定义浮层内容；默认展示第一个标签之外的所有标签 */
  popover?(props: { overflowTags: string[]; tags: string[] }): unknown
}>()
</script>

<template>
  <span v-if="tags.length === 0">-</span>

  <span v-else-if="tags.length === 1" class="inline-flex min-w-0">
    <el-tag class="mk-tag-group__first max-w-32.5" type="info" :size="size" :title="tags[0]">
      {{ tags[0] }}
    </el-tag>
  </span>

  <el-popover
    v-else-if="triggerArea === 'all'"
    :disabled="popoverDisabled"
    placement="bottom-start"
    :persistent="false"
    trigger="hover"
    :width="popoverWidth"
  >
    <template #reference>
      <span class="inline-flex min-w-0 items-center gap-1">
        <el-tag class="mk-tag-group__first max-w-32.5" type="info" :size="size" :title="tags[0]">
          {{ tags[0] }}
        </el-tag>
        <el-tag type="info" :size="size">+{{ tags.length - 1 }}</el-tag>
      </span>
    </template>

    <slot name="popover" :tags="tags" :overflow-tags="tags.slice(1)">
      <div class="flex flex-wrap gap-1">
        <el-tag v-for="tag in tags.slice(1)" :key="tag" type="info" :size="size">
          {{ tag }}
        </el-tag>
      </div>
    </slot>
  </el-popover>

  <span v-else class="inline-flex min-w-0 items-center gap-1">
    <el-tag class="mk-tag-group__first max-w-32.5" type="info" :size="size" :title="tags[0]">
      {{ tags[0] }}
    </el-tag>

    <el-popover
      :disabled="popoverDisabled"
      placement="bottom-start"
      :persistent="false"
      trigger="hover"
      :width="popoverWidth"
    >
      <template #reference>
        <el-tag type="info" :size="size">+{{ tags.length - 1 }}</el-tag>
      </template>

      <slot name="popover" :tags="tags" :overflow-tags="tags.slice(1)">
        <div class="flex flex-wrap gap-1">
          <el-tag v-for="tag in tags.slice(1)" :key="tag" type="info" :size="size">
            {{ tag }}
          </el-tag>
        </div>
      </slot>
    </el-popover>
  </span>
</template>

<style scoped lang="scss">
.mk-tag-group__first {
  :deep(.el-tag__content) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
