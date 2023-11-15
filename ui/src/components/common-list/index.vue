<template>
  <div class="common-list">
    <el-scrollbar>
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
    </el-scrollbar>
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
defineOptions({ name: 'CommonList' })
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  }
})

const emit = defineEmits(['click'])

const current = ref(0)

function clickHandle(row: any, index: number) {
  current.value = index
  emit('click', row)
}
</script>
<style lang="scss" scoped>
// 通用 ui li样式
.common-list {
  li {
    padding: 11px 16px;
    &.active {
      background: var(--el-color-primary-light-9);
      border-radius: 4px;
      color: var(--el-color-primary);
    }
  }
}
</style>
