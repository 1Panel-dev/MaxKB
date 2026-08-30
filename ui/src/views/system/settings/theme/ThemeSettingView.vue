<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, useTemplateRef } from 'vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import type { ThemeInfo } from '@/api/admin/auth/types'
import ThemeSettingApi from '@/api/admin/system/settings/theme-setting'
import { DEFAULT_PLATFORM_SETTING, DEFAULT_THEME_SETTING, THEME_OPTIONS } from '@/constants/theme'
import { useStore } from '@/stores'
import { MsgError, MsgSuccess } from '@/utils/message'
import LoginPreview from './components/LoginPreview.vue'
import PlatformPreview from './components/PlatformPreview.vue'

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

interface SyncThemeSettingOptions {
  applyRuntimeTheme?: boolean
  saveSnapshot?: boolean
}

const MAX_IMAGE_SIZE = 10 * 1024 * 1024
const IMAGE_TYPES = ['image/gif', 'image/jpeg', 'image/png']
const THEME_IMAGE_SETTINGS: ThemeImageSetting[] = [
  { description: '顶部网站显示 Logo，建议尺寸 48*48，支持 JPG、PNG、GIF，大小不超过 10MB', field: 'icon', label: '网站 Logo' },
  { description: '登录页面左侧 Logo，建议尺寸 126*32，支持 JPG、PNG、GIF，大小不超过 10 MB', field: 'loginLogo', label: '登录 Logo' },
  {
    description: '左侧背景图，矢量图建议尺寸 1728*1117，位图建议尺寸 3456*2234；支持 JPG、PNG、GIF，大小不超过 10 MB',
    field: 'loginImage',
    label: '登录背景图',
  },
]

const { theme } = useStore()
const initialThemeSetting = toThemeSettingForm(theme.themeInfo)
const normalizedInitialThemeColor = initialThemeSetting.theme.trim().toLowerCase()
const themeFormRef = useTemplateRef<FormInstance>('themeFormRef')
const loading = ref(false)
const savedThemeSetting = ref<ThemeSettingForm>({ ...initialThemeSetting })
const themeSetting = reactive<ThemeSettingForm>({ ...initialThemeSetting })
const selectedTheme = ref(THEME_OPTIONS.some((option) => option.value === normalizedInitialThemeColor) ? normalizedInitialThemeColor : 'custom')
const customThemeColor = ref(initialThemeSetting.theme)
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

