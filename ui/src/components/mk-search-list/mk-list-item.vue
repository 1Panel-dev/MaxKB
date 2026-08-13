<script setup lang="ts" generic="T extends Record<string, unknown>">
defineOptions({ name: 'MkSearchListItem' })

defineProps<{
  active?: boolean
  index: number
  labelField: keyof T & string
  row: T
}>()

const emit = defineEmits<{
  click: []
}>()

defineSlots<{
  action(props: { row: T; index: number }): unknown
  'action-dropdown'(props: { row: T; index: number }): unknown
  default?(props: { row: T; index: number; active: boolean }): unknown
}>()
</script>

<template>
  <div
    class="group flex cursor-pointer items-center rounded-md p-2 hover:bg-N900/10"
    :class="{ 'bg-primary/10 font-medium text-primary hover:bg-primary/10': active }"
    @click="emit('click')"
  >
    <slot :row="row" :index="index" :active="Boolean(active)">
      <span class="min-w-0 flex-1 truncate">{{ row[labelField] }}</span>
    </slot>
    <!-- 操作区保留布局宽度，hover/focus 时显示，并阻止触发行点击。 -->
    <div
      v-if="$slots.action || $slots['action-dropdown']"
      class="pointer-events-none ml-auto flex shrink-0 items-center font-normal text-N900 opacity-0 transition-opacity group-hover:pointer-events-auto group-hover:opacity-100 focus-within:pointer-events-auto focus-within:opacity-100"
      @click.stop
      @keydown.stop
    >
      <MkDropdown v-if="$slots['action-dropdown']" trigger="click" :teleported="false">
        <el-button class="-mr-1" text>
          <MkIcon name="icon_more_outlined" />
        </el-button>
        <template #dropdown>
          <slot name="action-dropdown" :row="row" :index="index" />
        </template>
      </MkDropdown>
      <slot v-else name="action" :row="row" :index="index" />
    </div>
  </div>
</template>
