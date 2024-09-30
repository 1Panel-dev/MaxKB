<template>
  <el-dialog
    align-center
    :title="$t('views.application.applicationForm.dialogues.paramSettings')"
    class="param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div>
      <el-scrollbar always>
        <div class="p-16">
          <el-form label-position="top" ref="paramFormRef" :model="form">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item>
                  <template #label>
                    <div class="flex align-center">
                      <span class="mr-4">Score 高于</span>
                      <el-tooltip effect="dark" content="Score越高相关性越强。" placement="right">
                        <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                      </el-tooltip>
                    </div>
                  </template>
                  <el-input-number
                    v-model="form.similarity"
                    :min="0"
                    :max="form.search_mode === 'blend' ? 2 : 1"
                    :precision="3"
                    :step="0.1"
                    :value-on-clear="0"
                    controls-position="right"
                    class="w-full"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item
                  :label="$t('views.application.applicationForm.dialogues.topReferences')"
                >
                  <el-input-number
                    v-model="form.top_n"
                    :min="1"
                    :max="100"
                    :value-on-clear="1"
                    controls-position="right"
                    class="w-full"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item :label="$t('views.application.applicationForm.dialogues.maxCharacters')">
              <el-slider
                v-model="form.max_paragraph_char_number"
                show-input
                :show-input-controls="false"
                :min="500"
                :max="100000"
                class="custom-slider"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <span class="dialog-footer p-16">
        <el-button @click.prevent="dialogVisible = false">{{
          $t('views.application.applicationForm.buttons.cancel')
        }}</el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('views.application.applicationForm.buttons.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance, FormRules } from 'element-plus'
const emit = defineEmits(['refresh'])

const paramFormRef = ref<FormInstance>()

const form = ref<any>({
  top_n: 3,
  similarity: 0,
  max_paragraph_char_number: 5000
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      top_n: 3,
      similarity: 0,
      max_paragraph_char_number: 5000
    }
  }
})

const open = (data: any) => {
  form.value = { ...form.value, ...cloneDeep(data) }
  dialogVisible.value = true
}

const submit = () => {
  paramFormRef?.value?.validate((valid: boolean, fields: any) => {
    if (valid) {
      emit('refresh', cloneDeep(form.value))
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.param-dialog {
  padding: 8px 8px 24px 8px;
  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }
  .el-dialog__body {
    padding: 0 !important;
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
