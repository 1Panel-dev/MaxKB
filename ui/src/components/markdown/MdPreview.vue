<template>
  <MdPreview noIconfont noPrettier v-bind="$attrs" />
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3'
defineOptions({ name: 'MdPreview' })
</script>
