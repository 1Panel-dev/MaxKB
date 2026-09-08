<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { InputInstance } from 'element-plus'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MkTagsEdit' })

const extensions = defineModel<string[]>({ required: true })
const props = withDefaults(defineProps<{ reservedExtensions?: readonly string[] }>(), {
  reservedExtensions: () => [],
})

// 扩展名编辑：自动聚焦，确认时归一化并检查重复值。
const extensionInputVisible = ref(false)
const extensionInput = ref('')
const inputRef = useTemplateRef<InputInstance>('inputRef')

function showExtensionInput() {
  extensionInputVisible.value = true
  nextTick(() => inputRef.value?.focus())
}

function confirmExtension() {
  const extension = extensionInput.value.trim().replace(/^\./, '').toUpperCase()
  if (extension) {
    if (props.reservedExtensions.includes(extension) || extensions.value.includes(extension)) {
      MsgWarning('该扩展名已存在')
    } else {
      extensions.value = [...extensions.value, extension]
    }
  }
  extensionInput.value = ''
  extensionInputVisible.value = false
}

function removeExtension(extension: string) {
  extensions.value = extensions.value.filter((currentExtension) => currentExtension !== extension)
}
</script>

<template>
  <div class="flex flex-wrap gap-2" @click.stop>
    <el-tag v-for="extension in extensions" :key="extension" closable effect="plain" type="info" @close="removeExtension(extension)">
      {{ extension }}
    </el-tag>
    <el-input
      v-if="extensionInputVisible"
      ref="inputRef"
      v-model="extensionInput"
      class="w-24!"
      size="small"
      @blur="confirmExtension"
      @keyup.enter="confirmExtension"
    />
    <el-button v-else size="small" @click="showExtensionInput">
      <MkIcon name="icon_add_outlined" />
      添加扩展名
    </el-button>
  </div>
</template>
