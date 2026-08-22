<script setup lang="ts">
import { computed } from 'vue'
import noDataImage from '@/assets/empty/no-data.svg'
import noSearchResultsImage from '@/assets/empty/no-search-results.svg'

defineOptions({ name: 'MkEmpty', inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    description?: string
    image?: string
    imageSize?: number
    type?: 'default' | 'search' | ''
  }>(),
  {
    imageSize: 125,
    type: 'default',
  },
)

defineSlots<{
  default(): unknown
  description(): unknown
  image(): unknown
}>()

const emptyState = computed(() => {
  if (props.type === 'search') {
    return {
      description: '没有找到相关内容',
      image: noSearchResultsImage,
    }
  }

  return {
    description: '暂无数据',
    image: noDataImage,
  }
})
</script>

<template>
  <el-empty
    v-bind="$attrs"
    :description="props.description ?? emptyState.description"
    :image="props.image ?? emptyState.image"
    :image-size="props.imageSize"
  >
    <template v-if="$slots.image" #image>
      <slot name="image" />
    </template>
    <template v-if="$slots.description" #description>
      <slot name="description" />
    </template>
    <template v-if="$slots.default" #default>
      <slot />
    </template>
  </el-empty>
</template>
