<template>
  <el-dialog
    title="显示设置"
    width="900"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    align-center
  >
    <el-row :gutter="8">
      <el-col :span="12">
        <div class="setting-preview border border-r-4 mr-16">
          <div class="setting-preview-container">
            <div class="setting-preview-header" :class="!isDefaultTheme ? 'custom-header' : ''">
              <div class="flex-between">
                <div class="flex align-center">
                  <div class="mr-12 ml-24 flex">
                    <AppAvatar
                      v-if="isAppIcon(detail?.icon)"
                      shape="square"
                      :size="32"
                      style="background: none"
                    >
                      <img :src="detail?.icon" alt="" />
                    </AppAvatar>
                    <AppAvatar
                      v-else-if="detail?.name"
                      :name="detail?.name"
                      pinyinColor
                      shape="square"
                      :size="32"
                    />
                  </div>

                  <h4>
                    {{ detail?.name || $t('views.application.applicationForm.form.appName.label') }}
                  </h4>
                </div>
                <div class="mr-16">
                  <el-button link>
                    <AppIcon
                      :iconName="'app-magnify'"
                      class="color-secondary"
                      style="font-size: 20px"
                    ></AppIcon>
                  </el-button>
                  <el-button link>
                    <el-icon :size="20" class="color-secondary"><Close /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <div class="float_icon">
            <el-image
              v-if="imgUrl.float_icon"
              :src="imgUrl.float_icon"
              alt=""
              fit="cover"
              style="width: 40px; height: 40px; display: block"
            />
            <img
              v-else
              src="@/assets/logo/logo.svg"
              height="50px"
              style="width: 40px; height: 40px; display: block"
            />
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <el-form ref="displayFormRef" :model="form">
          <el-row class="w-full mb-8">
            <el-col :span="12">
              <h5 class="mb-8">自定义主题色</h5>
              <el-color-picker v-model="customColor" @change="customColorHandle"
            /></el-col>
            <el-col :span="12">
              <h5 class="mb-8">头部标题字体颜色</h5>
              <el-color-picker v-model="customColor" @change="customColorHandle" />
            </el-col>
          </el-row>
          <el-card shadow="never" class="mb-8">
            <div class="flex-between mb-8">
              <span class="lighter">提问用户头像</span>

              <el-upload
                ref="uploadRef"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="(file: any, fileList: any) => onChange(file, fileList, 'avatar')"
              >
                <el-button size="small"> 替换 </el-button>
              </el-upload>
            </div>
            <el-text type="info" size="small"
              >建议尺寸 64*64，支持 JPG、PNG, GIF，大小不超过 10 MB</el-text
            >
          </el-card>
          <el-card shadow="never" class="mb-8">
            <div class="flex-between mb-8">
              <span class="lighter">AI 回复头像</span>

              <el-upload
                ref="uploadRef"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="(file: any, fileList: any) => onChange(file, fileList, 'avatar')"
              >
                <el-button size="small"> 替换 </el-button>
              </el-upload>
            </div>
            <el-text type="info" size="small"
              >建议尺寸 32*32，支持 JPG、PNG, GIF，大小不超过 10 MB</el-text
            >
          </el-card>
          <el-card shadow="never" class="mb-8">
            <div class="flex-between mb-8">
              <span class="lighter">浮窗入口图标</span>
              <el-upload
                ref="uploadRef"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*"
                :on-change="(file: any, fileList: any) => onChange(file, fileList, 'float_icon')"
              >
                <el-button size="small"> 替换 </el-button>
              </el-upload>
            </div>
            <el-text type="info" size="small">
              建议尺寸 64*64，支持 JPG、PNG, GIF，大小不超过 10 MB
            </el-text>
            <div class="border-t mt-8">
              <div class="flex-between mb-8">
                <span class="lighter">图标默认位置</span>
                <el-checkbox v-model="form.draggable" label="可拖拽位置" />
              </div>
              <el-row :gutter="8" class="w-full mb-8">
                <el-col :span="12">
                  <div class="flex align-center">
                    <el-select v-model="form.show_source" style="width: 80px">
                      <el-option label="右" value="右" />
                      <el-option label="左" value="左" />
                    </el-select>
                    <el-input-number
                      v-model="form.show_source"
                      :min="0"
                      controls-position="right"
                    />
                    <span class="ml-4">px</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="flex align-center">
                    <el-select v-model="form.show_source" style="width: 80px">
                      <el-option label="下" value="下" />
                      <el-option label="上" value="上" />
                    </el-select>
                    <el-input-number
                      v-model="form.show_source"
                      :min="0"
                      controls-position="right"
                    />
                    <span class="ml-4">px</span>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-card>

          <el-space direction="vertical" alignment="start" :size="2">
            <el-checkbox v-model="form.show_source" label="显示知识来源" />
            <el-checkbox v-model="form.show_history" label="显示历史记录" />
            <el-checkbox v-model="form.show_guide" label="显示引导图（浮窗模式）" />
            <el-checkbox v-model="form.show_guide" label="免责声明" />
          </el-space>
        </el-form>
      </el-col>
    </el-row>

    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click.prevent="resetForm" link>恢复默认 </el-button>
        <el-button @click.prevent="dialogVisible = false"
          >{{ $t('views.applicationOverview.appInfo.LimitDialog.cancelButtonText') }}
        </el-button>
        <el-button type="primary" @click="submit(displayFormRef)" :loading="loading">
          {{ $t('views.applicationOverview.appInfo.LimitDialog.saveButtonText') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules, UploadFiles } from 'element-plus'
import { isAppIcon } from '@/utils/application'
import applicationXpackApi from '@/api/application-xpack'
import { MsgSuccess, MsgError } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
const { user } = useStore()

const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const defaultSetting = {
  show_source: false,
  show_history: true,
  draggable: true,
  show_guide: true,
  avatar: '',
  float_icon: ''
}

const displayFormRef = ref()
const form = ref<any>({
  show_source: false
})

const xpackForm = ref<any>({
  show_source: false,
  show_history: false,
  draggable: false,
  show_guide: false,
  avatar: '',
  float_icon: ''
})

const imgUrl = ref<any>({
  avatar: '',
  float_icon: ''
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const detail = ref<any>(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false
    }
    imgUrl.value = {
      avatar: '',
      float_icon: ''
    }
  }
})

