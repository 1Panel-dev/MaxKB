<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules, InputInstance } from 'element-plus'
import { EditPen, Loading } from '@element-plus/icons-vue'

defineOptions({ name: 'MkEditName' })

const name = defineModel<string>({ required: true })
const props = defineProps<{
  maxlength?: number
  validate?: (name: string) => string | undefined
  save: (name: string) => Promise<string>
}>()
defineSlots<{ prefix(): unknown }>()

/* 名称编辑：草稿独立于已保存名称，取消不回写。 */
const editing = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const draft = ref({ name: '' })
const formRef = useTemplateRef<FormInstance>('formRef')
const inputRef = useTemplateRef<InputInstance>('inputRef')
const composing = ref(false)
const blurredDuringComposition = ref(false)
const nameRules = computed<FormRules>(() => ({
  name: [
    { required: true, message: '请输入名称' },
    { whitespace: true, message: '名称不能只有空格' },
    ...(props.maxlength === undefined ? [] : [{ max: props.maxlength, message: `名称不能超过 ${props.maxlength} 个字符` }]),
  ],
}))

function startEditing() {
  draft.value.name = name.value
  errorMessage.value = ''
  composing.value = false
  blurredDuringComposition.value = false
  editing.value = true
  nextTick(() => {
    inputRef.value?.focus()
    inputRef.value?.select()
  })
}

function cancelEditing() {
  if (saving.value) return
  editing.value = false
  errorMessage.value = ''
  blurredDuringComposition.value = false
}

/* 校验和保存共用锁，防止 Enter 与失焦重复提交。 */
async function saveName() {
  if (!editing.value || saving.value || composing.value) return
  saving.value = true
  errorMessage.value = ''
  try {
    const valid = await formRef.value?.validate((valid, fields) => {
      if (!valid) errorMessage.value = fields?.name?.[0]?.message ?? '请输入有效名称'
    })
    if (!valid) return

    const nextName = draft.value.name.trim()
    errorMessage.value = props.validate?.(nextName) ?? ''
    if (errorMessage.value) return
    if (nextName === name.value) {
      editing.value = false
      return
    }

    name.value = await props.save(nextName)
    editing.value = false
  } catch {
    // 接口错误由请求层提示，此处保留可重试的编辑状态。
    errorMessage.value = '保存失败，请重试'
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
  <div class="group flex-align-center min-h-8 min-w-0 w-full gap-1">
    <template v-if="!editing">
      <span v-if="$slots.prefix" class="flex-center shrink-0"><slot name="prefix" /></span>
      <span class="min-w-0 truncate" :title="name">{{ name }}</span>
      <MkTooltip content="编辑名称">
        <!-- 编辑名称 -->
        <el-button class="group-hover-visible shrink-0" text circle size="small" title="编辑名称" @click.stop="startEditing">
          <MkIcon :icon="EditPen" />
        </el-button>
      </MkTooltip>
    </template>
    <el-form
      v-else
      ref="formRef"
      class="min-w-0 w-full"
      :model="draft"
      :rules="nameRules"
      :show-message="false"
      @submit.prevent.stop
      @click.stop
      @keydown.stop="handleKeydown"
    >
      <el-form-item prop="name" class="mb-0!" :error="errorMessage">
        <MkTooltip :visible="!!errorMessage" :content="errorMessage" placement="top" :show-after="0">
          <el-input
            ref="inputRef"
            v-model="draft.name"
            placeholder="请输入名称"
            :maxlength="maxlength"
            :readonly="saving"
            :validate-event="false"
            @input="
              errorMessage = ''
              formRef?.clearValidate()
            "
            @blur="handleBlur"
            @compositionstart="composing = true"
            @compositionend="handleCompositionEnd"
          >
            <template v-if="saving" #suffix><MkIcon :icon="Loading" class="animate-spin" /></template>
          </el-input>
        </MkTooltip>
      </el-form-item>
    </el-form>
  </div>
</template>
