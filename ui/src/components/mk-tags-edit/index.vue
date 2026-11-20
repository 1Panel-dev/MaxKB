<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { InputInstance } from 'element-plus'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MkTagsEdit' })

const { t } = useI18n({ useScope: 'global' })

const tags = defineModel<string[]>({ required: true })
const props = withDefaults(defineProps<{ presetExtensions?: readonly string[] }>(), {
  presetExtensions: () => [],
})

// 标签编辑：自动聚焦，确定时清理输入并检查重复值。
const tagInputVisible = ref(false)
const tagInput = ref('')
const inputRef = useTemplateRef<InputInstance>('inputRef')

function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => inputRef.value?.focus())
}

function normalizeExtension(extension: string) {
  return extension.trim().replace(/^\./, '').toUpperCase()
}

function confirmTag() {
  const tag = normalizeExtension(tagInput.value)
  if (tag) {
    if (
      props.presetExtensions.some((presetExtension) => normalizeExtension(presetExtension) === tag) ||
      tags.value.some((currentTag) => normalizeExtension(currentTag) === tag)
    ) {
      MsgWarning(t('upload.extension.duplicateMessage'))
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
      :placeholder="t('upload.extension.add')"
      @blur="confirmTag"
      @keyup.enter="confirmTag"
    />
    <!-- 添加文件后缀 -->
    <el-button class="mk-add-tag-button" plain v-else size="small" @click="showTagInput">
      <MkIcon name="icon_add_outlined" size="14" />
      <span>{{ t('upload.extension.add') }}</span>
    </el-button>
  </div>
</template>
<style lang="scss" scoped></style>
