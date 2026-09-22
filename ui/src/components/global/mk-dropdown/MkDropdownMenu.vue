<script setup lang="ts">
import { provide, ref } from 'vue'
import { actionContextKey, type ActionContext } from '../mk-action/context'

defineOptions({ name: 'MkDropdownMenu', inheritAttrs: false })

provide(actionContextKey, ref<ActionContext>({ display: 'menu' }))

defineSlots<{
  /** 菜单项，使用 MkDropdownItem 或以 MkAction 为入口的业务 Action */
  default(): unknown
}>()
</script>

<template>
  <el-dropdown-menu v-bind="$attrs">
    <slot />
  </el-dropdown-menu>
</template>
