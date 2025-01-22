<template>
  <div class="theme-setting" v-loading="loading">
    <h4 class="p-16-24">{{ $t('views.system.theme.title') }}</h4>
    <el-scrollbar>
      <div class="p-24 pt-0">
        <div class="app-card p-24">
          <h5 class="mb-16">{{ $t('views.system.theme.platformDisplayTheme') }}</h5>
          <el-radio-group
            v-model="themeRadio"
            class="app-radio-button-group"
            @change="changeThemeHandle"
          >
            <template v-for="(item, index) in themeList" :key="index">
              <el-radio-button :label="item.label" :value="item.value" />
            </template>
            <el-radio-button :label="$t('views.system.theme.custom')" value="custom" />
          </el-radio-group>
          <div v-if="themeRadio === 'custom'">
            <h5 class="mt-16 mb-8">{{ $t('views.system.theme.customTheme') }}</h5>
            <el-color-picker v-model="customColor" @change="customColorHandle" />
          </div>
        </div>
        <div class="app-card p-24 mt-16">
          <h5 class="mb-16">{{ $t('views.system.theme.platformLoginSettings') }}</h5>
          <el-card shadow="never" class="layout-bg">
            <div class="flex-between">
              <h5 class="mb-16">{{ $t('views.system.theme.pagePreview') }}</h5>
              <el-button type="primary" link @click="resetForm('login')">
                {{ $t('views.system.theme.restoreDefaults') }}
              </el-button>
            </div>
            <el-scrollbar>
              <div class="theme-preview">
                <el-row :gutter="8">
                  <el-col :span="16">
                    <LoginPreview :data="themeForm" />
                  </el-col>
                  <el-col :span="8">
                    <div class="theme-form">
                      <el-card shadow="never" class="mb-8">
                        <div class="flex-between mb-8">
                          <span class="lighter">{{ $t('views.system.theme.websiteLogo') }}</span>
                          <el-upload
                            ref="uploadRef"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            accept="image/jpeg, image/png, image/gif"
                            :on-change="
                              (file: any, fileList: any) => onChange(file, fileList, 'icon')
                            "
                          >
                            <el-button size="small">
                              {{ $t('views.system.theme.replacePicture') }}
                            </el-button>
                          </el-upload>
                        </div>
                        <el-text type="info" size="small"
                          >{{ $t('views.system.theme.websiteLogoTip') }}
                        </el-text>
                      </el-card>
                      <el-card shadow="never" class="mb-8">
                        <div class="flex-between mb-8">
                          <span class="lighter"> {{ $t('views.system.theme.loginLogo') }}</span>
                          <el-upload
                            ref="uploadRef"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            accept="image/jpeg, image/png, image/gif"
                            :on-change="
                              (file: any, fileList: any) => onChange(file, fileList, 'loginLogo')
                            "
                          >
                            <el-button size="small">
                              {{ $t('views.system.theme.replacePicture') }}
                            </el-button>
                          </el-upload>
                        </div>
                        <el-text type="info" size="small"
                          >{{ $t('views.system.theme.loginLogoTip') }}
                        </el-text>
                      </el-card>
                      <el-card shadow="never" class="mb-8">
                        <div class="flex-between mb-8">
                          <span class="lighter">{{
                            $t('views.system.theme.loginBackground')
                          }}</span>
                          <el-upload
                            ref="uploadRef"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            accept="image/jpeg, image/png, image/gif"
                            :on-change="
                              (file: any, fileList: any) => onChange(file, fileList, 'loginImage')
                            "
                          >
                            <el-button size="small">
                              {{ $t('views.system.theme.replacePicture') }}
                            </el-button>
                          </el-upload>
                        </div>
                        <el-text type="info" size="small">
                          {{ $t('views.system.theme.loginBackgroundTip') }}
                        </el-text>
                      </el-card>

                      <el-form
                        ref="themeFormRef"
                        :model="themeForm"
                        label-position="top"
                        require-asterisk-position="right"
                        :rules="rules"
                        @submit.prevent
                      >
                        <el-form-item :label="$t('views.system.theme.websiteName')" prop="title">
                          <el-input
                            v-model="themeForm.title"
                            :placeholder="$t('views.system.theme.websiteNamePlaceholder')"
                          >
                          </el-input>
                          <el-text type="info">{{
                            $t('views.system.theme.websiteNameTip')
                          }}</el-text>
                        </el-form-item>
                        <el-form-item :label="$t('views.system.theme.websiteSlogan')" prop="slogan">
                          <el-input
                            v-model="themeForm.slogan"
                            :placeholder="$t('views.system.theme.websiteSloganPlaceholder')"
                            maxlength="64"
                            show-word-limit
                          >
                          </el-input>
                          <el-text type="info">{{
                            $t('views.system.theme.websiteSloganTip')
                          }}</el-text>
                        </el-form-item>
                      </el-form>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-scrollbar>
            <div class="mt-16">
              <el-text type="info">{{ $t('views.system.theme.logoDefaultTip') }}</el-text>
            </div>
          </el-card>
        </div>
        <div class="app-card p-24 mt-16">
          <h5 class="mb-16">{{ $t('views.system.theme.platformSetting') }}</h5>
          <el-card shadow="never" class="layout-bg">
            <div class="flex-between">
              <h5 class="mb-16">{{ $t('views.system.theme.pagePreview') }}</h5>
              <el-button type="primary" link @click="resetForm('platform')">
                {{ $t('views.system.theme.restoreDefaults') }}
              </el-button>
            </div>
            <el-scrollbar>
              <div class="theme-preview">
                <el-row :gutter="8">
                  <el-col :span="16">
                    <div class="theme-platform mr-16">
                      <div
                        class="theme-platform-header border-b flex-between"
                        :class="!isDefaultTheme ? 'custom-header' : ''"
                      >
                        <div class="flex-center h-full">
                          <div class="app-title-container cursor">
                            <div class="logo flex-center">
                              <LogoFull height="25px" />
                            </div>
                          </div>
                        </div>
                        <div class="flex-center">
                          <AppIcon
                            iconName="app-github"
                            class="cursor color-secondary mr-8 ml-8"
                            style="font-size: 20px"
                            v-if="themeForm.showProject"
                          ></AppIcon>
                          <AppIcon
                            iconName="app-reading"
                            class="cursor color-secondary mr-8 ml-8"
                            style="font-size: 20px"
                            v-if="themeForm.showUserManual"
                          ></AppIcon>
                          <AppIcon
                            iconName="app-help"
                            class="cursor color-secondary ml-8"
                            style="font-size: 20px"
                            v-if="themeForm.showForum"
                          ></AppIcon>
                        </div>
                      </div>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="theme-form">
                      <div>
                        <el-checkbox
                          v-model="themeForm.showUserManual"
                          :label="$t('views.system.theme.showUserManual')"
                        />
                        <div class="ml-24">
                          <el-input
                            v-model="themeForm.userManualUrl"
                            :placeholder="$t('views.system.theme.urlPlaceholder')"
                          />
                        </div>
                      </div>
                      <div class="mt-4">
                        <el-checkbox
                          v-model="themeForm.showForum"
                          :label="$t('views.system.theme.showForum')"
                        />
                        <div class="ml-24">
                          <el-input
                            v-model="themeForm.forumUrl"
                            :placeholder="$t('views.system.theme.urlPlaceholder')"
                          />
                        </div>
                      </div>
                      <div class="mt-4">
                        <el-checkbox
                          v-model="themeForm.showProject"
                          :label="$t('views.system.theme.showProject')"
                        />
                        <div class="ml-24">
                          <el-input
                            v-model="themeForm.projectUrl"
                            :placeholder="$t('views.system.theme.urlPlaceholder')"
                          />
                        </div>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-scrollbar>
            <div class="mt-16">
              <el-text type="info">{{ $t('views.system.theme.defaultTip') }}</el-text>
            </div>
          </el-card>
        </div>
      </div>
    </el-scrollbar>
    <div class="theme-setting__operate w-full p-16-24">
      <el-button @click="resetTheme">{{ $t('views.system.theme.abandonUpdate') }}</el-button>
      <el-button type="primary" @click="updateTheme(themeFormRef)">
        {{ $t('views.system.theme.saveAndApply') }}</el-button
      >
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import type { FormInstance, FormRules, UploadFiles } from 'element-plus'
import { cloneDeep } from 'lodash'
import LoginPreview from './LoginPreview.vue'
import { themeList, defaultSetting, defaultPlatformSetting } from '@/utils/theme'
import ThemeApi from '@/api/theme'
import { MsgSuccess, MsgError } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'

