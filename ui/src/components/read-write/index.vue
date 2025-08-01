<template>
  <div class="cursor w-full">
    <slot name="read">
      <div class="flex align-center" v-if="!isEdit" @dblclick="dblclick">
        <auto-tooltip :content="data">
          {{ data }}
        </auto-tooltip>

        <el-button
          v-if="trigger === 'default' && showEditIcon"
          class="ml-4"
          @click.stop="editNameHandle"
          text
        >
          <AppIcon iconName="app-edit"></AppIcon>
        </el-button>
      </div>
    </slot>
    <slot>
      <div class="flex align-center" @click.stop v-if="isEdit">
        <div class="w-full">
          <el-input
            ref="inputRef"
            v-model="writeValue"
            :placeholder="$t('common.inputPlaceholder')"
            autofocus
            :maxlength="maxlength || '-'"
            :show-word-limit="maxlength ? true : false"
            @blur="isEdit = false"
            @keyup.enter="submit"
            clearable
          ></el-input>
        </div>

        <span class="ml-4">
          <el-button type="primary" text @mousedown="submit" :disabled="loading">
            <el-icon><Select /></el-icon>
          </el-button>
        </span>
        <span>
          <el-button text @click.stop="isEdit = false" :disabled="loading">
            <el-icon><CloseBold /></el-icon>
          </el-button>
        </span>
      </div>
    </slot>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
defineOptions({ name: 'ReadWrite' })
const props = defineProps({
  data: {
    type: String,
    default: '',
  },
  showEditIcon: {
    type: Boolean,
    default: false,
  },
  maxlength: {
    type: Number,
    default: () => 0,
  },
  trigger: {
    type: String,
    default: 'default',
    validator: (value: string) => ['default', 'dblclick', 'manual'].includes(value),
  },
  write: {
    type: Boolean,
    default: false,
  },
})
const emit = defineEmits(['change', 'close'])
const inputRef = ref()
const isEdit = ref(false)
const writeValue = ref('')
const loading = ref(false)

watch(isEdit, (bool) => {
  if (!bool) {
    writeValue.value = ''
    emit('close')
  } else {
    setTimeout(() => {
      nextTick(() => {
        inputRef.value?.focus()
      })
    }, 200)
  }
})

watch(
  () => props.write,
  (bool) => {
    if (bool && props.trigger === 'manual') {
      editNameHandle()
    } else {
      isEdit.value = false
    }
  },
)

function dblclick() {
  if (props.trigger === 'dblclick') {
    editNameHandle()
  }
}

function submit() {
  loading.value = true
  emit('change', writeValue.value)
  setTimeout(() => {
    isEdit.value = false
    loading.value = false
  }, 200)
}
function editNameHandle() {
  writeValue.value = props.data
  isEdit.value = true
}

onMounted(() => {})
</script>
<style lang="scss" scoped></style>
