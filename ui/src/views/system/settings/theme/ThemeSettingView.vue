<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import type { ThemeInfo } from '@/api/admin/auth/types'
import ThemeSettingApi from '@/api/admin/system/settings/theme-setting'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import { DEFAULT_PLATFORM_SETTING, DEFAULT_THEME_COLOR, DEFAULT_THEME_SETTING, THEME_OPTIONS } from '@/constants/theme'
import { useStore } from '@/stores'
import { MsgError, MsgSuccess } from '@/utils/message'
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

interface ThemeImageSetting {
  description: string
  field: ThemeImageField
  label: string
}

const MAX_IMAGE_SIZE = 10 * 1024 * 1024
const IMAGE_TYPES = ['image/gif', 'image/jpeg', 'image/png']
const DEFAULT_THEME_SETTING_FORM: ThemeSettingForm = { ...DEFAULT_THEME_SETTING, ...DEFAULT_PLATFORM_SETTING }
const THEME_IMAGE_SETTINGS: ThemeImageSetting[] = [
  { description: '建议使用透明背景的方形图片，文件不超过 10 MB。', field: 'icon', label: '网站图标' },
  { description: '建议使用透明背景的横版 Logo，文件不超过 10 MB。', field: 'loginLogo', label: '登录页 Logo' },
  { description: '建议使用 1920 × 1080 图片，文件不超过 10 MB。', field: 'loginImage', label: '登录页插图' },
]

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

function toThemeSettingForm(setting?: ThemeInfo | null): ThemeSettingForm {
  return {
    forumUrl: setting?.forumUrl ?? DEFAULT_PLATFORM_SETTING.forumUrl,
    icon: setting?.icon ?? DEFAULT_THEME_SETTING.icon,
    loginImage: setting?.loginImage ?? DEFAULT_THEME_SETTING.loginImage,
    loginLogo: setting?.loginLogo ?? DEFAULT_THEME_SETTING.loginLogo,
    projectUrl: setting?.projectUrl ?? DEFAULT_PLATFORM_SETTING.projectUrl,
    showForum: setting?.showForum ?? DEFAULT_PLATFORM_SETTING.showForum,
    showProject: setting?.showProject ?? DEFAULT_PLATFORM_SETTING.showProject,
    showUserManual: setting?.showUserManual ?? DEFAULT_PLATFORM_SETTING.showUserManual,
    slogan: setting?.slogan ?? DEFAULT_THEME_SETTING.slogan,
    theme: setting?.theme ?? DEFAULT_THEME_SETTING.theme,
    title: setting?.title ?? DEFAULT_THEME_SETTING.title,
    userManualUrl: setting?.userManualUrl ?? DEFAULT_PLATFORM_SETTING.userManualUrl,
  }
}

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
      .then(() => theme.loadThemeInfo())
      .then((setting) => {
        applyThemeSetting(toThemeSettingForm(setting), true)
        MsgSuccess('保存成功')
      })
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
  theme.setTheme(toThemeInfo(themeSetting))
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

function createImageChangeHandler(field: ThemeImageField) {
  return (file: UploadFile) => handleImageChange(file, field)
}

onMounted(() => applyThemeSetting(toThemeSettingForm(theme.themeInfo), true))

onBeforeUnmount(() => theme.setTheme(toThemeInfo(savedThemeSetting.value)))
</script>

<template>
  <MkViewLayout class="system-settings-theme" :loading="loading">
    <template #default="{ Footer }">
      <div class="mx-auto w-full max-w-360 space-y-4">
        <section class="rounded-md border p-6">
          <div class="mb-5">
            <h5>平台主题色</h5>
            <p class="mt-1 text-N600">主题色会同步应用到管理端的按钮、链接和选中状态。</p>
          </div>
          <el-radio-group v-model="selectedTheme" @change="handleThemeChange">
            <el-radio-button v-for="themeOption in THEME_OPTIONS" :key="themeOption.value" :label="themeOption.label" :value="themeOption.value">
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

        <section class="rounded-md border p-6">
          <div class="flex-between mb-5">
            <div>
              <h5>平台登录设置</h5>
              <p class="mt-1 text-N600">配置登录页品牌信息和插图，修改后可在左侧实时预览。</p>
            </div>
            <el-button link type="primary" @click="handleRestoreLoginDefaults">恢复默认</el-button>
          </div>

          <div class="theme-setting-grid grid gap-6">
            <LoginPreview :data="themeSetting" />

            <div>
              <div v-for="imageSetting in THEME_IMAGE_SETTINGS" :key="imageSetting.field" class="image-setting-card mb-3 rounded-md border p-3">
                <div class="flex-between mb-2">
                  <span>{{ imageSetting.label }}</span>
                  <el-upload
                    action="#"
                    accept="image/jpeg,image/png,image/gif"
                    :auto-upload="false"
                    :on-change="createImageChangeHandler(imageSetting.field)"
                    :show-file-list="false"
                  >
                    <el-button>替换图片</el-button>
                  </el-upload>
                </div>
                <p class="text-N600">{{ imageSetting.description }}</p>
              </div>

              <el-form ref="themeFormRef" :model="themeSetting" :rules="formRules" label-position="top" require-asterisk-position="right">
                <el-form-item label="网站名称" prop="title">
                  <el-input v-model="themeSetting.title" maxlength="128" placeholder="请输入网站名称" show-word-limit />
                </el-form-item>
                <el-form-item label="网站欢迎语" prop="slogan">
                  <el-input v-model="themeSetting.slogan" maxlength="64" placeholder="请输入网站欢迎语" show-word-limit />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </section>

        <section class="rounded-md border p-6">
          <div class="flex-between mb-5">
            <div>
              <h5>平台入口设置</h5>
              <p class="mt-1 text-N600">控制平台顶部帮助入口的显示状态和跳转地址。</p>
            </div>
            <el-button link type="primary" @click="handleRestorePlatformDefaults"> 恢复默认 </el-button>
          </div>

          <div class="theme-setting-grid grid gap-6">
            <div class="platform-preview overflow-hidden rounded-md border">
              <header class="flex-between border-b px-5 py-3">
                <LogoFull class="h-8" />
                <div class="flex items-center gap-4 text-N600">
                  <span v-if="themeSetting.showProject" class="flex items-center gap-1"> <MkIcon name="icon_launch_outlined" />项目地址 </span>
                  <span v-if="themeSetting.showUserManual" class="flex items-center gap-1"> <MkIcon name="icon_book_outlined" />用户手册 </span>
                  <span v-if="themeSetting.showForum" class="flex items-center gap-1"> <MkIcon name="icon_info_outlined" />问题反馈 </span>
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
                <el-input v-model="themeSetting.forumUrl" class="mt-2" :disabled="!themeSetting.showForum" maxlength="128" placeholder="请输入问题反馈地址" show-word-limit />
              </div>
              <div>
                <el-checkbox v-model="themeSetting.showProject" label="显示项目地址" />
                <el-input v-model="themeSetting.projectUrl" class="mt-2" :disabled="!themeSetting.showProject" maxlength="128" placeholder="请输入项目地址" show-word-limit />
              </div>
            </div>
          </div>
        </section>
      </div>

      <component :is="Footer">
        <el-button @click="handleAbandonChanges">放弃更新</el-button>
        <el-button type="primary" @click="handleSaveTheme">保存并应用</el-button>
      </component>
    </template>
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
