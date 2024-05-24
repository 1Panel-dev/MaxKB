<template>
  <MdEditor noIconfont v-bind="$attrs">
    <template #defFooters>
      <slot name="defFooters"> </slot>
    </template>
  </MdEditor>
</template>

<script setup lang="ts">
import { MdEditor, config } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

import screenfull from 'screenfull'

import katex from 'katex'
import 'katex/dist/katex.min.css'

import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'

import mermaid from 'mermaid'

import highlight from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

// >=3.0
import * as prettier from 'prettier'
import parserMarkdown from 'prettier/plugins/markdown'

// https://at.alicdn.com/t/c/font_2605852_u82y61ve02.js
import './assets/font_prouiefeic.js'

config({
  editorExtensions: {
    prettier: {
      prettierInstance: prettier,
      parserMarkdownInstance: parserMarkdown
    },
    highlight: {
      instance: highlight
    },
    screenfull: {
      instance: screenfull
    },
    katex: {
      instance: katex
    },
    cropper: {
      instance: Cropper
    },
    mermaid: {
      instance: mermaid
    }
  }
})
</script>
