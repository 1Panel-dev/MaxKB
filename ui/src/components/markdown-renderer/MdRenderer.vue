<template>
  <MdPreview
    ref="editorRef"
    editorId="preview-only"
    :modelValue="item"
    v-for="(item, index) in md_view_list"
    :key="index"
    class="maxkb-md"
  />
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { MdPreview, config } from 'md-editor-v3'
config({
  markdownItConfig(md) {
    md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
      tokens[idx].attrSet('target', '_blank')
      return md.renderer.renderToken(tokens, idx, options)
    }
  }
})
const props = withDefaults(defineProps<{ source?: string; inner_suffix?: boolean }>(), {
  source: ''
})
const editorRef = ref()
const md_view_list = computed(() => {
  const temp_source = props.source
  const temp_md_img_list = temp_source.match(/(!\[.*?\]\(img\/.*?\){.*?})|(!\[.*?\]\(img\/.*?\))/g)
  const md_img_list = temp_md_img_list ? temp_md_img_list.filter((i) => i) : []
  const split_img_value = temp_source
    .split(/(!\[.*?\]\(img\/.*?\){.*?})|(!\[.*?\]\(img\/.*?\))/g)
    .filter((item) => item !== undefined)
    .filter((item) => !md_img_list?.includes(item))
  const result = Array.from(
    { length: md_img_list.length + split_img_value.length },
    (v, i) => i
  ).map((index) => {
    if (index % 2 == 0) {
      return split_img_value[Math.floor(index / 2)]
    } else {
      return md_img_list[Math.floor(index / 2)]
    }
  })
  return result
})
</script>
<style lang="scss" scoped></style>
