<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.SettingDisplayDialog.dialogTitle')"
    width="900"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    align-center
    class="display-setting-dialog"
  >
    <template #header="{ titleId, titleClass }">
      <div class="flex-between mb-8">
        <h4 :id="titleId" :class="titleClass">
          {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.dialogTitle') }}
        </h4>
        <div class="flex align-center">
          <el-button type="primary" @click.prevent="resetForm" link>
            <el-icon class="mr-4">
              <Refresh />
            </el-icon>
            {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.restoreDefault') }}
          </el-button>
          <el-divider direction="vertical" />
        </div>
      </div>
    </template>

    <div class="flex">
      <div class="setting-preview border border-r-4 mr-16" style="min-width: 400px">
        <div class="setting-preview-container">
          <div class="setting-preview-header" :style="customStyle">
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

                <h4 class="ellipsis">
                  {{ detail?.name || $t('views.application.applicationForm.form.appName.label') }}
                </h4>
              </div>
              <div class="mr-16">
                <el-button link>
                  <AppIcon
                    :iconName="'app-magnify'"
                    :style="{
                      color: xpackForm.custom_theme?.header_font_color
                    }"
                    style="font-size: 20px"
                  ></AppIcon>
                </el-button>
                <el-button link>
                  <el-icon
                    :size="20"
                    class="color-secondary"
                    :style="{
                      color: xpackForm.custom_theme?.header_font_color
                    }"
                  >
                    <Close />
                  </el-icon>
                </el-button>
              </div>
            </div>
          </div>
          <div>
            <div class="p-16" style="position: relative">
              <div class="flex">
                <div class="avatar" v-if="xpackForm.show_avatar">
                  <el-image
                    v-if="imgUrl.avatar"
                    :src="imgUrl.avatar"
                    alt=""
                    fit="cover"
                    style="width: 28px; height: 28px; display: block"
                  />
                  <LogoIcon
                    v-else
                    height="28px"
                    style="width: 28px; height: 28px; display: block"
                  />
                </div>

                <img
                  src="@/assets/display-bg2.png"
                  alt=""
                  :width="
                    xpackForm.show_avatar
                      ? xpackForm.show_user_avatar
                        ? '232px'
                        : '270px'
                      : xpackForm.show_user_avatar
                        ? '260px'
                        : '300px'
                  "
                />
              </div>
              <div class="flex mt-4" style="justify-content: flex-end">
                <img
                  src="@/assets/display-bg3.png"
                  alt=""
                  :width="
                    xpackForm.show_user_avatar
                      ? xpackForm.show_avatar
                        ? '227px'
                        : '255px'
                      : xpackForm.show_avatar
                        ? '265px'
                        : '292px'
                  "
                  style="object-fit: contain"
                />
                <div class="avatar ml-8" v-if="xpackForm.show_user_avatar">
                  <el-image
                    v-if="imgUrl.user_avatar"
                    :src="imgUrl.user_avatar"
                    alt=""
                    fit="cover"
                    style="width: 28px; height: 28px; display: block"
                  />
                  <AppAvatar v-else>
                    <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
                  </AppAvatar>
                </div>
              </div>
            </div>
            <div
              style="position: absolute; bottom: 0; padding-bottom: 8px; box-sizing: border-box"
              class="p-16 text-center w-full"
            >
              <img src="@/assets/display-bg1.png" alt="" class="w-full" />
              <el-text type="info" v-if="xpackForm.disclaimer" class="mt-8" style="font-size: 12px">
                <auto-tooltip :content="xpackForm.disclaimer_value">
                  {{ xpackForm.disclaimer_value }}
                </auto-tooltip>
              </el-text>
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
            src="/MaxKB.gif"
            height="50px"
            style="width: 40px; height: 40px; display: block"
          />
        </div>
      </div>

      <el-form ref="displayFormRef" :model="xpackForm">
        <el-row class="w-full mb-8">
          <el-col :span="12">
            <h5 class="mb-8">
              {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.customThemeColor') }}
            </h5>
            <div>
              <el-color-picker v-model="xpackForm.custom_theme.theme_color" />
              {{
                !xpackForm.custom_theme.theme_color
                  ? $t('views.applicationOverview.appInfo.SettingDisplayDialog.default')
                  : ''
              }}
            </div>
          </el-col>
          <el-col :span="12">
            <h5 class="mb-8">
              {{
                $t('views.applicationOverview.appInfo.SettingDisplayDialog.headerTitleFontColor')
              }}
            </h5>
            <el-color-picker v-model="xpackForm.custom_theme.header_font_color" />
          </el-col>
        </el-row>
        <el-row class="w-full mb-8">
          <h5 class="mb-8">
            {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.languageLabel') }}
          </h5>
          <el-select v-model="xpackForm.language" clearable>
            <el-option
              v-for="item in langList"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-row>
        <el-card shadow="never" class="mb-8">
          <div class="flex-between mb-8">
            <span class="lighter">{{
              $t('views.applicationOverview.appInfo.SettingDisplayDialog.AIAvatar')
            }}</span>
            <span class="flex align-center">
              <el-checkbox v-model="xpackForm.show_avatar">{{
                $t('views.applicationOverview.appInfo.SettingDisplayDialog.display')
              }}</el-checkbox>
              <el-upload
                class="ml-8"
                ref="uploadRef"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/jpeg, image/png, image/gif"
                :on-change="(file: any, fileList: any) => onChange(file, fileList, 'avatar')"
              >
                <el-button size="small">
                  {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.replace') }}
                </el-button>
              </el-upload>
            </span>
          </div>
          <el-text type="info" size="small">
            {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.imageMessage') }}
          </el-text>
        </el-card>
        <el-card shadow="never" class="mb-8">
          <div class="flex-between mb-8">
            <span class="lighter">{{
              $t('views.applicationOverview.appInfo.SettingDisplayDialog.askUserAvatar')
            }}</span>
            <span class="flex align-center">
              <el-checkbox v-model="xpackForm.show_user_avatar">
                {{
                  $t('views.applicationOverview.appInfo.SettingDisplayDialog.display')
                }}</el-checkbox
              >
              <el-upload
                class="ml-8"
                ref="uploadRef"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                accept="image/jpeg, image/png, image/gif"
                :on-change="(file: any, fileList: any) => onChange(file, fileList, 'user_avatar')"
              >
                <el-button size="small">
                  {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.replace') }}
                </el-button>
              </el-upload>
            </span>
          </div>
          <el-text type="info" size="small"
            >{{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.imageMessage') }}
          </el-text>
        </el-card>
        <el-card shadow="never" class="mb-8">
          <div class="flex-between mb-8">
            <span class="lighter">{{
              $t('views.applicationOverview.appInfo.SettingDisplayDialog.floatIcon')
            }}</span>
            <el-upload
              ref="uploadRef"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/jpeg, image/png, image/gif"
              :on-change="(file: any, fileList: any) => onChange(file, fileList, 'float_icon')"
            >
              <el-button size="small">
                {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.replace') }}
              </el-button>
            </el-upload>
          </div>
          <el-text type="info" size="small">
            {{ $t('views.applicationOverview.appInfo.SettingDisplayDialog.imageMessage') }}
          </el-text>
          <div class="border-t mt-8">
            <div class="flex-between mb-8">
              <span class="lighter">{{
                $t('views.applicationOverview.appInfo.SettingDisplayDialog.iconDefaultPosition')
              }}</span>
              <el-checkbox
                v-model="xpackForm.draggable"
                :label="
                  $t('views.applicationOverview.appInfo.SettingDisplayDialog.draggablePosition')
                "
              />
            </div>
            <el-row :gutter="8" class="w-full mb-8">
              <el-col :span="12">
                <div class="flex align-center">
                  <el-select v-model="xpackForm.float_location.x.type" style="width: 80px">
                    <el-option
                      :label="
                        $t(
                          'views.applicationOverview.appInfo.SettingDisplayDialog.iconPosition.left'
                        )
                      "
                      value="left"
                    />
                    <el-option
                      :label="
                        $t(
                          'views.applicationOverview.appInfo.SettingDisplayDialog.iconPosition.right'
                        )
                      "
                      value="right"
                    />
                  </el-select>
                  <el-input-number
                    v-model="xpackForm.float_location.x.value"
                    :min="0"
                    :step="1"
                    :precision="0"
                    :value-on-clear="0"
                    step-strictly
                    controls-position="right"
                  />
                  <span class="ml-4">px</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="flex align-center">
                  <el-select v-model="xpackForm.float_location.y.type" style="width: 80px">
                    <el-option
                      :label="
                        $t(
                          'views.applicationOverview.appInfo.SettingDisplayDialog.iconPosition.top'
                        )
                      "
                      value="top"
                    />
                    <el-option
                      :label="
                        $t(
                          'views.applicationOverview.appInfo.SettingDisplayDialog.iconPosition.bottom'
                        )
                      "
                      value="bottom"
                    />
                  </el-select>
                  <el-input-number
                    v-model="xpackForm.float_location.y.value"
                    :min="0"
                    :step="1"
                    :precision="0"
                    :value-on-clear="0"
                    step-strictly
                    controls-position="right"
                  />
                  <span class="ml-4">px</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-space direction="vertical" alignment="start" :size="2">
          <el-checkbox
            v-model="xpackForm.show_source"
            :label="
              isWorkFlow(detail.type)
                ? $t('views.applicationOverview.appInfo.SettingDisplayDialog.showExecutionDetail')
                : $t('views.applicationOverview.appInfo.SettingDisplayDialog.showSourceLabel')
            "
          />
          <el-checkbox
            v-model="xpackForm.show_history"
            :label="$t('views.applicationOverview.appInfo.SettingDisplayDialog.showHistory')"
          />
          <el-checkbox
            v-model="xpackForm.show_guide"
            :label="$t('views.applicationOverview.appInfo.SettingDisplayDialog.displayGuide')"
          />
          <el-checkbox
            v-model="xpackForm.disclaimer"
            :label="$t('views.applicationOverview.appInfo.SettingDisplayDialog.disclaimer')"
            @change="changeDisclaimer"
          />
          <span v-if="xpackForm.disclaimer"
            ><el-tooltip :content="xpackForm.disclaimer_value" placement="top">
              <el-input
                v-model="xpackForm.disclaimer_value"
                style="width: 422px; margin-bottom: 10px"
                @change="changeValue"
                :maxlength="128"
              /> </el-tooltip
          ></span>
        </el-space>
      </el-form>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(displayFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules, UploadFiles } from 'element-plus'
import { isAppIcon, isWorkFlow } from '@/utils/application'
import applicationXpackApi from '@/api/application-xpack'
import { MsgSuccess, MsgError } from '@/utils/message'
import { langList, t } from '@/locales'
import useStore from '@/stores'
import { cloneDeep } from 'lodash'

const { user } = useStore()

const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const defaultSetting = {
  show_source: false,
  language: '',
  show_history: true,
  draggable: true,
  show_guide: true,
  avatar: '',
  avatar_url: '',
  float_icon: '',
  float_icon_url: '',
  user_avatar: '',
  user_avatar_url: '',
  disclaimer: false,
  disclaimer_value: t('views.applicationOverview.appInfo.SettingDisplayDialog.disclaimerValue'),
  custom_theme: {
    theme_color: '',
    header_font_color: '#1f2329'
  },
  float_location: {
    y: { type: 'bottom', value: 30 },
    x: { type: 'right', value: 0 }
  },
  show_avatar: true,
  show_user_avatar: false
}

const displayFormRef = ref()

const xpackForm = ref<any>({
  show_source: false,
  language: '',
  show_history: false,
  draggable: false,
  show_guide: false,
  avatar: '',
  avatar_url: '',
  float_icon: '',
  float_icon_url: '',
  user_avatar: '',
  user_avatar_url: '',
  disclaimer: false,
  disclaimer_value: t('views.applicationOverview.appInfo.SettingDisplayDialog.disclaimerValue'),
  custom_theme: {
    theme_color: '',
    header_font_color: '#1f2329'
  },
  float_location: {
    y: { type: 'bottom', value: 30 },
    x: { type: 'right', value: 0 }
  },
  show_avatar: true,
  show_user_avatar: false
})

const imgUrl = ref<any>({
  avatar: '',
  float_icon: '',
  user_avatar: ''
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

const detail = ref<any>(null)

const customStyle = computed(() => {
  return {
    background: xpackForm.value.custom_theme?.theme_color,
    color: xpackForm.value.custom_theme?.header_font_color
  }
})

function resetForm() {
  xpackForm.value = cloneDeep(defaultSetting)
  imgUrl.value = {
    avatar: '',
    float_icon: '',
    user_avatar: ''
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
    xpackForm.value[`${attr}_url`] = ''
  }
}

const open = (data: any, content: any) => {
  detail.value = content
  xpackForm.value.show_source = data.show_source
  xpackForm.value.show_history = data.show_history
  xpackForm.value.language = data.language
  xpackForm.value.draggable = data.draggable
  xpackForm.value.show_guide = data.show_guide
  imgUrl.value.avatar = data.avatar
  imgUrl.value.float_icon = data.float_icon
  imgUrl.value.user_avatar = data.user_avatar
  xpackForm.value.disclaimer = data.disclaimer
  xpackForm.value.disclaimer_value = data.disclaimer_value
  if (
    xpackForm.value.disclaimer_value ===
    t('views.applicationOverview.appInfo.SettingDisplayDialog.disclaimerValue')
  ) {
    xpackForm.value.disclaimer_value = t(
      'views.applicationOverview.appInfo.SettingDisplayDialog.disclaimerValue'
    )
  }
  xpackForm.value.avatar_url = data.avatar
  xpackForm.value.user_avatar_url = data.user_avatar
  xpackForm.value.float_icon_url = data.float_icon
  xpackForm.value.show_avatar = data.show_avatar
  xpackForm.value.show_user_avatar = data.show_user_avatar
  xpackForm.value.custom_theme = {
    theme_color: data.custom_theme?.theme_color || '',
    header_font_color: data.custom_theme?.header_font_color || '#1f2329'
  }
  xpackForm.value.float_location = data.float_location
  dialogVisible.value = true
}

const changeValue = (value: string) => {
  xpackForm.value.disclaimer_value = value
}

const changeDisclaimer = (value: boolean) => {
  xpackForm.value.disclaimer = value
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      let fd = new FormData()
      Object.keys(xpackForm.value).map((item) => {
        if (['custom_theme', 'float_location'].includes(item)) {
          fd.append(item, JSON.stringify(xpackForm.value[item]))
        } else {
          fd.append(item, xpackForm.value[item])
        }
      })
      applicationXpackApi.putAccessToken(id as string, fd, loading).then((res) => {
        emit('refresh')
        // @ts-ignore
        MsgSuccess(t('common.settingSuccess'))
        dialogVisible.value = false
      })
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss">
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
    background: var(--dialog-bg-gradient-color);
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

.display-setting-dialog {
  .el-dialog__header {
    padding-right: 8px;
  }

  .el-dialog__headerbtn {
    top: 8px;
  }
}
</style>
