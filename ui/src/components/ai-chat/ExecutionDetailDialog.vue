<template>
  <el-dialog
    class="execution-details-dialog responsive-dialog"
    :title="$t('chat.executionDetails.title')"
    v-model="dialogVisible"
    destroy-on-close
    append-to-body
    align-center
    @click.stop
  >
   <ExecutionDetailContent :detail="detail" :type="type" />
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { cloneDeep } from 'lodash'
import ExecutionDetailContent from './component/ExecutionDetailContent.vue'

const props = defineProps<{
  type?: string
}>()

const dialogVisible = ref(false)
const detail = ref<any[]>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = []
  }
})

const open = (data: any) => {
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}
onBeforeUnmount(() => {
  dialogVisible.value = false
})
defineExpose({ open })
</script>
<style lang="scss">
.execution-details-dialog {

  .el-dialog__header {
    padding-bottom: 16px;
  }

  .execution-details {
    max-height: calc(100vh - 260px);

    .arrow-icon {
      transition: 0.2s;
    }
  }
}
</style>
