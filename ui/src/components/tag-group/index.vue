<template>
  <div class="tag-group" v-if="props.tags.length">
    <el-tag :size="props.size" class="default-tag tag-ellipsis" :title="props.tags[0]">
      {{ props.tags[0] }}
    </el-tag>
    <el-tooltip effect="light" :disabled="tooltipDisabled">
      <el-tag :size="props.size" class="info-tag ml-4 cursor" v-if="props.tags?.length > 1">
        +{{ props.tags?.length - 1 }}
      </el-tag>
      <template #content>
        <el-tag
          :size="props.size"
          v-for="item in props.tags.slice(1)"
          :key="item"
          class="default-tag mr-4"
        >
          {{ item }}
        </el-tag>
      </template>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
const props = defineProps<{
  tags: string[]
  size?: 'large' | 'default' | 'small'
  tooltipDisabled?: boolean
}>()
</script>

<style lang="scss" scoped>
.tag-group {
  :deep(.el-tag__content) {
    width: 100%;
  }
  /* tag超出省略号 */
  .tag-ellipsis {
    box-sizing: border-box;
    max-width: 130px;
    .el-tag__content {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }
}
</style>