const { user } = useStore()
const router = useRouter()

onBeforeRouteLeave((to, from) => {
  user.setTheme(cloneTheme.value)
})

const themeInfo = computed(() => user.themeInfo)
const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})

const themeFormRef = ref<FormInstance>()
const loading = ref(false)
const cloneTheme = ref(null)
const themeForm = ref<any>({
  theme: '',
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: t('views.system.theme.defaultSlogan'),
  ...defaultPlatformSetting
})
const themeRadio = ref('')
const customColor = ref('')

const rules = reactive<FormRules>({
  title: [
    { required: true, message: t('views.system.theme.websiteNamePlaceholder'), trigger: 'blur' }
  ],
  slogan: [
    { required: true, message: t('views.system.theme.websiteSloganPlaceholder'), trigger: 'blur' }
  ]
})

const onChange = (file: any, fileList: UploadFiles, attr: string) => {
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    // @ts-ignore
    MsgError(t('views.system.theme.fileMessageError'))
    return false
  } else {
    themeForm.value[attr] = file.raw
  }
  user.setTheme(themeForm.value)
}

function changeThemeHandle(val: string) {
  if (val !== 'custom') {
    themeForm.value.theme = val
    user.setTheme(themeForm.value)
  }
}

function customColorHandle(val: string) {
  themeForm.value.theme = val
  user.setTheme(themeForm.value)
}

