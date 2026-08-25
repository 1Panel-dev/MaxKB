<script setup lang="ts">
import { computed, ref } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import LoginLayout from '@/views/login/components/LoginLayout.vue'
import AccountLogin from '@/views/login/modes/AccountLogin.vue'

interface ThemeOption {
  color: string
  label: string
  value: string
}

const themeOptions: ThemeOption[] = [
  { color: '#3370ff', label: '默认', value: 'default' },
  { color: '#ff8b38', label: '活力橙', value: 'orange' },
  { color: '#20bfa9', label: '松石绿', value: 'green' },
  { color: '#7f3bf5', label: '神秘紫', value: 'purple' },
  { color: '#df4d70', label: '胭脂红', value: 'red' },
  { color: '#3370ff', label: '自定义', value: 'custom' },
]

const selectedTheme = ref('default')
const customThemeColor = ref('#3370ff')
const websiteName = ref('MaxKB')
const welcomeText = ref('强大易用的企业级智能体平台')

const platformLinks = ref([
  {
    enabled: true,
    label: '用户手册',
    url: 'https://bbs.fit2cloud.com/c/mk/11',
  },
  {
    enabled: true,
    label: '论坛求助',
    url: 'https://bbs.fit2cloud.com/c/mk/11',
  },
  {
    enabled: true,
    label: '项目地址',
    url: 'https://github.com/1Panel-dev/MaxKB',
  },
])

const currentThemeColor = computed(
  () =>
    (selectedTheme.value === 'custom'
      ? customThemeColor.value
      : themeOptions.find((themeOption) => themeOption.value === selectedTheme.value)?.color) ??
    '#3370ff',
)

const selectTheme = (themeOption: ThemeOption) => {
  selectedTheme.value = themeOption.value
  if (themeOption.value !== 'custom') customThemeColor.value = themeOption.color
}
</script>

<template>
  <div class="appearance-settings flex h-full flex-col">
    <el-scrollbar class="min-h-0 flex-1">
      <div class="p-6">
        <section>
          <h6>平台显示主题</h6>
          <div class="mt-4 flex">
            <div class="theme-selector">
              <button
                v-for="themeOption in themeOptions"
                :key="themeOption.value"
                type="button"
                :class="{ active: selectedTheme === themeOption.value }"
                @click="selectTheme(themeOption)"
              >
                {{ themeOption.label }}
              </button>
            </div>

            <el-color-picker
              v-if="selectedTheme === 'custom'"
              v-model="customThemeColor"
              class="ml-3"
            />
          </div>
        </section>

        <el-divider class="!my-4" />

        <section>
          <div class="flex-between">
            <h6>平台登录设置</h6>
            <button type="button" class="text-primary">恢复默认</button>
          </div>

          <div class="mt-4 grid grid-cols-[minmax(560px,2fr)_minmax(300px,1fr)] gap-4">
            <div>
              <div class="login-preview-frame">
                <div class="preview-browser-bar">
                  <div class="preview-browser-tab">
                    <img src="@/assets/logo/MaxKB-logo.svg" alt="" />
                    <span>{{ websiteName }}</span>
                    <span class="ml-auto text-N500">×</span>
                  </div>
                </div>
                <div class="login-preview-viewport">
                  <LoginLayout
                    preview
                    :theme-color="currentThemeColor"
                    :website-name="websiteName"
                    :welcome-text="welcomeText"
                  >
                    <AccountLogin />
                  </LoginLayout>
                </div>
              </div>
              <p class="mt-2 text-N500">预览页默认为 MaxKB 登录界面，支持自定义设置</p>
            </div>

            <div class="space-y-2">
              <article class="upload-setting-card">
                <div>
                  <h6>网站 Logo</h6>
                  <p>顶部网站显示 Logo，建议尺寸 48×48，支持 JPG、PNG、GIF，大小不超过 10MB</p>
                </div>
                <el-button :icon="Upload" aria-label="上传网站 Logo" />
              </article>

              <article class="upload-setting-card">
                <div>
                  <h6>登录 Logo</h6>
                  <p>登录页面左侧 Logo，建议尺寸 126×32，支持 JPG、PNG、GIF，大小不超过 10MB</p>
                </div>
                <el-button :icon="Upload" aria-label="上传登录 Logo" />
              </article>

              <article class="upload-setting-card">
                <div>
                  <h6>登录背景图</h6>
                  <p>
                    左侧背景图，矢量图建议尺寸 1728×1117，位图建议尺寸 3456×2234；支持
                    JPG、PNG、GIF，大小不超过 10MB
                  </p>
                </div>
                <el-button :icon="Upload" aria-label="上传登录背景图" />
              </article>

              <el-form label-position="top" class="appearance-form">
                <el-form-item label="网站名称" required>
                  <el-input v-model="websiteName" />
                </el-form-item>
                <el-form-item label="欢迎语" required>
                  <el-input v-model="welcomeText" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </section>

        <el-divider class="!my-4" />

        <section>
          <div class="flex-between">
            <h6>平台设置</h6>
            <button type="button" class="text-primary">恢复默认</button>
          </div>

          <div class="mt-4 grid grid-cols-[minmax(560px,2fr)_minmax(300px,1fr)] gap-4">
            <div>
              <div class="platform-preview">
                <img src="@/assets/appearance/platform-preview.png" alt="平台界面预览" />
              </div>
              <p class="mt-2 text-N500">预览页默认为 MaxKB 平台界面，支持自定义设置</p>
            </div>

            <div class="space-y-3">
              <div v-for="platformLink in platformLinks" :key="platformLink.label">
                <el-checkbox v-model="platformLink.enabled">{{ platformLink.label }}</el-checkbox>
                <el-input v-model="platformLink.url" class="mt-2 pl-6" />
              </div>
            </div>
          </div>
        </section>
      </div>
    </el-scrollbar>

    <footer
      class="appearance-actions flex justify-end gap-3 border-t border-N900/15 bg-white px-6 py-4"
    >
      <el-button>放弃更新</el-button>
      <el-button type="primary">保存并应用</el-button>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.theme-selector {
  border: 1px solid var(--mk-N350);
  border-radius: 6px;
  display: flex;
  padding: 3px;

  button {
    border-radius: 4px;
    padding: 2px calc(var(--spacing) * 2);

    &.active {
      // background: rgb(var(--mk-primary-rgb) / 10%);
      // color: var(--mk-primary);
    }
  }
}

