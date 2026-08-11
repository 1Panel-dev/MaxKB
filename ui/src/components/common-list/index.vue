<template>
  <div class="common-list">
    <ul v-if="data.length > 0">
      <template v-for="(item, index) in data" :key="item[valueKey] ?? index">
        <li
          @click.stop="clickHandle(item, index)"
          :class="current === item[valueKey] ? 'active' : ''"
          class="cursor"
        >
          <slot :row="item" :index="index" />
        </li>
      </template>
    </ul>
    <slot v-else name="empty">
      <el-empty description="暂无数据" />
    </slot>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    data: any[]
    defaultActive?: string
    valueKey?: string
    loading?: boolean
  }>(),
  {
    data: () => [],
    defaultActive: '',
    valueKey: 'id',
    loading: false,
  },
)

const emit = defineEmits<{
  (e: 'click', item: any): void
}>()

const current = ref<string | number>('')

watch(
  () => props.defaultActive,
  (val) => {
    current.value = val
  },
  { immediate: true },
)

function clickHandle(row: any, _index: number) {
  current.value = row[props.valueKey]
  emit('click', row)
}

function clearCurrent() {
  current.value = ''
}

defineExpose({ clearCurrent })
</script>

<style lang="scss" scoped>
.common-list {
  li {
    padding: 8px;
    font-weight: 400;
    font-size: 14px;
    margin-bottom: 4px;
    min-height: 24px;
    line-height: 24px;
    border-radius: 6px;
    &.active {
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      font-weight: 500;
      &:hover {
        background: var(--el-color-primary-light-9);
      }
    }
    &:hover {
      background: rgba(var(--el-text-color-primary-rgb), 0.06);
    }
  }
}
</style>
