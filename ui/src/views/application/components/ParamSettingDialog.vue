<template>
  <el-dialog title="参数设置" class="param-dialog" v-model="dialogVisible" style="width: 550px">
    <div class="dialog-max-height">
      <el-scrollbar>
        <div class="p-16">
          <el-form label-position="top" ref="paramFormRef" :model="form">
            <el-form-item label="检索模式">
              <el-radio-group v-model="form.search_mode" class="card__radio">
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="form.search_mode === 'embedding' ? 'active' : ''"
                >
                  <el-radio value="embedding" size="large">
                    <p class="mb-4">向量检索</p>
                    <el-text type="info">通过向量距离计算与用户问题最相似的文本分段</el-text>
                  </el-radio>
                </el-card>
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="form.search_mode === 'keywords' ? 'active' : ''"
                >
                  <el-radio value="keywords" size="large">
                    <p class="mb-4">全文检索</p>
                    <el-text type="info">通过关键词检索，返回包含关键词最多的文本分段</el-text>
                  </el-radio>
                </el-card>
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="form.search_mode === 'blend' ? 'active' : ''"
                >
                  <el-radio value="blend" size="large">
                    <p class="mb-4">混合检索</p>
                    <el-text type="info"
                      >同时执行全文检索和向量检索，再进行重排序，从两类查询结果中选择匹配用户问题的最佳结果</el-text
                    >
                  </el-radio>
                </el-card>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <template #label>
                <div class="flex align-center">
                  <span class="mr-4">相似度高于</span>
                  <el-tooltip effect="dark" content="相似度越高相关性越强。" placement="right">
                    <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                  </el-tooltip>
                </div>
              </template>
              <el-input-number
                v-model="form.similarity"
                :min="0"
                :max="1"
                :precision="3"
                :step="0.1"
                controls-position="right"
              />
            </el-form-item>
            <el-form-item label="引用分段数 TOP">
              <el-input-number v-model="form.top_n" :min="1" :max="10" controls-position="right" />
            </el-form-item>
            <el-form-item label="最多引用字符数">
              <el-slider
                v-model="form.max_paragraph_char_number"
                show-input
                :show-input-controls="false"
                :min="500"
                :max="10000"
                class="custom-slider"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(paramFormRef)" :loading="loading">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

import type { FormInstance, FormRules } from 'element-plus'

const emit = defineEmits(['refresh'])

const paramFormRef = ref()
const form = ref<any>({
  search_mode: 'embedding',
  top_n: 3,
  similarity: 0.6,
  max_paragraph_char_number: 5000
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      search_mode: 'embedding',
      top_n: 3,
      similarity: 0.6,
      max_paragraph_char_number: 5000
    }
  }
})

const open = (data: any) => {
  form.value = { ...form.value, ...data }
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
.param-dialog {
  padding: 8px;
  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }
  .el-dialog__body {
    padding: 0 !important;
  }
  .dialog-max-height {
    height: calc(100vh - 260px);
  }
  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
