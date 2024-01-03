<template>
  <el-dialog title="添加关联知识库" v-model="dialogVisible" width="600">
    <template #header="{ titleId, titleClass }">
      <div class="my-header flex">
        <h4 :id="titleId" :class="titleClass">添加关联知识库</h4>
        <el-button link class="ml-16" @click="refresh">
          <el-icon class="mr-4"><Refresh /></el-icon>刷新
        </el-button>
      </div>
    </template>
    <el-row :gutter="12" v-loading="loading">
      <el-col :span="12" v-for="(item, index) in data" :key="index" class="mb-16">
        <CardCheckbox value-field="id" :data="item" v-model="checkList">
          <span class="ellipsis">
            {{ item.name }}
          </span>
        </CardCheckbox>
      </el-col>
    </el-row>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitHandle"> 确认 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  },
  loading: Boolean
})

const emit = defineEmits(['addData', 'refresh'])

const dialogVisible = ref<boolean>(false)
const checkList = ref([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
  }
})

const open = (checked: any) => {
  checkList.value = checked
  dialogVisible.value = true
}
const submitHandle = () => {
  emit('addData', checkList.value)
  dialogVisible.value = false
}

const refresh = () => {
  emit('refresh')
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