.login-preview-frame {
  background: white;
  border: 1px solid var(--mk-N300);
  border-radius: 6px;
  height: 496px;
  overflow: hidden;
}

.preview-browser-bar {
  align-items: end;
  background: var(--mk-N100);
  display: flex;
  height: 32px;
  padding: 0 8px;
}

.preview-browser-tab {
  align-items: center;
  background: white;
  border-radius: 5px 5px 0 0;
  display: flex;
  font-size: 10px;
  gap: 4px;
  height: 27px;
  padding: 0 8px;
  width: 110px;

  img {
    height: 12px;
    object-fit: contain;
    width: 28px;
  }
}

.login-preview-viewport {
  height: 464px;
  overflow: hidden;

  :deep(.login-layout) {
    transform: scale(0.5264);
    transform-origin: left top;
  }
}

.upload-setting-card {
  align-items: flex-start;
  border: 1px solid var(--mk-N300);
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  min-height: 100px;
  padding: 12px;

  p {
    color: var(--mk-N500);
    line-height: 20px;
    margin-top: calc(var(--spacing) * 2);
  }
}

.appearance-form {
  margin-top: 26px;
}

.platform-preview {
  border: 1px solid var(--mk-N300);
  border-radius: 6px;
  height: 226px;
  overflow: hidden;

  img {
    height: 100%;
    object-fit: cover;
    object-position: top;
    width: 100%;
  }
}

.appearance-actions {
  flex-shrink: 0;
}

:deep(.appearance-form .el-form-item) {
  margin-bottom: 16px;
}

:deep(.appearance-form .el-form-item__label) {
  color: var(--el-text-color-primary);
  padding-bottom: calc(var(--spacing) * 2);
}

@media (max-width: 1050px) {
  .appearance-settings section > .grid {
    grid-template-columns: 1fr;
  }

  .login-preview-frame {
    display: none;
  }
}
</style>
