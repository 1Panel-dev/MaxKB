<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { InputInstance } from 'element-plus'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MkTagsEdit' })

const tags = defineModel<string[]>({ required: true })
const props = withDefaults(defineProps<{ reservedTags?: readonly string[]; normalizeTag?: (tag: string) => string }>(), {
  reservedTags: () => [],
})

// 标签编辑：自动聚焦，确认时清理输入并检查重复值。
const tagInputVisible = ref(false)
const tagInput = ref('')
const inputRef = useTemplateRef<InputInstance>('inputRef')

function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => inputRef.value?.focus())
}

function confirmTag() {
  const input = tagInput.value.trim()
  const tag = props.normalizeTag ? props.normalizeTag(input) : input
  if (tag) {
    if (props.reservedTags.includes(tag) || tags.value.includes(tag)) {
      MsgWarning('文件后缀已存在')
    } else {
      tags.value = [...tags.value, tag]
    }
  }
  tagInput.value = ''
  tagInputVisible.value = false
}

function removeTag(tag: string) {
  tags.value = tags.value.filter((currentTag) => currentTag !== tag)
}
</script>

<template>
  <div class="mk-tags-edit flex flex-wrap gap-2" @click.stop>
    <template v-for="tag in tags" :key="tag">
      <el-tag closable effect="plain" type="info" :disable-transitions="true" @close="removeTag(tag)">
        {{ tag }}
      </el-tag>
    </template>

    <el-input
      v-if="tagInputVisible"
      ref="inputRef"
      v-model="tagInput"
      class="w-26!"
      size="small"
      placeholder="添加后缀名"
      @blur="confirmTag"
      @keyup.enter="confirmTag"
    />
    <el-button class="add-tag-button" plain v-else size="small" @click="showTagInput">
      <MkIcon name="icon_add_outlined" size="14" />
      <span>添加后缀名</span>
    </el-button>
  </div>
</template>
<style lang="scss" scoped>
.mk-tags-edit {
  .add-tag-button {
    padding: 0 8px;
    height: 24px;
    line-height: 24px;
    font-size: 14px;
    border: 1px dashed var(--el-border-color);
    border-radius: var(--el-border-radius-small);
    color: var(--mk-N500);
  }
}
</style>
