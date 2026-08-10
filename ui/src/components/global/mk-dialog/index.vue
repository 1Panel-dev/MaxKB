<script setup lang="ts">
defineOptions({ name: 'MkDialog', inheritAttrs: false })

const visible = defineModel<boolean>({ default: false })

defineSlots<{
  default(): unknown
  footer(): unknown
  header(props: { close: () => void; titleClass: string; titleId: string }): unknown
  subtitle(): unknown
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
    <template v-if="$slots.header || $slots.subtitle" #header="{ close, titleClass, titleId }">
      <slot
        v-if="$slots.header"
        name="header"
        :close="close"
        :title-class="titleClass"
        :title-id="titleId"
      />
      <span v-else :id="titleId" :class="titleClass">{{ $attrs.title }}</span>
      <p v-if="$slots.subtitle" class="mt-2 text-N600">
        <slot name="subtitle" />
      </p>
    </template>

    <el-scrollbar>
      <div style="max-height: calc(100vh - 272px)">
        <slot />
      </div>
    </el-scrollbar>

    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </el-dialog>
</template>
