<template>
  <el-dialog title="添加关联数据集" v-model="dialogVisible" width="600">
    <el-checkbox-group v-model="checkList" class="app-custom-checkbox-group">
      <el-row :gutter="12" v-loading="loading">
        <el-col :span="12" v-for="(item, index) in data" :key="index" class="mb-16">
          <el-card shadow="hover">
            <div class="title flex-between">
              <div class="flex align-center">
                <AppAvatar class="mr-12" shape="square" :size="32">
                  <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                </AppAvatar>
                <h4 class="ellipsis-1">{{ item.name }}</h4>
              </div>
              <el-checkbox :label="item.id" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-checkbox-group>
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
  }
})

const emit = defineEmits(['addData'])

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const checkList = ref([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
    loading.value = false
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

defineExpose({ open })
</script>
<style lang="scss" scope></style>
