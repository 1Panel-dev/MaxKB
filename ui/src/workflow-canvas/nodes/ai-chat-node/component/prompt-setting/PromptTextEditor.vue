<script setup lang="ts">
import { ref } from 'vue'
import { FullScreen } from '@element-plus/icons-vue'

defineOptions({ name: 'AiChatNodePromptTextEditor' })

const props = withDefaults(defineProps<{ modelValue: string; placeholder?: string; rows?: number; title: string }>(), { placeholder: '', rows: 4 })
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const visible = ref(false)
const draft = ref('')

function open() {
  draft.value = props.modelValue
  visible.value = true
}

function submit() {
  emit('update:modelValue', draft.value)
  visible.value = false
}
</script>

<template>
  <div class="relative w-full">
    <el-input
      :model-value="modelValue"
      :placeholder="placeholder"
      :rows="rows"
      type="textarea"
      @update:model-value="emit('update:modelValue', $event)"
      @wheel.stop
    />
    <el-button class="absolute right-2 bottom-2" size="small" text title="放大编辑" @click="open">
      <MkIcon :icon="FullScreen" />
    </el-button>
  </div>

  <MkDialog v-model="visible" :title="title" width="900">
    <el-input v-model="draft" :autosize="{ minRows: 18, maxRows: 28 }" :placeholder="placeholder" type="textarea" @wheel.stop />
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">确定</el-button>
    </template>
  </MkDialog>
</template>
