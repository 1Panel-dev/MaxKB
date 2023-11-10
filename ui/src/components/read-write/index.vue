<template>
  <div class="cursor">
    <slot name="read">
      <div class="flex align-center" v-if="!isEdit">
        <span>{{ data }}</span>
        <el-button @click.prevent="editNameHandle" text v-if="showEditIcon">
          <el-icon><Edit /></el-icon>
        </el-button>
      </div>
    </slot>
    <slot>
      <div class="flex align-center" v-if="isEdit">
        <el-input ref="inputRef" v-model="writeValue" placeholder="请输入"></el-input>
        <span class="ml-4">
          <el-button type="primary" text @click="submit" :disabled="loading">
            <el-icon><Select /></el-icon>
          </el-button>
        </span>
        <span>
          <el-button text @click="isEdit = false" :disabled="loading">
            <el-icon><CloseBold /></el-icon>
          </el-button>
        </span>
      </div>
    </slot>
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
defineOptions({ name: 'ReadWrite' })
const props = defineProps({
  data: {
    type: String,
    default: ''
  },
  showEditIcon: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['change'])
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
function editNameHandle(row: any) {
  writeValue.value = props.data
  isEdit.value = true
}
</script>
<style lang="scss" scoped></style>
