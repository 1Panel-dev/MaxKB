<template>
  <el-dialog
    align-center
    :title="$t('common.setting')"
    class="param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form label-position="top" ref="paramFormRef" :model="form" class="p-12-16">
      <el-text type="info" class="color-secondary">{{
        $t('views.application.applicationForm.form.reasoningContent.tooltip')
      }}</el-text>
      <el-row class="mt-16" :gutter="20">
        <el-col :span="12">
          <el-form-item
            :label="$t('views.application.applicationForm.form.reasoningContent.start')"
          >
            <el-input
              type="textarea"
              v-model="form.reasoning_content_start"
              :rows="6"
              maxlength="50"
              placeholder="<think>"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="$t('views.application.applicationForm.form.reasoningContent.end')">
            <el-input
              type="textarea"
              v-model="form.reasoning_content_end"
              :rows="6"
              maxlength="50"
              placeholder="</think>"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'

const emit = defineEmits(['refresh'])

const form = ref<any>({
  reasoning_content_start: '<think>',
  reasoning_content_end: '</think>'
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)
watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      reasoning_content_start: '<think>',
      reasoning_content_end: '</think>'
    }
  }
})

const open = (data: any) => {
  form.value = { ...form.value, ...data }
  dialogVisible.value = true
}

const submit = () => {
  emit('refresh', form.value)
  dialogVisible.value = false
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
