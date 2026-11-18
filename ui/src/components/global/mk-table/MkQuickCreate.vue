<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ButtonInstance, InputInstance } from 'element-plus'

defineOptions({ name: 'MkQuickCreate' })
const { t } = useI18n({ useScope: 'global' })

const props = withDefaults(
  defineProps<{
    loading?: boolean
    text?: string
    placeholder?: string
    maxlength?: number
  }>(),
  { loading: false, maxlength: 256 },
)
const emit = defineEmits<{ create: [name: string] }>()

/* 行内快速创建 */
const showCreateInput = ref(false)
const createName = ref('')
const createDisabled = computed(() => props.loading || !createName.value.trim())
const inputRef = ref<InputInstance>()
const triggerRef = ref<ButtonInstance>()

function handleShowCreateInput() {
  showCreateInput.value = true
  void nextTick(() => inputRef.value?.focus())
}

function resetDraft() {
  showCreateInput.value = false
  createName.value = ''
  void nextTick(() => triggerRef.value?.$el.focus())
}

function handleCancel() {
  if (!props.loading) resetDraft()
}

function handleCreate() {
  if (createDisabled.value) return
  emit('create', createName.value.trim())
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key !== 'Enter' || event.isComposing || event.keyCode === 229) return
  event.preventDefault()
  handleCreate()
}

defineExpose({ close: resetDraft })
</script>

<template>
  <div class="p-3">
    <div v-if="showCreateInput" class="flex-align-center" @keydown.esc.prevent="handleCancel">
      <el-input
        ref="inputRef"
        v-model="createName"
        class="mr-3 w-80!"
        :placeholder="props.placeholder ?? t('common.name.placeholder')"
        :maxlength="props.maxlength"
        @keydown="handleKeydown"
        show-word-limit
        clearable
      />
      <!-- 创建 -->
      <el-button type="primary" :loading="props.loading" :disabled="createDisabled" @click="handleCreate">{{ t('common.actions.create') }}</el-button>
      <!-- 取消创建 -->
      <el-button plain :disabled="props.loading" @click="handleCancel">{{ t('common.actions.cancel') }}</el-button>
    </div>
    <!-- 展开快速创建 -->
    <el-button v-else ref="triggerRef" type="primary" link @click="handleShowCreateInput">
      <MkIcon name="icon_add_outlined" />
      <span>{{ props.text ?? t('common.actions.quickCreate') }}</span>
    </el-button>
  </div>
</template>
