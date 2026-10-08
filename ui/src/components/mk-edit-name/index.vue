<script setup lang="ts">
import { nextTick, ref, useTemplateRef, watch } from 'vue'
import type { InputInstance } from 'element-plus'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'MkEditName' })

const name = defineModel<string>({ required: true })
const props = defineProps<{
  disabled?: boolean
  maxlength?: number
  validate?: (name: string) => string | undefined
  save: (name: string) => Promise<string>
}>()
defineSlots<{ prefix(): unknown }>()

/* 名称编辑：草稿独立于已保存名称，取消不回写。 */
const editing = ref(false)
const saving = ref(false)
const draftName = ref('')
const inputRef = useTemplateRef<InputInstance>('inputRef')
const composing = ref(false)
const blurredDuringComposition = ref(false)
function startEditing() {
  if (props.disabled) return
  draftName.value = name.value
  composing.value = false
  blurredDuringComposition.value = false
  editing.value = true
  nextTick(() => {
    inputRef.value?.focus()
    inputRef.value?.input?.setSelectionRange(draftName.value.length, draftName.value.length)
  })
}

function cancelEditing() {
  if (saving.value) return
  editing.value = false
  blurredDuringComposition.value = false
}

watch(
  () => props.disabled,
  (disabled) => {
    if (!disabled) return
    editing.value = false
    blurredDuringComposition.value = false
  },
)

/* 校验和保存共用锁，防止 Enter 与失焦重复提交。 */
async function saveName() {
  if (props.disabled || !editing.value || saving.value || composing.value) return
  saving.value = true
  try {
    const nextName = draftName.value.trim()
    if (!nextName) {
      MsgWarning('请输入名称')
      return
    }

    const validationMessage = props.validate?.(nextName)
    if (validationMessage) {
      MsgWarning(validationMessage)
      return
    }
    if (nextName === name.value) {
      editing.value = false
      return
    }

    name.value = await props.save(nextName)
    editing.value = false
  } catch {
    // 接口错误由请求层提示，此处保留可重试的编辑状态。
  } finally {
    saving.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.isComposing || composing.value || event.keyCode === 229) return
  if (event.key === 'Enter') {
    event.preventDefault()
    void saveName()
  } else if (event.key === 'Escape') {
    event.preventDefault()
    cancelEditing()
  }
}

function handleBlur() {
  if (composing.value) {
    blurredDuringComposition.value = true
    return
  }
  void saveName()
}

function handleCompositionEnd() {
  composing.value = false
  if (blurredDuringComposition.value) {
    blurredDuringComposition.value = false
    nextTick(() => void saveName())
  }
}
</script>

<template>
  <div class="group flex-align-center w-full gap-2">
    <template v-if="!editing">
      <span v-if="$slots.prefix" class="flex-center shrink-0"><slot name="prefix" /></span>
      <span class="min-w-0 truncate">{{ name }}</span>

      <!-- 编辑名称 -->
      <el-button v-if="!disabled" class="group-hover-visible shrink-0" text @click.stop="startEditing">
        <MkIcon name="icon_edit_outlined" />
      </el-button>
    </template>
    <el-input
      v-else
      ref="inputRef"
      v-model="draftName"
      class="min-w-0 w-full"
      placeholder="请输入名称"
      :maxlength="maxlength"
      :readonly="saving"
      :validate-event="false"
      @click.stop
      @keydown.stop="handleKeydown"
      @blur="handleBlur"
      @compositionstart="composing = true"
      @compositionend="handleCompositionEnd"
    />
  </div>
</template>
