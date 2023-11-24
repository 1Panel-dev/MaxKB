<template>
  <el-dialog title="添加关联数据集" v-model="dialogVisible" width="600">
    <el-checkbox-group v-model="checkList" class="app-custom-checkbox-group">
      <el-row :gutter="12">
        <el-col :span="12">
          <el-card shadow="hover">
            <div class="title flex-between">
              <div class="flex align-center">
                <AppAvatar class="mr-12" shape="square" :size="32">
                  <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                </AppAvatar>
                <h4 class="ellipsis-1">数据集</h4>
              </div>
              <el-checkbox label="Option A" />
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

const emit = defineEmits(['updateContent'])

const dialogVisible = ref<boolean>(false)
const checkList = ref([])

const paragraphFormRef = ref()

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
  }
})

const open = (data: any) => {
  dialogVisible.value = true
}
const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    emit('updateContent', paragraphFormRef.value?.form)
    dialogVisible.value = false
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
