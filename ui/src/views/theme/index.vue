<template>
  <p class="router-title">外观配置</p>
  <div class="appearance-table__content">
    <el-scrollbar>
      <div class="theme">
        <div class="platform-theme">平台显示主题</div>
        <div class="navigate-bg">顶部导航背景色</div>
        <div class="color-type">
          <div class="color-item" :class="navigateBg === 'dark' && 'active'" @click="navigateClick('dark')">
            <img :src="DarkBg" alt="" />
            <div class="color-item-label">
              <el-radio v-model="navigateBg" @change="navigateBgChange" label="dark">暗色</el-radio>
            </div>
          </div>
          <div class="color-item" :class="navigateBg === 'light' && 'active'" @click="navigateClick('light')">
            <img :src="LightBg" alt="" />
            <div class="color-item-label">
              <el-radio v-model="navigateBg" @change="navigateBgChange" label="light">浅色</el-radio>
            </div>
          </div>
        </div>
        <div class="theme-bg">主题色</div>
        <div class="theme-color">
          <el-radio-group v-model="themeColor" @change="themeColorChange">
            <el-radio label="default">默认 (蓝色) </el-radio>
            <el-radio label="custom">自定义</el-radio>
          </el-radio-group>
        </div>

        <template v-if="themeColor === 'custom'">
          <div class="custom-color">自定义色值</div>
          <el-color-picker
            :trigger-width="108"
            v-model="customColor"
            :predefine="COLOR_PANEL"
            is-custom
            effect="light"
            @change="customColorChange"
          />
        </template>
      </div>
      <div class="login">
        <div class="platform-login">平台登录设置</div>
        <div class="page-preview">
          <div class="title">
            <span class="left">页面预览</span>
            <el-button text @click="resetLoginForm(true)">恢复默认</el-button>
          </div>
          <div class="page-setting">
            <div class="page-content">
              <!-- <img :src="loginPreview" alt="" /> -->
              <login-preview 
                :navigate-bg="navigateBg" 
                :theme-color="themeColor" 
                :custom-color="customColor" 
                :name="loginForm.name" 
                :slogan="loginForm.slogan" 
                :web="web"
                :bg="bg"
                :login="login"
                :height="navigateHeight"
                :foot="loginForm.foot"
                :foot-content="loginForm.footContent"
              />
              <div class="tips-page">
                默认为 DataEase 登录界面，支持自定义设置
              </div>
            </div>
            <div class="config-list">
              <div class="config-item" v-for="ele in configList" :key="ele.type">
                <div class="config-logo">
                  <span class="logo">{{ ele.logo }}</span>
                  <el-upload
                    :name="ele.type"
                    :show-file-list="false"
                    class="upload-demo"
                    accept=".jpeg,.jpg,.png,.gif,.svg"
                    :before-upload="e => beforeUpload(e, ele.type)"
                    :http-request="uploadImg"
                  >
                    <el-button secondary>替换图片</el-button>
                  </el-upload>
                </div>
                <div class="tips">{{ ele.tips }}</div>
              </div>
              <el-form
                ref="loginFormRef"
                :model="loginForm"
                label-position="top"
                :rules="rules"
                require-asterisk-position="right"
                label-width="120px"
                class="page-Form"
              >
                <el-form-item label="网站名称" prop="name">
                  <el-input v-model="loginForm.name" />
                  <div class="form-tips">显示在网页 Tab 的平台名称</div>
                </el-form-item>
                <el-form-item label="Slogan" prop="slogan">
                  <el-input v-model="loginForm.slogan" />
                  <div class="form-tips">产品 Logo 下的 Slogan</div>
                </el-form-item>
                <el-form-item label="页脚" prop="foot">
                  <el-switch active-value="true" inactive-value="false" v-model="loginForm.foot" />
                </el-form-item>
                <el-form-item label="页脚内容" prop="footContent" v-if="loginForm.foot === 'true'">
                  <tinymce-editor v-if="loginForm.foot === 'true'" v-model="loginForm.footContent"/>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </div>
      <div class="login">
        <div class="platform-login">平台设置</div>
        <div class="page-preview">
          <div class="title">
            <span class="left">页面预览</span>
            <el-button text @click="resetTopForm(true)">恢复默认</el-button>
          </div>
          <div class="page-setting">
            <div class="page-content">
              <!-- <div class="navigate-preview" :style="{'height': `${navigateHeight}px`}"> -->
              <div class="navigate-preview" style="height: 425px;">
                <div class="navigate-head" :class="{ 'light-head': navigateBg && navigateBg === 'light' }">
                  <img class="logo" v-if="navigate" :src="navigate.startsWith('blob') ? navigate : (baseUrl + navigate)" alt="" />
                  <Icon v-else className="logo" name="logo"></Icon>
                  <el-divider direction="vertical" />
                </div>
                <div class="navigate-content" />
              </div>
              <div class="tips-page">
                默认为 DataEase 平台界面，支持自定义设置
              </div>
            </div>
            <div class="config-list">
              <div class="config-item">
                <div class="config-logo">
                  <span class="logo">顶部导航 Logo</span>
                  <el-upload
                    class="upload-demo"
                    :show-file-list="false"
                    accept=".jpeg,.jpg,.png,.gif,.svg"
                    :before-upload="e => beforeUpload(e, 'navigate')"
                    :http-request="uploadImg"
                  >
                    <el-button secondary>替换图片</el-button>
                  </el-upload>
                </div>
                <div class="tips">顶部导航菜单显示的 Logo；建议尺寸 134 x 34，支持 JPG、PNG，大小不超过 200KB</div>
              </div>
              <el-form
                ref="topFormRef"
                :model="topForm"
                label-position="top"
                :rules="topRules"
                require-asterisk-position="right"
                label-width="120px"
                class="page-Form"
              >
                <el-form-item style="margin-bottom: 14px" label="帮助文档" prop="help">
                  <el-input v-model="topForm.help" />
                </el-form-item>

                <el-form-item label="AI助手按钮" prop="showAi">
                  <el-radio-group v-model="topForm.showAi" >
                    <el-radio v-for="option in btnShowOptions" :key="option.label" :label="option.label">{{ option.name }}</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="文档按钮" prop="showDoc">
                  <el-radio-group v-model="topForm.showDoc">
                    <el-radio v-for="option in btnShowOptions" :key="option.label" :label="option.label">{{ option.name }}</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item label="关于按钮" prop="showAbout">
                  <el-radio-group v-model="topForm.showAbout">
                    <el-radio v-for="option in btnShowOptions" :key="option.label" :label="option.label">{{ option.name }}</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>

            </div>
          </div>
        </div>
      </div>
    </el-scrollbar>
  </div>
  <div class="appearance-foot">
    <el-button secondary @click="giveUp">{{ t('appearance.give_up') }}</el-button>
    <el-button type="primary" v-if="showSaveButton" @click="saveHandler">{{ t('appearance.save_apply') }}</el-button>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from "vue";
