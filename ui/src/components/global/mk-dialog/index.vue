<script setup lang="ts">
defineOptions({ name: 'MkDialog', inheritAttrs: false })

const visible = defineModel<boolean>({ default: false })

defineSlots<{
  default(): unknown
  footer(): unknown
  header(): unknown
}>()
</script>

<template>
  <el-dialog
    v-model="visible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :show-close="true"
    :width="600"
    v-bind="$attrs"
  >
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>

    <el-scrollbar max-height="calc(100vh - 120px)">
      <div><slot /></div>
    </el-scrollbar>

    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </el-dialog>
</template>
