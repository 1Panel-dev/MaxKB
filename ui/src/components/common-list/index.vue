<template>
  <div class="common-list">
    <ul v-if="data.length > 0">
      <InfiniteScroll
        :size="renderList.length"
        :total="data.length"
        :page_size="paginationConfig.page_size"
        v-model:current_page="paginationConfig.current_page"
      >
        <template v-for="(item, index) in renderList" :key="item[props.valueKey] ?? index">
          <li
            @click.stop="clickHandle(item, index)"
            :class="current === item[props.valueKey] ? 'active color-primary-1' : ''"
            class="cursor"
            @mouseenter.stop="mouseenter(item)"
            @mouseleave.stop="mouseleave()"
          >
            <slot :row="item" :index="index"> </slot>
          </li>
        </template>
      </InfiniteScroll>
    </ul>
    <slot name="empty" v-else>
      <el-empty :description="$t('common.noData')" />
    </slot>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, reactive, computed } from 'vue'

defineOptions({ name: 'CommonList' })

const props = withDefaults(
  defineProps<{
    data: Array<any>
    defaultActive?: string
    valueKey?: string // 唯一标识的键名
  }>(),
  {
    data: () => [],
    defaultActive: '',
    valueKey: 'id',
  },
)

const current = ref<number | string>(0)

watch(
  () => props.defaultActive,
  (val) => {
    current.value = val
  },
  { immediate: true },
)

const emit = defineEmits(['click', 'mouseenter', 'mouseleave'])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 50,
  total: 0,
})

// 前端分页滚动加载：data 为全量数据，仅渲染前 current_page * page_size 条，滚动到底再追加
const renderList = computed(() =>
  props.data.slice(0, paginationConfig.current_page * paginationConfig.page_size),
)

// 数据源变化时重置到第一页，避免切换数据后仍停留在很大的页码
watch(
  () => props.data,
  () => {
    paginationConfig.current_page = 1
  },
)

function mouseenter(row: any) {
  emit('mouseenter', row)
}
function mouseleave() {
  emit('mouseleave')
}

function clickHandle(row: any, index: number) {
  current.value = row[props.valueKey]
  emit('click', row)
}

function clearCurrent() {
  current.value = 0
}
defineExpose({
  clearCurrent,
})
</script>
<style lang="scss" scoped>
/* 通用 ui li样式 */
.common-list {
  li {
    padding: 8px;
    font-weight: 400;
    font-size: 14px;
    margin-bottom: 4px;
    min-height: 24px;
    line-height: 24px;
    &.active {
      background: var(--el-color-primary-light-9);
      border-radius: var(--app-border-radius-small);
      color: var(--el-color-primary);
      font-weight: 500;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
    }
    &:hover {
      border-radius: var(--app-border-radius-small);
      background: rgba(var(--el-text-color-primary-rgb), 0.1);
    }
    &.is-active {
      &:hover {
        color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
      }
    }
  }
}
</style>
