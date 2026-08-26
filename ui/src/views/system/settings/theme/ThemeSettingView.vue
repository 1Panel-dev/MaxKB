<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import type { ThemeInfo } from '@/api/admin/auth/types'
import ThemeSettingApi from '@/api/admin/system/theme-setting'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import {
  DEFAULT_PLATFORM_SETTING,
  DEFAULT_THEME_COLOR,
  DEFAULT_THEME_SETTING,
  THEME_OPTIONS,
} from '@/constants/theme'
import { useStore } from '@/stores'
import { MsgError } from '@/utils/message'
import LoginPreview from './LoginPreview.vue'

type ThemeImageField = 'icon' | 'loginImage' | 'loginLogo'
type ThemeImageValue = File | string

interface ThemeSettingForm {
  forumUrl: string
  icon: ThemeImageValue
  loginImage: ThemeImageValue
  loginLogo: ThemeImageValue
  projectUrl: string
  showForum: boolean
  showProject: boolean
  showUserManual: boolean
  slogan: string
  theme: string
  title: string
  userManualUrl: string
}

const MAX_IMAGE_SIZE = 10 * 1024 * 1024
const IMAGE_TYPES = ['image/gif', 'image/jpeg', 'image/png']
const DEFAULT_THEME_SETTING_FORM: ThemeSettingForm = {
  ...DEFAULT_THEME_SETTING,
  ...DEFAULT_PLATFORM_SETTING,
}

const { theme } = useStore()
const themeFormRef = useTemplateRef<FormInstance>('themeFormRef')
const loading = ref(false)
const savedThemeSetting = ref<ThemeSettingForm>({ ...DEFAULT_THEME_SETTING_FORM })
const themeSetting = reactive<ThemeSettingForm>({ ...DEFAULT_THEME_SETTING_FORM })
const selectedTheme = ref(DEFAULT_THEME_COLOR)
const customThemeColor = ref(DEFAULT_THEME_COLOR)
const formRules: FormRules<ThemeSettingForm> = {
  slogan: [{ required: true, message: '请输入网站欢迎语', trigger: 'blur' }],
  title: [{ required: true, message: '请输入网站名称', trigger: 'blur' }],
}

const isCustomTheme = computed(() => selectedTheme.value === 'custom')

function toThemeInfo(setting: ThemeSettingForm): ThemeInfo {
  return {
    ...setting,
    icon: typeof setting.icon === 'string' ? setting.icon : undefined,
    loginImage: typeof setting.loginImage === 'string' ? setting.loginImage : undefined,
    loginLogo: typeof setting.loginLogo === 'string' ? setting.loginLogo : undefined,
  }
}

function syncThemeSelection(themeColor: string) {
  const normalizedThemeColor = themeColor.trim().toLowerCase()
  const presetTheme = THEME_OPTIONS.find((option) => option.value === normalizedThemeColor)
  selectedTheme.value = presetTheme?.value ?? 'custom'
  customThemeColor.value = themeColor
}

function applyThemeSetting(setting: ThemeSettingForm, saveSnapshot = false) {
  Object.assign(themeSetting, setting)
  syncThemeSelection(setting.theme)
  theme.setTheme(toThemeInfo(setting))
  if (saveSnapshot) savedThemeSetting.value = { ...setting }
}

/* 主题加载与保存 */

function createThemeFormData() {
  const formData = new FormData()
  Object.entries(themeSetting).forEach(([field, value]) => {
    formData.append(field, value instanceof File ? value : String(value))
  })
  return formData
}

function handleSaveTheme() {
  themeFormRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    ThemeSettingApi.putThemeSetting(createThemeFormData())

      .finally(() => {
        loading.value = false
      })
  })
}

/* 实时预览与恢复 */
function handleThemeChange(value: string | number | boolean | undefined) {
  if (typeof value !== 'string' || value === 'custom') return
  themeSetting.theme = value
  customThemeColor.value = value
  theme.setTheme(toThemeInfo(themeSetting))
}

function handleCustomColorChange(value: string | null) {
  if (!value) return
  themeSetting.theme = value
  theme.setTheme(toThemeInfo(themeSetting))
}

