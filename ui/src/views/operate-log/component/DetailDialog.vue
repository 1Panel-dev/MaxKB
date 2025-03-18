<template>
  <el-dialog
    :title="$t('views.operateLog.table.opt.label')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-scrollbar height="400" class="details">
      <div class="content">{{ details }}</div>
    </el-scrollbar>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">
          {{ $t('views.operateLog.close') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const dialogVisible = ref<boolean>(false)
const details = ref<string>()

const open = (data: any) => {
  details.value = JSON.stringify(data.details, null, 4)
  dialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.details {
  margin: 0 10px 30px;
  border: 1px #cccccc solid;
  .content {
    padding: 10px 20px;
    white-space: pre-wrap;
  }
}
</style>
