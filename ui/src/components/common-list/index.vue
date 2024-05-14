<template>
  <div class="common-list">
    <ul v-if="data.length > 0">
      <template v-for="(item, index) in data" :key="index">
        <li
          @click.prevent="clickHandle(item, index)"
          :class="current === index ? 'active' : ''"
          class="cursor"
        >
          <slot :row="item" :index="index"> </slot>
        </li>
      </template>
    </ul>
    <el-empty description="暂无数据" v-else />
  </div>
</template>
<script setup lang="ts">
import { ref, watch, useSlots } from 'vue'

defineOptions({ name: 'CommonList' })

const props = withDefaults(
  defineProps<{
    data: Array<any>
    defaultActive?: string
  }>(),
  {
    data: () => [],
    defaultActive: ''
  }
)

watch(
  () => props.defaultActive,
  (val) => {
    if (val) {
      current.value = props.data.findIndex((v) => v.id === val)
    }
  },
  { immediate: true }
)

const emit = defineEmits(['click'])

const current = ref(0)

function clickHandle(row: any, index: number) {
  current.value = index
  emit('click', row)
}
</script>
<style lang="scss" scoped>
/* 通用 ui li样式 */
.common-list {
  li {
    padding: 10px 16px;
    &.active {
      background: var(--el-color-primary-light-9);
      border-radius: 4px;
      color: var(--el-color-primary);
    }
  }
}
</style>
