<script setup lang="ts">
defineOptions({ name: 'MkDrawer', inheritAttrs: false })

withDefaults(
  defineProps<{
    closeOnClickModal?: boolean
    closeOnPressEscape?: boolean
    destroyOnClose?: boolean
    showClose?: boolean
  }>(),
  {
    closeOnClickModal: false,
    closeOnPressEscape: false,
    destroyOnClose: true,
    showClose: true,
  },
)

const visible = defineModel<boolean>({ default: false })

defineSlots<{
  default(): unknown
  footer(): unknown
  header(): unknown
}>()
</script>

<template>
  <el-drawer
    v-model="visible"
    size="600"
    v-bind="$attrs"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :destroy-on-close="destroyOnClose"
    :show-close="showClose"
  >
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>

    <el-scrollbar>
      <div class="p-6"><slot /></div>
    </el-scrollbar>

    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </el-drawer>
</template>
