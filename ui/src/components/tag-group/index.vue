<template>
  <div class="tag-group" v-if="props.tags.length">
    <el-tag class="default-tag" style="max-width: 100%">
      <span class="ellipsis" style="max-width: 100%">{{ props.tags[0] }}</span>
    </el-tag>
    <el-tooltip effect="light">
      <el-tag class="info-tag ml-4 cursor" v-if="props.tags?.length > 1">
        +{{ props.tags?.length - 1 }}
      </el-tag>
      <template #content>
        <el-tag v-for="item in props.tags.slice(1)" :key="item" class="default-tag mr-4">
          {{ item }}
        </el-tag>
      </template>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
const props = defineProps<{
  tags: string[]
}>()
</script>

<style lang="scss" scoped>
.tag-group {
  :deep(.el-tag__content) {
    width: 100%;
  }
}
</style>