function handleAbandonChanges() {
  applyThemeSetting({ ...savedThemeSetting.value })
  themeFormRef.value?.clearValidate()
}

function handleRestoreLoginDefaults() {
  Object.assign(themeSetting, {
    icon: DEFAULT_THEME_SETTING.icon,
    loginImage: DEFAULT_THEME_SETTING.loginImage,
    loginLogo: DEFAULT_THEME_SETTING.loginLogo,
    slogan: DEFAULT_THEME_SETTING.slogan,
    title: DEFAULT_THEME_SETTING.title,
  })
}

function handleRestorePlatformDefaults() {
  Object.assign(themeSetting, DEFAULT_PLATFORM_SETTING)
}

/* 图片上传 */
function handleImageChange(file: UploadFile, field: ThemeImageField) {
  if (!file.raw) return
  if (!IMAGE_TYPES.includes(file.raw.type)) {
    MsgError('仅支持 JPG、PNG 或 GIF 格式的图片')
    return
  }
  if (file.raw.size > MAX_IMAGE_SIZE) {
    MsgError('图片大小不能超过 10 MB')
    return
  }
  themeSetting[field] = file.raw
}

function handleIconChange(file: UploadFile) {
  handleImageChange(file, 'icon')
}

function handleLoginLogoChange(file: UploadFile) {
  handleImageChange(file, 'loginLogo')
}

function handleLoginImageChange(file: UploadFile) {
  handleImageChange(file, 'loginImage')
}
</script>

