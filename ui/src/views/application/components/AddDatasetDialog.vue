<template>
  <el-dialog title="添加关联数据集" v-model="dialogVisible" width="600">
    <CardCheckbox value-field="id" :data-list="data" v-model="checkList">
      <template #default="scope">
        <div class="title flex-between">
          <div class="flex align-center">
            <AppAvatar class="mr-12" shape="square" :size="32">
              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
            </AppAvatar>
            <h4 class="ellipsis-1">{{ scope.name }}</h4>
          </div>
          <input type="checkbox" id="check1" :checked="scope.checked" />
        </div>
      </template>
    </CardCheckbox>

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
import CardCheckbox from '@/components/card-checkbox/index.vue'
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