function resetTheme() {
  user.setTheme(cloneTheme.value)
  themeForm.value = cloneDeep(themeInfo.value)
}

function resetForm(val: string) {
  themeForm.value =
    val === 'login'
      ? {
          ...themeForm.value,
          theme: themeForm.value.theme,
          ...defaultSetting
        }
      : {
          ...themeForm.value,
          theme: themeForm.value.theme,
          ...defaultPlatformSetting
        }

  user.setTheme(themeForm.value)
}

const updateTheme = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      let fd = new FormData()
      Object.keys(themeForm.value).map((item) => {
        fd.append(item, themeForm.value[item])
      })
      ThemeApi.postThemeInfo(fd, loading).then((res) => {
        user.theme()
        cloneTheme.value = cloneDeep(themeForm.value)
        MsgSuccess(t('views.system.theme.saveSuccess'))
      })
    }
  })
}

onMounted(() => {
  if (user.isExpire()) {
    router.push({ path: `/application` })
  }
  if (themeInfo.value) {
    themeRadio.value = themeList.some((v) => v.value === themeInfo.value.theme)
      ? themeInfo.value.theme
      : 'custom'
    customColor.value = themeInfo.value.theme
    themeForm.value = cloneDeep(themeInfo.value)
    cloneTheme.value = cloneDeep(themeInfo.value)
  }
})
</script>

<style lang="scss" scoped>
.theme-setting {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  padding-bottom: 64px;

  &__operate {
    position: absolute;
    bottom: 0;
    right: 0;
    left: 0;
    background: #ffffff;
    text-align: right;
    box-sizing: border-box;
    box-shadow: 0px -2px 4px 0px rgba(31, 35, 41, 0.08);
  }

  .theme-preview {
    min-width: 1000px;
  }

  .theme-platform {
    background: #ffffff;
    height: 220px;

    .theme-platform-header {
      padding: 10px 20px;
      background: var(--app-header-bg-color);
    }
  }
}
</style>
