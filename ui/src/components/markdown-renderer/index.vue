<template>
  <div v-html="markdownIt.render(source)" />
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import MarkdownItAbbr from 'markdown-it-abbr'
import MarkdownItAnchor from 'markdown-it-anchor'
import MarkdownItFootnote from 'markdown-it-footnote'
import MarkdownItHighlightjs from 'markdown-it-highlightjs'
import MarkdownItTasklists from 'markdown-it-task-lists'
import MarkdownItSub from 'markdown-it-sub'
import MarkdownItSup from 'markdown-it-sup'
import MarkdownItTOC from 'markdown-it-toc-done-right'

defineOptions({ name: 'MarkdownRenderer' })

const markdownIt = MarkdownIt({
  html: true, // 允许HTML语法
  typographer: true, // 启用Typographer插件，可以更好地处理中文字符和标点符号
  linkify: true // 自动将文本中的URL转换为链接
})

markdownIt
  .use(MarkdownItHighlightjs)
  .use(MarkdownItTasklists)
  .use(MarkdownItAbbr)
  .use(MarkdownItAnchor)
  .use(MarkdownItFootnote)
  .use(MarkdownItSub)
  .use(MarkdownItSup)
  .use(MarkdownItTOC)

defineProps({
  source: {
    type: String,
    default: ''
  }
})
</script>
