<template>
  <div class="common-list">
    <el-scrollbar>
      <ul v-if="data.length > 0">
        <li
          v-if="slots.prefix"
          @click="clickHandle()"
          :class="modelValue === undefined || modelValue === null ? 'active' : ''"
          class="cursor"
        >
          <slot name="prefix"> </slot>
        </li>
        <template v-for="(item, index) in data" :key="index">
          <li
            @click.prevent="clickHandle(item)"
            :class="modelValue === item ? 'active' : ''"
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
import { ref, watch, useSlots } from 'vue'

const slots = useSlots()
defineOptions({ name: 'CommonList' })

withDefaults(
  defineProps<{
    modelValue?: any

    data: Array<any>
  }>(),
  {
    data: () => []
  }
)

const emit = defineEmits(['click', 'update:modelValue'])

function clickHandle(row?: any) {
  emit('click', row)
  emit('update:modelValue', row)
}
</script>
<style lang="scss" scoped>
/* 通用 ui li样式 */
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
