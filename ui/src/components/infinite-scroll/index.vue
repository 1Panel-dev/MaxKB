<template>
  <div v-infinite-scroll="loadData" :infinite-scroll-disabled="disabledScroll">
    <slot />
  </div>
  <div style="padding: 0 10px 16px" class="text-center lighter color-secondary">
    <el-text class="text-with-lines" type="info" v-if="size > 0 && loading">
      {{ $t('components.loading') }}...</el-text
    >
    <el-text class="text-with-lines" v-if="noMore" type="info">
      {{ $t('components.noMore') }}</el-text
    >
  </div>
</template>
<script setup lang="ts">
import { ref, computed, watch } from 'vue'

defineOptions({ name: 'InfiniteScroll' })
const props = defineProps({
  /**
   * 对象数量
   */
  size: {
    type: Number,
    default: 0,
  },
  /**
   * 总数
   */
  total: {
    type: Number,
    default: 0,
  },
  /**
   * 总数
   */
  page_size: {
    type: Number,
    default: 0,
  },
  current_page: {
    type: Number,
    default: 0,
  },
  loading: Boolean,
})

const emit = defineEmits(['update:current_page', 'load'])
const current = ref(props.current_page)

watch(
  () => props.current_page,
  (val) => {
    if (val === 1) {
      current.value = 1
    }
  },
)

const noMore = computed(
  () =>
    props.size > 0 && props.size === props.total && props.total > props.page_size && !props.loading,
)
const disabledScroll = computed(() => props.size > 0 && (props.loading || noMore.value))
function loadData() {
  if (props.total > props.page_size) {
    current.value += 1
    emit('update:current_page', current.value)
    emit('load')
  }
}
</script>
<style lang="scss" scoped>
.text-with-lines {
  position: relative;
  display: inline-block;
}

.text-with-lines::before,
.text-with-lines::after {
  content: '';
  position: absolute;
  width: 80px;
  border-bottom: 1px solid var(--el-border-color);
  top: 10px;
}

.text-with-lines::before {
  left: -88px; /* 左侧线条位置 */
}

.text-with-lines::after {
  right: -82px; /* 右侧线条位置 */
}
</style>
