<template>
  <el-dialog title="执行详情" v-model="dialogVisible" destroy-on-close append-to-body align-center>
    <el-scrollbar>
      <div class="paragraph-source-height">
        <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
          <div class="flex-between cursor">
            <div class="flex align-center">
              <el-icon class="mr-8"><CaretRight /></el-icon>
              开始
            </div>
            <div class="flex align-center">
              <span class="mr-16 color-secondary">6.01s</span>
              <el-icon class="success" :size="16"><CircleCheck /></el-icon>
            </div>
          </div>
          <el-collapse-transition>
            <div class="card-never border-r-4 mt-8">
              <div class="p-8-12">参数输入</div>
              <div class="p-8-12 border-t-dashed lighter">如何快速开始</div>
            </div>
          </el-collapse-transition>
        </el-card>
      </div>
    </el-scrollbar>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { cloneDeep } from 'lodash'
import { arraySort } from '@/utils/utils'
import { MdPreview } from 'md-editor-v3'
const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const detail = ref<any>({})

const current = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
  }
})

const open = (data: any, id?: string) => {
  detail.value = cloneDeep(data)

  dialogVisible.value = true
}
onBeforeUnmount(() => {
  dialogVisible.value = false
})
defineExpose({ open })
</script>
<style lang="scss">
.paragraph-source {
  padding: 0;

  .el-dialog__header {
    padding: 24px 24px 0 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .paragraph-source-height {
    max-height: calc(100vh - 260px);
  }
  .paragraph-source-card {
    height: 260px;
  }
}
@media only screen and (max-width: 768px) {
  .paragraph-source {
    width: 90% !important;
    .footer-content {
      display: block;
    }
    .paragraph-source-card {
      height: 285px;
    }
  }
}
</style>
