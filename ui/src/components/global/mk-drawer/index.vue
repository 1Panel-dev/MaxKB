<script setup lang="ts">
defineOptions({ name: 'MkDrawer', inheritAttrs: false })

const props = defineProps<{ contentClass?: string }>()

const visible = defineModel<boolean>({ default: false })

defineSlots<{ default(): unknown; footer(): unknown; header(): unknown }>()
</script>

<template>
  <el-drawer
    v-model="visible"
    :append-to-body="true"
    size="700"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :show-close="true"
    v-bind="$attrs"
  >
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>

    <el-scrollbar view-class="h-full">
      <div class="p-6" :class="props.contentClass"><slot /></div>
    </el-scrollbar>

    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </el-drawer>
</template>
