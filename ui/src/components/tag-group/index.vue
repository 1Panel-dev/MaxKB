<template>
  <div class="tag-group" v-if="props.tags.length">
    <el-tag :size="props.size" class="default-tag tag-ellipsis" :title="props.tags[0]">
      {{ i18n_name(props.tags[0]) }}
    </el-tag>
    <el-popover
      placement="bottom"
      :disabled="tooltipDisabled"
      :popper-style="{ width: 'auto', maxWidth: '300px' }"
      :persistent="false"
    >
      <template #reference>
        <el-tag :size="props.size" class="info-tag ml-4 cursor" v-if="props.tags?.length > 1">
          +{{ props.tags?.length - 1 }}
        </el-tag>
      </template>
      <el-space>
        <el-tag
          :size="props.size"
          v-for="item in props.tags.slice(1)"
          :key="item"
          class="default-tag mr-4"
        >
          {{ item }}
        </el-tag>
      </el-space>
    </el-popover>
  </div>
</template>
<script setup lang="ts">
import { i18n_name } from '@/utils/common'

const props = defineProps<{
  tags: string[]
  size?: 'large' | 'default' | 'small'
  tooltipDisabled?: boolean
}>()
</script>

<style lang="scss" scoped>
.tag-group {
  /* tag超出省略号 */
  .tag-ellipsis {
    box-sizing: border-box;
    max-width: 130px;
    :deep(.el-tag__content) {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }
}
.el-popper.is-customized {
  background: #ffffff;
  box-shadow: 0px 4px 8px 0px rgba(var(--el-text-color-primary-rgb), 0.1);
}

.el-popper.is-customized .el-popper__arrow::before {
  background: #ffffff;
  right: 0;
}
</style>