import DarkBg from "@/assets/img/dark-theme-bg.png";
import LightBg from "@/assets/img/light-theme-bg.png";
import { type FormInstance, type FormRules, type UploadUserFile, ElMessage } from "element-plus-secondary";
import { useI18n } from '@/hooks/web/useI18n'
import request from '@/config/axios'
import { useAppearanceStoreWithOut } from '@/store/modules/appearance'
import LoginPreview from "./LoginPreview.vue"
import TinymceEditor from "@/components/rich-text/TinymceEditor.vue"
const appearanceStore = useAppearanceStoreWithOut()
const { t } = useI18n()
interface LoginForm {
  name: string;
  slogan: string;
  foot: string;
  footContent?: string
}
interface ConfigItem {
  pkey: string
  pval: string
  type: string
  sort: number
}
const btnShowOptions = [
  { label: '0', name: '显示'},
  { label: '1', name: '隐藏'},
  { label: '2', name: 'Iframe中隐藏'}
]
const COLOR_PANEL = [
  '#FF4500',
  '#FF8C00',
  '#FFD700',
  '#71AE46',
  '#00CED1',
  '#1E90FF',
  '#C71585',
  '#999999',
  '#000000',
  '#FFFFFF'
]
const basePath = import.meta.env.VITE_API_BASEPATH
const baseUrl = basePath + '/appearance/image/'
const fileList = ref<UploadUserFile[]>([])
const navigateBg = ref("dark");
const themeColor = ref("default");
const customColor = ref("#307eff");
const web = ref('')
const bg = ref('')
const login = ref('')
const navigate = ref('')
const navigateHeight = ref(400)

const changedItemArray = ref<ConfigItem[]>([])

