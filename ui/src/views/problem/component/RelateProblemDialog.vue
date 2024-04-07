<template>
  <el-dialog
    title="关联分段"
    v-model="dialogVisible"
    width="80%"
    class="paragraph-dialog"
    destroy-on-close
  >
    <el-row v-loading="loading">
      <el-col :span="8">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="bold title align-center p-24 pb-0">选择文档</div>
          <div class="p-8" style="padding-bottom: 8px">
            <common-list :data="documentList" class="mt-8" v-loading="loading">
              <template #default="{ row }">
                {{ row.name }}
              </template>
            </common-list>
          </div>
        </el-scrollbar>
      </el-col>
      <el-col :span="16" class="border-l">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="p-24" style="padding-bottom: 8px">
            <div class="flex-between mb-16">
              <div class="bold title align-center">选择分段</div>
            </div>
          </div>
        </el-scrollbar>
        <div class="text-right p-24 pt-0">
          <el-button> 取消 </el-button>
          <el-button type="primary" :disabled="loading"> 保存 </el-button>
        </div>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep, debounce } from 'lodash'

// import paragraphApi from '@/api/paragraph'
import useStore from '@/stores'

const props = defineProps({
  title: String
})
const { application, document } = useStore()

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const emit = defineEmits(['refresh'])

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const documentList = ref([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    documentList.value = []
  }
})

const open = (data: any) => {
  getDocument()
  dialogVisible.value = true
}
function getDocument() {
  document.asyncGetAllDocument(id, loading).then((res: any) => {
    documentList.value = res.data
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.paragraph-dialog {
  padding: 0 !important;
  .el-scrollbar {
    height: auto !important;
  }
  .el-dialog__header {
    padding: 16px 24px;
  }
  .el-dialog__body {
    border-top: 1px solid var(--el-border-color);
  }
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid var(--el-border-color);
  }

  .title {
    color: var(--app-text-color);
  }
}
</style>
