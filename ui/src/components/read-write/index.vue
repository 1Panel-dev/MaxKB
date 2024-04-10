<template>
  <div class="cursor w-full">
    <slot name="read">
      <div class="flex align-center" v-if="!isEdit">
        <auto-tooltip :content="data">
          {{ data }}
        </auto-tooltip>

        <el-button class="ml-4" @click.stop="editNameHandle" text v-if="showEditIcon">
          <el-icon><EditPen /></el-icon>
        </el-button>
      </div>
    </slot>
    <slot>
      <div class="flex align-center" @click.stop v-if="isEdit">
        <div class="w-full">
          <el-input
            ref="inputRef"
            v-model="writeValue"
            placeholder="请输入"
            autofocus
            :maxlength="maxlength || '-'"
            :show-word-limit="maxlength ? true : false"
          ></el-input>
        </div>

        <span class="ml-4">
          <el-button type="primary" text @click.stop="submit" :disabled="loading">
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
    default: ''
  },
  showEditIcon: {
    type: Boolean,
    default: false
  },
  maxlength: {
    type: Number,
    default: () => 0
  }
})
const emit = defineEmits(['change'])
const inputRef = ref()
const isEdit = ref(false)
const writeValue = ref('')
const loading = ref(false)

watch(isEdit, (bool) => {
  if (!bool) {
    writeValue.value = ''
  }
})

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

onMounted(() => {
  nextTick(() => {
    inputRef.value?.focus()
  })
})
</script>
<style lang="scss" scoped></style>