const loginFormRef = ref<FormInstance>();
const defaultLoginForm = reactive<LoginForm>({
  name: "DataEase",
  slogan: "欢迎使用 DataEase 数据可视化分析平台",
  foot: 'false',
  footContent: ''
});
const loginForm = reactive<LoginForm>({
  name: "DataEase",
  slogan: "欢迎使用 DataEase 数据可视化分析平台",
  foot: 'false',
  footContent: ''
});

const rules = reactive<FormRules>({
  name: [{ required: true, message: "请输入网站名称", trigger: "blur" }],
  slogan: [
    {
      required: true,
      message: "请输入Slogan",
      trigger: "blur",
    },
  ],
  foot: [
    {
      required: true,
      message: "",
      trigger: "change",
    },
  ],
});

const topForm = reactive<{ help: string, showAi: string, showDoc: string, showAbout: string }>({
  help: "https://dataease.io/docs/",
  showAi: '0',
  showDoc: '0',
  showAbout: '0'
});

const defaultTopForm = reactive<{ help: string, showAi: string, showDoc: string, showAbout: string }>({
  help: "https://dataease.io/docs/",
  showAi: '0',
  showDoc: '0',
  showAbout: '0'
});

const topRules = reactive<FormRules>({
  help: [{ required: true, message: "请输入帮助文档", trigger: "blur" }],
  showAi: [{ required: true, message: "请选择是否展示AI助手", trigger: "change" }],
  showDoc: [{ required: true, message: "请选择是否展示文档", trigger: "change" }],
  showAbout: [{ required: true, message: "请选择是否展示关于", trigger: "change" }],
});
const configList = [
  {
    logo: "网站 Logo",
    type: "web",
    tips: "顶部网站显示的 Logo，建议尺寸 48 x 48，支持 JPG、PNG、SVG，大小不超过 200KB",
  },
  {
    logo: "登录 Logo",
    type: "login",
    tips: "登录页面右侧 Logo，建议尺寸 204 x 52，支持 JPG、PNG、SVG，大小不超过 200KB",
  },
  {
    logo: "登录背景图",
    type: "bg",
    tips: "左侧背景图，矢量图建议尺寸 640 x 900，位图建议尺寸 1280 x 1800；支持 JPG、PNG、SVG，大小不超过 5M",
  },
];

