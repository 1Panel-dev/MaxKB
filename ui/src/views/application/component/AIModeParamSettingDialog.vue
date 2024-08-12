<template>
  <el-dialog
    align-center
    :title="$t('views.application.applicationForm.dialogues.paramSettings')"
    class="aiMode-param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
  >
    <el-form label-position="top" ref="paramFormRef" :model="form">
      <el-form-item>
        <template #label>
          <div class="flex align-center">
            <div class="flex-between mr-4">
              <span>温度</span>
            </div>
            <el-tooltip effect="dark" placement="right">
              <template #content
                >较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定</template
              >
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-slider
          v-model="form.similarity"
          show-input
          :show-input-controls="false"
          :min="0"
          :max="1"
          :precision="2"
          :step="0.01"
          class="custom-slider"
        />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex align-center">
            <div class="flex-between mr-4">
              <span>输出最大Tokens</span>
            </div>
            <el-tooltip effect="dark" placement="right">
              <template #content>指定模型可生成的最大token个数</template>
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-slider
          v-model="form.max_paragraph_char_number"
          show-input
          :show-input-controls="false"
          :min="1"
          :max="10000"
          class="custom-slider"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">{{
          $t('views.application.applicationForm.buttons.cancel')
        }}</el-button>
        <el-button type="primary" @click="submit(paramFormRef)" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'

const emit = defineEmits(['refresh'])

const paramFormRef = ref()

const form = ref<any>({
  similarity: 0.6,
  max_paragraph_char_number: 5000
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      similarity: 0.6,
      max_paragraph_char_number: 5000
    }
  }
})

const open = (data: any) => {
  form.value = cloneDeep(data)

  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      emit('refresh', form.value)
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.aiMode-param-dialog {
  padding: 8px 8px 24px 8px;
  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }
  .el-dialog__body {
    padding: 16px !important;
  }
  .dialog-max-height {
    height: 550px;
  }
  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
