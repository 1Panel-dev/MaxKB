<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { PortalSetting } from '@/api/types'
import MkEditAvatar from '@/components/mk-edit-avatar/index.vue'
import defaultLogo from '@/assets/mk-logo/logo.svg'

const props = defineProps<{ setting: PortalSetting; saving: boolean; save: (payload: FormData) => Promise<void> }>()

/* 门户名称与 Logo */
const editVisible = ref(false)
const portalFormRef = useTemplateRef<FormInstance>('portalFormRef')
const portalForm = reactive({ name: '', logo: '' })
const logoFile = ref<File | null>(null)
const logoChanged = ref(false)
const portalRules: FormRules = {
  name: [
    { required: true, message: '请输入门户名称', trigger: 'blur' },
    { whitespace: true, message: '门户名称不能为空白', trigger: 'blur' },
  ],
}

function handleOpenPortalEdit() {
  handleClosePortalEdit()
  portalForm.name = props.setting.name
  portalForm.logo = props.setting.logo || ''
  editVisible.value = true
}

function handleLogoChange(_icon: string, file: File | null) {
  logoFile.value = file
  logoChanged.value = true
}

function handleSavePortalInfo() {
  portalFormRef.value?.validate((valid) => {
    if (!valid) return
    const payload = new FormData()
    payload.append('name', portalForm.name.trim())
    if (logoChanged.value) payload.append('logo', logoFile.value || '')
    return props.save(payload).then(() => {
      editVisible.value = false
    })
  })
}

function handleClosePortalEdit() {
  portalForm.name = ''
  portalForm.logo = ''
  logoFile.value = null
  logoChanged.value = false
  portalFormRef.value?.clearValidate()
}
</script>

<template>
  <!-- 编辑门户名称与 Logo -->
  <el-button text :disabled="saving" @click="handleOpenPortalEdit">
    <MkIcon name="icon_edit_outlined" />
  </el-button>
  <MkDialog v-model="editVisible" title="编辑" @closed="handleClosePortalEdit">
    <el-form ref="portalFormRef" :model="portalForm" :rules="portalRules" label-position="top" @submit.prevent>
      <el-form-item label="名称" prop="name">
        <!-- <MkEditAvatar v-model="portalForm.logo" :default-icon="defaultLogo" :size="48" :editable="!saving" @change="handleLogoChange" /> -->
        <el-input v-model="portalForm.name" maxlength="64" show-word-limit :disabled="saving" placeholder="请输入门户名称" />
      </el-form-item>
    </el-form>
    <template #footer>
      <!-- 取消编辑 -->
      <el-button plain :disabled="saving" @click="editVisible = false">取消</el-button>
      <!-- 保存门户信息 -->
      <el-button type="primary" :loading="saving" @click="handleSavePortalInfo">保存</el-button>
    </template>
  </MkDialog>
</template>