const giveUp = () => {
  resetLoginForm(false)
  resetTopForm(false)
  init()
}
const showSaveButton = ref(true)
const saveHandler = () => {
  const param = buildParam()
  const url = '/appearance/save'
  request.post({ url, data: param, headersType: 'multipart/form-data;' }).then(res => {
    if (!res.msg) {
      ElMessage.success(t('common.save_success'))
      appearanceStore.setLoaded(false)
      appearanceStore.setAppearance()
      showSaveButton.value = false
      nextTick(() => {
        showSaveButton.value = true
      })
    }
  })
}
const buildParam = () => {
  for (const key in loginForm) {
    const item = loginForm[key]
    if (key === 'footContent') {
      addChangeArray(key, item, 'blob')
    } else {
      addChangeArray(key, item)
    }
  }
  for (const key in topForm) {
    const item = topForm[key]
    addChangeArray(key, item)
  }
  const formData = new FormData();
  if (fileList.value.length) {
    fileList.value.forEach((file) => {
      const name = file.name + "," + file['flag']
      const fileArray = [file]
      const newfile = new File(fileArray, name, { type: file['type'] })
      formData.append("files", newfile)
    })
  }
  formData.append(
    "request",
    new Blob([JSON.stringify(changedItemArray.value)], { type: "application/json" })
  );
  return formData
}
const init = () => {
  const url = '/appearance/query'
  changedItemArray.value = []
  fileList.value = []
  request.get({ url }).then(res => {
    const list = res.data
    if (!list.length) {
      return
    }
    list.forEach(item => {
      const pkey = item.pkey
      const pval = item.pval
      if (pkey === 'navigateBg') {
        navigateBg.value = pval
      } else if(pkey === 'themeColor') {
        themeColor.value = pval
      } else if(pkey === 'customColor') {
        customColor.value = pval
      } else if(pkey === 'web') {
        web.value = pval
      } else if(pkey === 'login') {
        login.value = pval
      } else if(pkey === 'bg') {
        bg.value = pval
      } else if(pkey === 'navigate') {
        navigate.value = pval
      } else if(loginForm.hasOwnProperty(pkey)) {
        loginForm[pkey] = pval
      } else if(topForm.hasOwnProperty(pkey)) {
        topForm[pkey] = pval
      }
    })
  })
}
const addChangeArray = (key: string, val: string, type?: string) => {
  let len = changedItemArray.value.length
  let match = false
  while (len--) {
    const item = changedItemArray.value[len]
    if (item['pkey'] === key) {
      changedItemArray.value[len] = { pkey: key, pval: val, type: type || 'text', sort: 1 }
      match = true
    }
  }
  if (!match) {
    changedItemArray.value.push({ pkey: key, pval: val, type: type || 'text', sort: 1  })
  }
}
const navigateBgChange = val => {
  addChangeArray('navigateBg', val)
}
const navigateClick = val => {
  navigateBg.value = val
  navigateBgChange(val)
}
const themeColorChange = val => {
  addChangeArray('themeColor', val)
}
const customColorChange = val => {
  addChangeArray('customColor', val)
}
const resetLoginForm = (reset2Default?: boolean) => {
  for (const key in loginForm) {
    loginForm[key] = defaultLoginForm[key]
  }
  clearFiles(['web', 'login', 'bg'])
  if (reset2Default) {
    addChangeArray('web', '', 'file')
    addChangeArray('login', '', 'file')
    addChangeArray('bg', '', 'file')
    web.value = ''
    login.value = ''
    bg.value = ''
  }
}
const resetTopForm = (reset2Default?: boolean) => {
  for (const key in topForm) {
    topForm[key] = defaultTopForm[key]
  }
  clearFiles(['navigate'])
  if (reset2Default) {
    addChangeArray('navigate', '', 'file')
    navigate.value = ''
  }
}
const uploadImg = options => {
  const file = options.file
  if (file['flag'] === 'web') {
    web.value = URL.createObjectURL(file)
  } else if(file['flag'] === 'bg') {
    bg.value = URL.createObjectURL(file)
  } else if(file['flag'] === 'login') {
    login.value = URL.createObjectURL(file)
  } else if(file['flag'] === 'navigate') {
    navigate.value = URL.createObjectURL(file)
  }
}
const beforeUpload = (file, type) => {
  addChangeArray(type, file.uid, 'file')
  let len = fileList.value?.length
  let match = false
  file.flag = type
  while (len--) {
    const tfile = fileList.value[len]
    if (type == tfile['flag']) {
      fileList.value[len] = file
      match = true
    }
  }
  if (!match) {
    fileList.value?.push(file)
  }
  return true
}

const clearFiles = (array?: string[]) => {
  if (!array?.length || !fileList.value?.length) {
    fileList.value = []
    return
  }
  let len = fileList.value.length
  while (len--) {
    const file = fileList.value[len]
    if (array.includes(file['flag'])) {
      fileList.value.splice(len, 1)
    }
  }
}

const getHeight = () => {
  const dom = document.getElementsByClassName('navigate-preview')
  const width = dom[0].clientWidth
  navigateHeight.value = parseInt((width * 0.625).toString())
}

onMounted(() => {
  init()
  nextTick(() => {
    getHeight()
  })
  window.addEventListener('resize', getHeight)
})
onUnmounted(() => {
  window.removeEventListener('resize', getHeight)
})
</script>

