<template>
  <MdEditor noIconfont noPrettier v-bind="$attrs">
    <template #defFooters>
      <slot name="defFooters"> </slot>
    </template>
  </MdEditor>
</template>

<script setup lang="ts">
import { MdEditor } from 'md-editor-v3'

// // <3.0
// import prettier from 'prettier'
// import parserMarkdown from 'prettier/parser-markdown'
// // >=3.0
// import * as prettier from 'prettier'
// import parserMarkdown from 'prettier/plugins/markdown'

// https://at.alicdn.com/t/c/font_2605852_u82y61ve02.js
import './assets/iconfont.js'
</script>
