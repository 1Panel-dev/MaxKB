<template>
  <MdEditor noIconfont noPrettier v-bind="$attrs">
    <template #defFooters>
      <slot name="defFooters"> </slot>
    </template>
  </MdEditor>
</template>

<script setup lang="ts">
import { MdEditor } from 'md-editor-v3'

import './assets/markdown-iconfont.js'
defineOptions({ name: 'MdEditor' })
</script>