<template>
  <MkViewLayout class="system-settings-theme" title="外观设置" :loading="loading">
    <section class="theme-section rounded-md border p-4">
      <h5 class="mb-4">平台主题色</h5>
      <el-radio-group v-model="selectedTheme" @change="handleThemeChange">
        <el-radio-button
          v-for="themeOption in THEME_OPTIONS"
          :key="themeOption.value"
          :label="themeOption.label"
          :value="themeOption.value"
        >
          <span class="inline-flex items-center gap-2">
            <span class="theme-color-dot" :style="{ backgroundColor: themeOption.value }"></span>
            {{ themeOption.label }}
          </span>
        </el-radio-button>
        <el-radio-button label="自定义" value="custom" />
      </el-radio-group>
      <div v-if="isCustomTheme" class="mt-4 flex items-center gap-3">
        <span>自定义颜色</span>
        <el-color-picker v-model="customThemeColor" @change="handleCustomColorChange" />
        <span class="text-N600">{{ customThemeColor }}</span>
      </div>
    </section>

    <section class="theme-section mt-4 rounded-md border p-4">
      <div class="flex-between mb-4">
        <h5>平台登录设置</h5>
        <el-button link type="primary" @click="handleRestoreLoginDefaults">恢复默认</el-button>
      </div>

      <div class="theme-setting-grid grid gap-4">
        <LoginPreview :data="themeSetting" />

        <div>
          <div class="image-setting-card mb-3 rounded-md border p-3">
            <div class="flex-between mb-2">
              <span>网站图标</span>
              <el-upload
                action="#"
                accept="image/jpeg,image/png,image/gif"
                :auto-upload="false"
                :on-change="handleIconChange"
                :show-file-list="false"
              >
                <el-button>替换图片</el-button>
              </el-upload>
            </div>
            <p class="text-N600">建议使用透明背景的方形图片，文件不超过 10 MB。</p>
          </div>

          <div class="image-setting-card mb-3 rounded-md border p-3">
            <div class="flex-between mb-2">
              <span>登录页 Logo</span>
              <el-upload
                action="#"
                accept="image/jpeg,image/png,image/gif"
                :auto-upload="false"
                :on-change="handleLoginLogoChange"
                :show-file-list="false"
              >
                <el-button>替换图片</el-button>
              </el-upload>
            </div>
            <p class="text-N600">建议使用透明背景的横版 Logo，文件不超过 10 MB。</p>
          </div>

          <div class="image-setting-card mb-4 rounded-md border p-3">
            <div class="flex-between mb-2">
              <span>登录页背景</span>
              <el-upload
                action="#"
                accept="image/jpeg,image/png,image/gif"
                :auto-upload="false"
                :on-change="handleLoginImageChange"
                :show-file-list="false"
              >
                <el-button>替换图片</el-button>
              </el-upload>
            </div>
            <p class="text-N600">建议使用 1920 × 1080 图片，文件不超过 10 MB。</p>
          </div>

          <el-form
            ref="themeFormRef"
            :model="themeSetting"
            :rules="formRules"
            label-position="top"
            require-asterisk-position="right"
          >
            <el-form-item label="网站名称" prop="title">
              <el-input
                v-model="themeSetting.title"
                maxlength="128"
                placeholder="请输入网站名称"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="网站欢迎语" prop="slogan">
              <el-input
                v-model="themeSetting.slogan"
                maxlength="64"
                placeholder="请输入网站欢迎语"
                show-word-limit
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </section>

    <section class="theme-section mt-4 rounded-md border p-4">
      <div class="flex-between mb-4">
        <h5>平台入口设置</h5>
        <el-button link type="primary" @click="handleRestorePlatformDefaults">恢复默认</el-button>
      </div>

      <div class="theme-setting-grid grid gap-4">
        <div class="platform-preview overflow-hidden rounded-md border">
          <header class="flex-between border-b px-5 py-3">
            <LogoFull class="h-8" />
            <div class="flex items-center gap-4 text-N600">
              <span v-if="themeSetting.showProject" class="flex items-center gap-1">
                <MkIcon name="icon_launch_outlined" />项目地址
              </span>
              <span v-if="themeSetting.showUserManual" class="flex items-center gap-1">
                <MkIcon name="icon_book_outlined" />用户手册
              </span>
              <span v-if="themeSetting.showForum" class="flex items-center gap-1">
                <MkIcon name="icon_info_outlined" />问题反馈
              </span>
            </div>
          </header>
          <div class="platform-preview-content flex-col-center text-N600">
            <MkIcon name="icon_home_outlined" :size="40" />
            <span class="mt-2">平台首页预览</span>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <el-checkbox v-model="themeSetting.showUserManual" label="显示用户手册" />
            <el-input
              v-model="themeSetting.userManualUrl"
              class="mt-2"
              :disabled="!themeSetting.showUserManual"
              maxlength="128"
              placeholder="请输入用户手册地址"
              show-word-limit
            />
          </div>
          <div>
            <el-checkbox v-model="themeSetting.showForum" label="显示问题反馈" />
            <el-input
              v-model="themeSetting.forumUrl"
              class="mt-2"
              :disabled="!themeSetting.showForum"
              maxlength="128"
              placeholder="请输入问题反馈地址"
              show-word-limit
            />
          </div>
          <div>
            <el-checkbox v-model="themeSetting.showProject" label="显示项目地址" />
            <el-input
              v-model="themeSetting.projectUrl"
              class="mt-2"
              :disabled="!themeSetting.showProject"
              maxlength="128"
              placeholder="请输入项目地址"
              show-word-limit
            />
          </div>
        </div>
      </div>
    </section>

    <footer
      class="theme-actions sticky bottom-0 -mx-6 mt-4 flex justify-end gap-3 border-t px-6 py-4"
    >
      <el-button @click="handleAbandonChanges">放弃更新</el-button>
      <el-button type="primary" @click="handleSaveTheme"> 保存并应用 </el-button>
    </footer>
  </MkViewLayout>
</template>

<style scoped lang="scss">
.image-setting-card {
  min-height: 88px;
}

.platform-preview-content {
  background: var(--mk-N100);
  min-height: 244px;
}

.theme-actions {
  background: var(--el-bg-color);
  z-index: 3;
}

.theme-color-dot {
  border-radius: 50%;
  height: 12px;
  width: 12px;
}

.theme-setting-grid {
  grid-template-columns: minmax(520px, 2fr) minmax(300px, 1fr);
}

@media (max-width: 1120px) {
  .theme-setting-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