<style lang="less" scoped>
.router-title {
  color: #1f2329;
  font-feature-settings: "clig" off, "liga" off;
  font-family: "阿里巴巴普惠体 3.0 55 Regular L3";
  font-size: 20px;
  font-style: normal;
  font-weight: 500;
  line-height: 28px;
  margin-top: 6px;
}
.appearance-table__content {
  width: 100%;
  min-width: 840px;
  margin-top: 16px;
  overflow-y: auto;
  height: calc(100vh - 180px);
  box-sizing: border-box;

  :deep(.ed-form-item__error) {
    top: 88%;
  }

  .theme,
  .login,
  .setting {
    background: var(--ContentBG, #ffffff);
    padding: 24px;
    width: 100%;
    border-radius: 4px;

    & > :nth-child(1) {
      font-size: 16px;
      font-weight: 500;
      line-height: 24px;
    }
  }

  .theme {
    .navigate-bg {
      font-size: 14px;
      font-weight: 400;
      line-height: 22px;
      margin: 16px 0 8px 0;
    }
    .theme-bg {
      font-size: 14px;
      font-weight: 400;
      line-height: 22px;
      margin: 16px 0 6px 0;
    }

    .color-type {
      display: flex;
      .color-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        padding-top: 10px;
        width: 258px;
        height: 184px;
        border-radius: 4px;
        border: 1px solid #dee0e3;
        background-color: #f5f6f7;
        margin-right: 17px;
        &:hover {
          cursor: pointer;
        }
        img {
          width: 180px;
          height: 120px;
        }

        .color-item-label {
          height: 40px;
          width: 100%;
          border-top: 1px solid #dddedf;
          display: flex;
          align-items: center;
          padding-left: 12px;
          background-color: #fff;
          border-bottom-left-radius: 4px;
          border-bottom-right-radius: 4px;
        }
        &.active {
          border-color: var(--ed-color-primary);
          .color-item-label {
            background-color: #ebf1ff;
          }
        }
      }
    }

    .theme-color {
      font-size: 14px;
      font-weight: 400;
      line-height: 22px;
    }

    .custom-color {
      font-size: 12px;
      font-weight: 400;
      line-height: 20px;
      margin: 8px 0;
    }
  }

  .login,
  .setting {
    margin-top: 16px;
  }

  .login {
    .page-preview {
      background-color: #f5f6f7;
      margin-top: 16px;
      padding: 16px;
      border-radius: 4px;
      .title {
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        .left {
          font-size: 14px;
          font-weight: 500;
          line-height: 22px;
        }
      }

      .page-setting {
        display: flex;
        justify-content: space-between;
        .page-content {
          width: calc(100% - 378px);
          .navigate-preview {
            height: calc(100% - 28px);
            .light-head {
              background-color: #ffffff !important;
              box-shadow: 0px 0.5px 0px 0px #1f232926 !important;
              .ed-divider {
                border-color: #1f232926 !important;
              }
              .logo {
                color: #3371ff !important;
              }
            }
            .navigate-head {
              height: 45px;
              margin-bottom: 1px;
              display: flex;
              align-items: center;
              background-color: #050e21;
              padding: 0 15px;
              .logo {
                width: 120px;
                height: 28px;
                color: #fff;
              }

              .ed-divider {
                margin: 0 17px;
                border-color: rgba(255, 255, 255, 0.3);
              }
            }
            .navigate-content {
              height: calc(100% - 45px);
              background-color: #fff;
            }
          }
          .tips-page {
            font-size: 14px;
            font-weight: 400;
            line-height: 22px;
            color: #8f959e;
            margin-top: 6px;
          }
        }

        .config-list {
          width: 378px;
          margin-left: 16px;

          .config-item {
            height: 104px;
            margin-bottom: 8px;
            padding: 16px;
            border-radius: 4px;
            border: 1px solid #dee0e3;
            background: #fff;
            .config-logo {
              display: flex;
              align-items: center;
              justify-content: space-between;
              margin-bottom: 8px;
              .logo {
                font-size: 14px;
                font-weight: 400;
                line-height: 22px;
              }
              .ed-button {
                min-width: 64px;
                height: 28px;
                line-height: 28px;
                padding: 4px 7px;
                font-size: 12px;
                font-weight: 400;
              }
            }

            .tips {
              font-size: 12px;
              font-weight: 400;
              line-height: 18px;
              white-space: pre-wrap;
              color: #8f959e;
            }
          }

          .page-Form {
            .form-tips {
              font-size: 14px;
              font-weight: 400;
              line-height: 22px;
              color: #8f959e;
            }

            .ed-form-item {
              margin-bottom: 8px;
            }
            .appearance-radio-item {
              :deep(.ed-form-item__content) {
                padding-left: 8px;
                padding-right: 8px;
                // background-color: var(--ed-input-bg-color, var(--ed-fill-color-blank));
                background-image: none;
                border-radius: var(--ed-input-border-radius, var(--ed-border-radius-base));
                transition: var(--ed-transition-box-shadow);
                box-shadow: 0 0 0 1px var(--ed-input-border-color, var(--ed-border-color)) inset;
              }
            }
          }
        }
      }
    }
  }
}
.appearance-foot {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  height: 64px;
  background: var(--ContentBG, #ffffff);
  box-shadow: 0px -2px 4px 0px #1F232914;
  margin-top: 1px;
}
</style>
