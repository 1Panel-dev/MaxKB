<template>
  <el-dialog
    :title="$t('views.application.applicationForm.title.create')"
    v-model="dialogVisible"
    width="600"
    append-to-body
  >
    <el-form
      ref="applicationFormRef"
      :model="applicationForm"
      :rules="rules"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item :label="$t('views.application.applicationForm.form.appName.label')" prop="name">
        <el-input
          v-model="applicationForm.name"
          maxlength="64"
          :placeholder="$t('views.application.applicationForm.form.appName.placeholder')"
          show-word-limit
        />
      </el-form-item>
      <el-form-item :label="$t('views.application.applicationForm.form.appDescription.label')">
        <el-input
          v-model="applicationForm.desc"
          type="textarea"
          :placeholder="$t('views.application.applicationForm.form.appDescription.placeholder')"
          :rows="3"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="选择应用类型">
        <el-radio-group v-model="applicationForm.search_mode" class="card__radio">
          <el-card
            shadow="never"
            class="mb-16"
            :class="applicationForm.search_mode === 'embedding' ? 'active' : ''"
          >
            <el-radio value="embedding" size="large">
              <p class="mb-4">简单配置</p>
              <el-text type="info">适合新手创建小助手</el-text>
            </el-radio>
          </el-card>
          <el-card
            shadow="never"
            class="mb-16"
            :class="applicationForm.search_mode === 'keywords' ? 'active' : ''"
          >
            <el-radio value="keywords" size="large">
              <p class="mb-4">高级编排</p>
              <el-text type="info">适合高级用户自定义小助手的工作流</el-text>
            </el-radio>
          </el-card>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">
          {{ $t('views.application.applicationForm.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle">
          {{ $t('views.application.applicationForm.buttons.create') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ApplicationFormType } from '@/api/type/application'

const dialogVisible = ref<boolean>(false)

const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: ''
})
watch(dialogVisible, (bool) => {
  if (!bool) {
  }
})

const open = () => {
  dialogVisible.value = true
}
const submitHandle = () => {
  dialogVisible.value = false
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
