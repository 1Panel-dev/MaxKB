<script setup lang="ts">
defineOptions({ name: 'MkTagGroup' })

withDefaults(
  defineProps<{
    /** 是否禁用标签组浮层 */
    popoverDisabled?: boolean
    /** 标签文字 */
    tags?: string[]
  }>(),
  {
    popoverDisabled: false,
    tags: () => [],
  },
)
</script>

<template>
  <span class="inline-flex items-center gap-1">
    <el-tag type="info" :title="tags?.[0]">
      {{ tags?.[0] }}
    </el-tag>

    <el-popover
      :disabled="popoverDisabled"
      placement="bottom-start"
      :persistent="false"
      trigger="hover"
      v-if="tags?.length > 1"
    >
      <template #reference>
        <el-tag type="info" class="cursor-pointer">+{{ tags.length - 1 }}</el-tag>
      </template>
      <div class="flex-wrap gap-1">
        <el-tag v-for="tag in tags.slice(1)" :key="tag" type="info">
          {{ tag }}
        </el-tag>
      </div>
    </el-popover>
  </span>
</template>

<style scoped lang="scss"></style>
