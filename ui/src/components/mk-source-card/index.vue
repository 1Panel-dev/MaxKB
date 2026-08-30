<script setup lang="ts">
import { h, type FunctionalComponent } from 'vue'
import { dateFormat } from '@/utils/time'
import MkSourceCardAction from './mk-source-card-action.vue'
import MkSourceCardActionDropdown from './mk-source-card-action-dropdown.vue'

/**

 * 自定义标题：title 插槽提供原始 title，可在省略标题后紧跟状态图标。
 * @example
 * <template #title="{ title }">
 *   <h6 class="min-w-0 truncate" :title="title">{{ title }}</h6>
 *   <StatusIcon class="shrink-0" />
 * </template>
 *
 * Footer：常驻内容直接放在 footer；悬浮操作放入 Action。
 * ActionDropdown 是可选的，不需要 More 菜单时只保留 switch 即可。
 * @example
 * <template #footer="{ Action, ActionDropdown }">
 *   <MkStatusLabel :active="active" />
 *   <component :is="Action">
 *     <el-switch v-model="active" size="small" />
 *     <component :is="ActionDropdown">
 *       <MkDropdownItem>编辑</MkDropdownItem>
 *     </component>
 *   </component>
 * </template>
 */
defineOptions({ name: 'MkSourceCard' })

const props = withDefaults(
  defineProps<{
    create_time?: string //创建日期
    nick_name?: string // 创建者
    selectable?: boolean
    selected?: boolean
    title: string
  }>(),
  { selectable: false, selected: false },
)

const emit = defineEmits<{ selected: [selected: boolean] }>()

const slots = defineSlots<{
  default?: () => unknown
  footer?: (props: { Action: FunctionalComponent; ActionDropdown: typeof MkSourceCardActionDropdown }) => unknown
  icon?: () => unknown
  subtitle?: () => unknown
  tag?: () => unknown
  title?: (props: { title: string }) => unknown
}>()

const SourceCardAction: FunctionalComponent = (_, { slots }) => (props.selectable ? null : h(MkSourceCardAction, null, slots))

function handleSelect() {
  if (props.selectable) emit('selected', !props.selected)
}

function handleSelectedChange(selected: boolean | string | number) {
  emit('selected', Boolean(selected))
}
</script>

<template>
  <el-card
    :class="{ 'cursor-pointer': props.selectable, 'border-primary! bg-primary/10!': props.selectable && props.selected }"
    :role="props.selectable ? 'checkbox' : undefined"
    :tabindex="props.selectable ? 0 : undefined"
    shadow="hover"
    class="mk-source-card group relative"
    body-class="flex h-full flex-col"
    @click="handleSelect"
  >
    <div v-if="props.selectable" class="absolute top-4 right-4 z-10" @click.stop @keydown.stop>
      <el-checkbox :model-value="props.selected" @change="handleSelectedChange" />
    </div>

    <header class="flex-between items-start gap-2" :class="{ 'pr-7': props.selectable }">
      <div class="flex min-w-0 flex-1 items-center gap-3">
        <div v-if="slots.icon" class="shrink-0">
          <slot name="icon" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex min-w-0 items-center gap-2">
            <slot name="title" :title="props.title">
              <h6 class="min-w-0 truncate" :title="props.title">{{ props.title }}</h6>
            </slot>
          </div>
          <div class="text-sm text-N600">
            <slot name="subtitle">
              <div class="flex gap-1">
                <span>{{ props.nick_name }}</span>
                <span>创建于</span>
                <span>{{ dateFormat(props.create_time) }}</span>
              </div>
            </slot>
          </div>
        </div>
      </div>

      <slot name="tag" />
    </header>
    <div class="my-4 h-full text-N600">
      <slot />
    </div>

    <footer class="flex items-center gap-2">
      <slot name="footer" :Action="SourceCardAction" :ActionDropdown="MkSourceCardActionDropdown" />
    </footer>
  </el-card>
</template>

<style lang="scss" scoped>
.mk-source-card {
  min-width: 250px;
  min-height: 172px;
}
</style>
