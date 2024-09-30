<template>
  <div class="theme-setting" v-loading="loading">
    <h4 class="p-16-24">外观设置</h4>
    <el-scrollbar>
      <div class="p-24 pt-0">
        <div class="app-card p-24">
          <h5 class="mb-16">平台显示主题</h5>
          <el-radio-group
            v-model="themeRadio"
            class="app-radio-button-group"
            @change="changeThemeHandle"
          >
            <template v-for="(item, index) in themeList" :key="index">
              <el-radio-button :label="item.label" :value="item.value" />
            </template>
            <el-radio-button label="自定义" value="custom" />
          </el-radio-group>
          <div v-if="themeRadio === 'custom'">
            <h5 class="mt-16 mb-8">自定义主题</h5>
            <el-color-picker v-model="customColor" @change="customColorHandle" />
          </div>
        </div>
        <div class="app-card p-24 mt-16">
          <h5 class="mb-16">平台登陆设置</h5>
          <el-card shadow="never" class="layout-bg">
            <div class="flex-between">
              <h5 class="mb-16">页面预览</h5>
              <el-button type="primary" link @click="resetForm('login')"> 恢复默认 </el-button>
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
                          <span class="lighter">网站 Logo</span>
                          <el-upload
                            ref="uploadRef"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            accept="image/*"
                            :on-change="
                              (file: any, fileList: any) => onChange(file, fileList, 'icon')
                            "
                          >
                            <el-button size="small"> 替换图片 </el-button>
                          </el-upload>
                        </div>
                        <el-text type="info" size="small"
                          >顶部网站显示的 Logo，建议尺寸 48 x 48，支持 JPG、PNG、SVG，大小不超过
                          200KB</el-text
                        >
                      </el-card>
                      <el-card shadow="never" class="mb-8">
                        <div class="flex-between mb-8">
                          <span class="lighter">登录 Logo</span>
                          <el-upload
                            ref="uploadRef"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            accept="image/*"
                            :on-change="
                              (file: any, fileList: any) => onChange(file, fileList, 'loginLogo')
                            "
                          >
                            <el-button size="small"> 替换图片 </el-button>
                          </el-upload>
                        </div>
                        <el-text type="info" size="small"
                          >登录页面右侧 Logo，建议尺寸 204*52，支持 JPG、PNG、SVG，大小不超过
                          200KB</el-text
                        >
                      </el-card>
                      <el-card shadow="never" class="mb-8">
                        <div class="flex-between mb-8">
                          <span class="lighter">登录背景图</span>
                          <el-upload
                            ref="uploadRef"
                            action="#"
                            :auto-upload="false"
                            :show-file-list="false"
                            accept="image/*"
                            :on-change="
                              (file: any, fileList: any) => onChange(file, fileList, 'loginImage')
                            "
                          >
                            <el-button size="small"> 替换图片 </el-button>
                          </el-upload>
                        </div>
                        <el-text type="info" size="small">
                          左侧背景图，矢量图建议尺寸 576*900，位图建议尺寸1152*1800；支持
                          JPG、PNG、SVG，大小不超过 5M
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
                        <el-form-item label="网站名称" prop="title">
                          <el-input v-model="themeForm.title" placeholder="请输入网站名称">
                          </el-input>
                          <el-text type="info"> 显示在网页 Tab 的平台名称 </el-text>
                        </el-form-item>
                        <el-form-item label="欢迎语" prop="slogan">
                          <el-input
                            v-model="themeForm.slogan"
                            placeholder="请输入欢迎语"
                            maxlength="64"
                            show-word-limit
                          >
                          </el-input>
                          <el-text type="info"> 产品 Logo 下的 欢迎语 </el-text>
                        </el-form-item>
                      </el-form>
                    </div></el-col
                  >
                </el-row>
              </div>
            </el-scrollbar>
            <div class="mt-16">
              <el-text type="info">默认为 MaxKB 登录界面，支持自定义设置</el-text>
            </div>
          </el-card>
        </div>
        <div class="app-card p-24 mt-16">
          <h5 class="mb-16">平台设置</h5>
          <el-card shadow="never" class="layout-bg">
            <div class="flex-between">
              <h5 class="mb-16">页面预览</h5>
              <el-button type="primary" link @click="resetForm('platform')"> 恢复默认 </el-button>
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
                        <el-checkbox v-model="themeForm.showUserManual" label="显示用户手册" />
                        <div class="ml-16">
                          <el-input
                            v-model="themeForm.userManualUrl"
                            placeholder="请输入 URL 地址"
                          />
                        </div>
                      </div>
                      <div class="my-2">
                        <el-checkbox v-model="themeForm.showForum" label="显示论坛求助" />
                        <div class="ml-16">
                          <el-input v-model="themeForm.forumUrl" placeholder="请输入 URL 地址" />
                        </div>
                      </div>
                      <div class="mt-2">
                        <el-checkbox v-model="themeForm.showProject" label="显示项目地址" />
                        <div class="ml-16">
                          <el-input v-model="themeForm.projectUrl" placeholder="请输入 URL 地址" />
                        </div>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-scrollbar>
            <div class="mt-16">
              <el-text type="info">默认为 MaxKB 登录界面，支持自定义设置</el-text>
            </div>
          </el-card>
        </div>
      </div>
    </el-scrollbar>
    <div class="theme-setting__operate w-full p-16-24">
      <el-button @click="resetTheme">放弃更新</el-button>
      <el-button type="primary" @click="updataTheme(themeFormRef)"> 保存并应用 </el-button>
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
  slogan: '欢迎使用 MaxKB 智能知识库问答系统',
  ...defaultPlatformSetting
})
const themeRadio = ref('')
const customColor = ref('')

const rules = reactive<FormRules>({
  title: [{ required: true, message: '请输入网站标题', trigger: 'blur' }],
  slogan: [{ required: true, message: '请输入欢迎语', trigger: 'blur' }]
})

const onChange = (file: any, fileList: UploadFiles, attr: string) => {
  if (attr === 'loginImage') {
    const isLimit = file?.size / 1024 / 1024 < 5
    if (!isLimit) {
      // @ts-ignore
      MsgError(`文件大小超过 5M`)
      return false
    } else {
      themeForm.value[attr] = file.raw
    }
  } else {
    const isLimit = file?.size / 1024 < 200
    if (!isLimit) {
      // @ts-ignore
      MsgError(`文件大小超过 200KB`)
      return false
    } else {
      themeForm.value[attr] = file.raw
    }
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
    val === 'base'
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

const updataTheme = async (formEl: FormInstance | undefined, test?: string) => {
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
        MsgSuccess('外观设置成功')
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
