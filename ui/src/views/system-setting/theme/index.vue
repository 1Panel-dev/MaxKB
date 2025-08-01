<template>
  <div class="theme-setting p-16-24" v-loading="loading">
    <el-breadcrumb separator-icon="ArrowRight" class="mb-16">
      <el-breadcrumb-item>{{ t('views.system.subTitle') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ $t('theme.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-scrollbar>
      <el-card style="--el-card-padding: 16px">
        <h5 class="mb-16">{{ $t('theme.platformDisplayTheme') }}</h5>
        <el-radio-group
          v-model="themeRadio"
          class="app-radio-button-group"
          @change="changeThemeHandle"
        >
          <template v-for="(item, index) in themeList" :key="index">
            <el-radio-button :label="item.label" :value="item.value" />
          </template>
          <el-radio-button :label="$t('theme.custom')" value="custom" />
        </el-radio-group>
        <div v-if="themeRadio === 'custom'">
          <h5 class="mt-16 mb-8">{{ $t('theme.customTheme') }}</h5>
          <el-color-picker v-model="customColor" @change="customColorHandle" />
        </div>
      </el-card>

      <el-card style="--el-card-padding: 16px" class="mt-16">
        <h5 class="mb-16">{{ $t('theme.platformLoginSettings') }}</h5>
        <el-card shadow="never" class="layout-bg">
          <div class="flex-between">
            <h5 class="mb-16">{{ $t('theme.pagePreview') }}</h5>
            <el-button type="primary" link @click="resetForm('login')">
              {{ $t('theme.restoreDefaults') }}
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
                        <span class="lighter">{{ $t('theme.websiteLogo') }}</span>
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
                            {{ $t('theme.replacePicture') }}
                          </el-button>
                        </el-upload>
                      </div>
                      <el-text type="info" size="small">{{ $t('theme.websiteLogoTip') }} </el-text>
                    </el-card>
                    <el-card shadow="never" class="mb-8">
                      <div class="flex-between mb-8">
                        <span class="lighter"> {{ $t('theme.loginLogo') }}</span>
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
                            {{ $t('theme.replacePicture') }}
                          </el-button>
                        </el-upload>
                      </div>
                      <el-text type="info" size="small">{{ $t('theme.loginLogoTip') }} </el-text>
                    </el-card>
                    <el-card shadow="never" class="mb-8">
                      <div class="flex-between mb-8">
                        <span class="lighter">{{ $t('theme.loginBackground') }}</span>
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
                            {{ $t('theme.replacePicture') }}
                          </el-button>
                        </el-upload>
                      </div>
                      <el-text type="info" size="small">
                        {{ $t('theme.loginBackgroundTip') }}
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
                      <el-form-item :label="$t('theme.websiteName')" prop="title">
                        <el-input
                          v-model="themeForm.title"
                          :placeholder="$t('theme.websiteNamePlaceholder')"
                          show-word-limit
                          maxlength="128"
                        >
                        </el-input>
                        <el-text type="info">{{ $t('theme.websiteNameTip') }} </el-text>
                      </el-form-item>
                      <el-form-item :label="$t('theme.websiteSlogan')" prop="slogan">
                        <el-input
                          v-model="themeForm.slogan"
                          :placeholder="$t('theme.websiteSloganPlaceholder')"
                          maxlength="64"
                          show-word-limit
                        >
                        </el-input>
                        <el-text type="info">{{ $t('theme.websiteSloganTip') }} </el-text>
                      </el-form-item>
                    </el-form>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-scrollbar>
          <div class="mt-16">
            <el-text type="info">{{ $t('theme.logoDefaultTip') }}</el-text>
          </div>
        </el-card>
      </el-card>
      <el-card style="--el-card-padding: 16px" class="mt-16">
        <h5 class="mb-16">{{ $t('theme.platformSetting') }}</h5>
        <el-card shadow="never" class="layout-bg">
          <div class="flex-between">
            <h5 class="mb-16">{{ $t('theme.pagePreview') }}</h5>
            <el-button type="primary" link @click="resetForm('platform')">
              {{ $t('theme.restoreDefaults') }}
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
                          iconName="app-user-manual"
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
                        :label="$t('theme.showUserManual')"
                      />
                      <div class="ml-24">
                        <el-input
                          v-model="themeForm.userManualUrl"
                          :placeholder="$t('theme.urlPlaceholder')"
                          show-word-limit
                          maxlength="128"
                        />
                      </div>
                    </div>
                    <div class="mt-4">
                      <el-checkbox v-model="themeForm.showForum" :label="$t('theme.showForum')" />
                      <div class="ml-24">
                        <el-input
                          v-model="themeForm.forumUrl"
                          :placeholder="$t('theme.urlPlaceholder')"
                          show-word-limit
                          maxlength="128"
                        />
                      </div>
                    </div>
                    <div class="mt-4">
                      <el-checkbox
                        v-model="themeForm.showProject"
                        :label="$t('theme.showProject')"
                      />
                      <div class="ml-24">
                        <el-input
                          v-model="themeForm.projectUrl"
                          :placeholder="$t('theme.urlPlaceholder')"
                          show-word-limit
                          maxlength="128"
                        />
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-scrollbar>
          <div class="mt-16">
            <el-text type="info">{{ $t('theme.defaultTip') }}</el-text>
          </div>
        </el-card>
      </el-card>
    </el-scrollbar>
    <div class="theme-setting__operate w-full p-16-24">
      <el-button @click="resetTheme">{{ $t('theme.abandonUpdate') }}</el-button>
      <el-button
        type="primary"
        @click="updateTheme(themeFormRef)"
        v-hasPermission="
          new ComplexPermission(
            [RoleConst.ADMIN],
            [PermissionConst.APPEARANCE_SETTINGS_EDIT],
            [],
            'OR',
          )
        "
      >
        {{ $t('theme.saveAndApply') }}
      </el-button>
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
import ThemeApi from '@/api/system-settings/theme'
import { MsgSuccess, MsgError } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
import { ComplexPermission } from '@/utils/permission/type'

const { theme } = useStore()
const router = useRouter()

onBeforeRouteLeave((to, from) => {
  theme.setTheme(cloneTheme.value)
})

const themeInfo = computed(() => theme.themeInfo)
const isDefaultTheme = computed(() => {
  return theme.isDefaultTheme()
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
  slogan: t('theme.defaultSlogan'),
  ...defaultPlatformSetting,
})
const themeRadio = ref('')
const customColor = ref('')

const rules = reactive<FormRules>({
  title: [{ required: true, message: t('theme.websiteNamePlaceholder'), trigger: 'blur' }],
  slogan: [{ required: true, message: t('theme.websiteSloganPlaceholder'), trigger: 'blur' }],
})

const onChange = (file: any, fileList: UploadFiles, attr: string) => {
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    // @ts-ignore
    MsgError(t('theme.fileMessageError'))
    return false
  } else {
    themeForm.value[attr] = file.raw
  }
  theme.setTheme(themeForm.value)
}

function changeThemeHandle(val: string) {
  if (val !== 'custom') {
    themeForm.value.theme = val
    theme.setTheme(themeForm.value)
  }
}

function customColorHandle(val: string) {
  themeForm.value.theme = val
  theme.setTheme(themeForm.value)
}

function resetTheme() {
  theme.setTheme(cloneTheme.value)
  themeForm.value = cloneDeep(themeInfo.value)
}

function resetForm(val: string) {
  themeForm.value =
    val === 'login'
      ? {
          ...themeForm.value,
          theme: themeForm.value.theme,
          ...defaultSetting,
        }
      : {
          ...themeForm.value,
          theme: themeForm.value.theme,
          ...defaultPlatformSetting,
        }

  theme.setTheme(themeForm.value)
}

const updateTheme = async (formEl: FormInstance | undefined, test?: string) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      const fd = new FormData()
      Object.keys(themeForm.value).map((item) => {
        fd.append(item, themeForm.value[item])
      })
      ThemeApi.postThemeInfo(fd, loading).then((res) => {
        theme.theme()
        cloneTheme.value = cloneDeep(themeForm.value)
        MsgSuccess(t('theme.saveSuccess'))
      })
    }
  })
}

onMounted(() => {
  // if (user.isExpire()) {
  //   router.push({path: `/application`})
  // }
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