function syncThemeSetting(setting: ThemeSettingForm, { applyRuntimeTheme = false, saveSnapshot = false }: SyncThemeSettingOptions = {}) {
  const normalizedThemeColor = setting.theme.trim().toLowerCase()
  Object.assign(themeSetting, setting)
  selectedTheme.value = THEME_OPTIONS.some((option) => option.value === normalizedThemeColor) ? normalizedThemeColor : 'custom'
  customThemeColor.value = setting.theme
  if (applyRuntimeTheme) theme.setTheme(toThemeInfo(setting))
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
        syncThemeSetting(toThemeSettingForm(setting), { saveSnapshot: true })
        MsgSuccess('保存成功')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

/* 实时预览与恢复 */
function handleThemeColorChange(value: string | number | boolean | null | undefined) {
  if (typeof value !== 'string' || value === 'custom') return
  themeSetting.theme = value
  customThemeColor.value = value
  theme.setTheme(toThemeInfo(themeSetting))
}

function handleAbandonChanges() {
  syncThemeSetting({ ...savedThemeSetting.value }, { applyRuntimeTheme: true })
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
function handleUploadImage(field: ThemeImageField) {
  return (file: UploadFile) => {
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
}

onBeforeUnmount(() => theme.setTheme(toThemeInfo(savedThemeSetting.value)))
</script>

<template>
  <MkViewLayout class="system-settings-theme" :loading="loading" title="">
    <template #default="{ Footer }">
      <div class="space-y-4">
        <h6 class="mt-6">平台主题色</h6>
        <el-radio-group v-model="selectedTheme" @change="handleThemeColorChange">
          <el-radio-button v-for="themeOption in THEME_OPTIONS" :key="themeOption.value" :label="themeOption.label" :value="themeOption.value">
            {{ themeOption.label }}
          </el-radio-button>
          <el-radio-button label="自定义" value="custom" />
        </el-radio-group>
        <div v-if="isCustomTheme" class="flex items-center gap-3">
          <span>自定义颜色</span>
          <el-color-picker v-model="customThemeColor" @change="handleThemeColorChange" />
        </div>
        <el-divider class="mb-4!" />
        <div class="flex-between">
          <h6>平台登录设置</h6>

          <el-button text type="primary" class="-mt-1 -mr-1" @click="handleRestoreLoginDefaults">恢复默认</el-button>
        </div>

        <div class="theme-setting-grid grid gap-6">
          <LoginPreview :data="themeSetting" />

          <div class="space-y-2">
            <el-card v-for="imageSetting in THEME_IMAGE_SETTINGS" :key="imageSetting.field" class="small" shadow="never">
              <div class="flex-between mb-2">
                <span>{{ imageSetting.label }}</span>
                <el-upload
                  action="#"
                  accept="image/jpeg,image/png,image/gif"
                  :auto-upload="false"
                  :on-change="handleUploadImage(imageSetting.field)"
                  :show-file-list="false"
                >
                  <el-button plain class="shrink-0 min-w-8! w-8!">
                    <MkIcon name="icon_upload_outlined" />
                  </el-button>
                </el-upload>
              </div>
              <p class="text-N600">{{ imageSetting.description }}</p>
            </el-card>
            <el-form ref="themeFormRef" :model="themeSetting" :rules="formRules" label-position="top" require-asterisk-position="right">
              <el-form-item label="网站名称" prop="title">
                <el-input v-model="themeSetting.title" maxlength="128" placeholder="请输入网站名称" show-word-limit />
              </el-form-item>
              <el-form-item label="欢迎语" prop="slogan">
                <el-input v-model="themeSetting.slogan" maxlength="64" placeholder="请输入网站欢迎语" show-word-limit />
              </el-form-item>
            </el-form>
          </div>
          <span>预览页默认为 MaxKB 登录界面，支持自定义设置</span>
        </div>

        <el-divider class="mb-4!" />
        <div class="flex-between">
          <h6>平台设置</h6>
          <el-button text type="primary" class="-mt-1 -mr-1" @click="handleRestorePlatformDefaults">恢复默认</el-button>
        </div>

        <div class="theme-setting-grid grid gap-6">
          <PlatformPreview :data="themeSetting" />

          <div class="flex flex-col gap-3">
            <el-checkbox v-model="themeSetting.showUserManual" label="用户手册" />
            <div class="ml-6">
              <el-input
                v-if="themeSetting.showUserManual"
                v-model="themeSetting.userManualUrl"
                maxlength="128"
                placeholder="请输入用户手册地址"
                show-word-limit
              />
            </div>

            <el-checkbox v-model="themeSetting.showForum" label="论坛求助" />
            <div class="ml-6">
              <el-input
                v-if="themeSetting.showForum"
                v-model="themeSetting.forumUrl"
                maxlength="128"
                placeholder="请输入论坛求助地址"
                show-word-limit
              />
            </div>

            <el-checkbox v-model="themeSetting.showProject" label="项目地址" />
            <div class="ml-6">
              <el-input
                v-if="themeSetting.showProject"
                v-model="themeSetting.projectUrl"
                maxlength="128"
                placeholder="请输入项目地址"
                show-word-limit
              />
            </div>
          </div>
          <span>预览页默认为 MaxKB 平台界面，支持自定义设置</span>
        </div>
      </div>

      <component :is="Footer">
        <el-button @click="handleAbandonChanges">放弃更新</el-button>
        <el-button type="primary" @click="handleSaveTheme">保存并应用</el-button>
      </component>
    </template>
  </MkViewLayout>
</template>

<style scoped lang="scss">
.theme-setting-grid {
  grid-template-columns: minmax(520px, 2fr) minmax(300px, 1fr);
}

@media (max-width: 1120px) {
  .theme-setting-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
