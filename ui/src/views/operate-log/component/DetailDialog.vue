<template>
  <el-dialog
    :title="$t('views.operateLog.table.opt.label')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="border border-r-4 mb-16" style="white-space: pre-wrap; height: 400px">
      <el-scrollbar>
        <div class="p-16">
          {{ details }}
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <span class="dialog-footer mt-16">
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
<style lang="scss" scoped></style>
