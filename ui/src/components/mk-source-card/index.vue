<script setup lang="ts">
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
 *       <MkDropdownMenu>
 *         <MkDropdownItem>编辑</MkDropdownItem>
 *       </MkDropdownMenu>
 *     </component>
 *   </component>
 * </template>
 */
defineOptions({ name: 'MkSourceCard' })

const props = defineProps<{
  create_time?: string  //创建日期
  nick_name?: string // 创建者
  title: string
}>()

const slots = defineSlots<{
  default?: () => unknown
  footer?: (props: {
    Action: typeof MkSourceCardAction
    ActionDropdown: typeof MkSourceCardActionDropdown
  }) => unknown
  icon?: () => unknown
  subtitle?: () => unknown
  tag?: () => unknown
  title?: (props: { title: string }) => unknown
}>()
</script>

<template>
  <el-card shadow="hover" class="mk-source-card group" body-class="flex h-full flex-col">
    <header class="flex-between items-start gap-2">
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
      <slot
        name="footer"
        :Action="MkSourceCardAction"
        :ActionDropdown="MkSourceCardActionDropdown"
      />
    </footer>
  </el-card>
</template>

<style lang="scss" scoped>
.mk-source-card {
  min-width: 250px;
  min-height: 172px;
}
</style>
