<script setup lang="ts">
import type { TagProps } from 'element-plus'

defineOptions({ name: 'MkTagGroup' })

withDefaults(
  defineProps<{
    /** 是否禁用标签组浮层 */
    popoverDisabled?: boolean
    /** 标签文字 */
    tags?: string[]
    /** 标签尺寸 */
    size?: TagProps['size']
    /** 首个标签的类型 */
    type?: TagProps['type']
  }>(),
  { popoverDisabled: false, tags: () => [], type: 'info' },
)
</script>

<template>
  <span class="inline-flex items-center gap-1">
    <el-tag :type="type" :size="size" :title="tags?.[0]" :disable-transitions="true">
      {{ tags?.[0] }}
    </el-tag>

    <el-popover
      :disabled="popoverDisabled"
      placement="bottom-start"
      popper-class="mk-tag-group__popper"
      trigger="hover"
      :popper-style="{ maxWidth: '250px', width: 'auto' }"
      :show-after="200"
      v-if="tags?.length > 1"
    >
      <template #reference>
        <el-tag type="info" :size="size" class="cursor-pointer" :disable-transitions="true">+{{ tags.length - 1 }}</el-tag>
      </template>
      <div class="flex-wrap gap-2 px-4 py-3">
        <el-tag v-for="tag in tags.slice(1)" :key="tag" type="info" :size="size" :title="tag" :disable-transitions="true">
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
