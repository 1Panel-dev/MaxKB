<script setup lang="ts" generic="T extends object">
import { computed } from 'vue'
import type { TagProps } from 'element-plus'
import { TOOLTIP_SHOW_DELAY } from '@/components/global/mk-tooltip/constants'

defineOptions({ name: 'MkTagGroup' })

const props = withDefaults(
  defineProps<{
    /** 是否禁用标签组浮层 */
    popoverDisabled?: boolean
    /** 字符串或待格式化的标签数据 */
    tags?: (string | T)[]
    /** 获取对象标签的展示文字 */
    formatLabel?: (tag: T) => string
    /** 标签尺寸 */
    size?: TagProps['size']
    /** 首个标签的类型 */
    type?: TagProps['type']
  }>(),
  { popoverDisabled: false, tags: () => [], type: 'info', size: 'small' },
)

const tagLabels = computed(() => {
  const { tags, formatLabel } = props
  return (tags ?? []).flatMap((tag) => {
    if (typeof tag === 'string') return [tag]
    return formatLabel ? [formatLabel(tag)] : []
  })
})
</script>

<template>
  <span class="inline-flex items-center gap-1">
    <el-tag :type="type" :size="size" :title="tagLabels[0]" :disable-transitions="true">
      {{ tagLabels[0] }}
    </el-tag>

    <el-popover
      :disabled="popoverDisabled"
      placement="bottom-start"
      popper-class="mk-tag-group__popper"
      trigger="hover"
      :popper-style="{ maxWidth: '250px', width: 'auto' }"
      :show-after="TOOLTIP_SHOW_DELAY"
      v-if="tagLabels.length > 1"
    >
      <template #reference>
        <el-tag type="info" :size="size" class="cursor-pointer" :disable-transitions="true">+{{ tagLabels.length - 1 }}</el-tag>
      </template>
      <div class="flex-wrap gap-2 px-4 py-3">
        <el-tag v-for="tag in tagLabels.slice(1)" :key="tag" type="info" :size="size" :title="tag" :disable-transitions="true">
          {{ tag }}
        </el-tag>
      </div>
    </el-popover>
  </span>
</template>

<style scoped lang="scss">
:global(.el-popper.el-popover.mk-tag-group__popper[data-popper-placement]) {
  translate: 0 -2px;
}

:global(.el-popper.el-popover.mk-tag-group__popper .el-popper__arrow) {
  display: block;
  &[data-popper-placement] {
    translate: none;
  }
}
</style>