function resetForm() {
  form.value = {
    ...defaultSetting
  }
  imgUrl.value = {
    avatar: '',
    float_icon: ''
  }
}

const onChange = (file: any, fileList: UploadFiles, attr: string) => {
  //1、判断文件大小是否合法，文件限制不能大于 10 MB
  const isLimit = file?.size / 1024 / 1024 < 10
  if (!isLimit) {
    // @ts-ignore
    MsgError(t('views.applicationOverview.appInfo.EditAvatarDialog.fileSizeExceeded'))
    return false
  } else {
    xpackForm.value[attr] = file.raw
    imgUrl.value[attr] = URL.createObjectURL(file.raw)
  }
}

const open = (data: any, content: any) => {
  detail.value = content
  xpackForm.value.show_source = data.show_source
  xpackForm.value.show_history = data.show_history
  xpackForm.value.draggable = data.draggable
  xpackForm.value.show_guide = data.show_guide
  xpackForm.value.avatar = data.avatar
  xpackForm.value.float_icon = data.float_icon
  imgUrl.value.avatar = data.avatar
  imgUrl.value.float_icon = data.float_icon
  form.value = xpackForm.value

  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      let fd = new FormData()
      Object.keys(form.value).map((item) => {
        fd.append(item, form.value[item])
      })
      applicationXpackApi.putAccessToken(id as string, fd, loading).then((res) => {
        emit('refresh')
        // @ts-ignore
        MsgSuccess(t('views.applicationOverview.appInfo.LimitDialog.settingSuccessMessage'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.setting-preview {
  background: #f5f6f7;
  height: 570px;
  position: relative;
  .float_icon {
    position: absolute;
    right: 8px;
    bottom: 15px;
  }
  .setting-preview-container {
    position: absolute;
    left: 16px;
    top: 25px;
    border-radius: 8px;
    border: 1px solid #ffffff;
    background: linear-gradient(
        188deg,
        rgba(235, 241, 255, 0.2) 39.6%,
        rgba(231, 249, 255, 0.2) 94.3%
      ),
      #eff0f1;
    box-shadow: 0px 4px 8px 0px rgba(31, 35, 41, 0.1);
    overflow: hidden;
    width: 330px;
    height: 520px;
    .setting-preview-header {
      background: var(--app-header-bg-color);
      height: var(--app-header-height);
      line-height: var(--app-header-height);
      box-sizing: border-box;
      border-bottom: 1px solid var(--el-border-color);
    }
  }
}
</style>
