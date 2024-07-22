<template>
  <el-dialog title="显示设置" v-model="dialogVisible">
    <el-form label-position="top" ref="displayFormRef" :model="form">
      <el-form-item>
        <el-space direction="vertical" alignment="start">
          <el-checkbox v-model="form.show_source" label="显示知识来源" />
          <el-checkbox v-model="form.show_history" label="显示历史记录" />
          <el-checkbox v-model="form.draggable" label="可拖拽位置（浮窗模式）" />
          <el-checkbox v-model="form.show_guide" label="显示引导图（浮窗模式）" />
        </el-space>
      </el-form-item>
      <el-form-item label="对话头像">
        <div class="flex mt-8">
          <div class="border border-r-4 mr-16" style="width: 50px; height: 50px; padding: 8px">
            <img v-if="imgUrl.avatar" :src="imgUrl.avatar" alt="" height="50px" />
            <LogoIcon v-else height="50px" />
          </div>

          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="(file: any, fileList: any) => onChange(file, fileList, 'avatar')"
          >
            <el-button icon="Upload">{{
              $t('views.applicationOverview.appInfo.EditAvatarDialog.upload')
            }}</el-button>
            <template #tip>
              <div class="el-upload__tip info" style="margin-top: 0">
                建议尺寸 32*32，支持 JPG、PNG，大小不超过 200 KB
              </div>
            </template>
          </el-upload>
        </div>
      </el-form-item>
      <el-form-item label="浮窗入口图标">
        <div class="flex mt-8">
          <div class="border border-r-4 mr-16" style="width: 50px; height: 50px; padding: 8px">
            <img v-if="imgUrl.float_icon" :src="imgUrl.float_icon" alt="" height="50px" />
            <img v-else src="@/assets/logo/logo.svg" height="50px" />
          </div>

          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="(file: any, fileList: any) => onChange(file, fileList, 'float_icon')"
          >
            <el-button icon="Upload">{{
              $t('views.applicationOverview.appInfo.EditAvatarDialog.upload')
            }}</el-button>
            <template #tip>
              <div class="el-upload__tip info" style="margin-top: 0">
                建议尺寸 32*32，支持 JPG、PNG，大小不超过 200 KB
              </div>
            </template>
          </el-upload>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button v-if="user.isEnterprise()" type="primary" @click.prevent="resetForm" link
          >恢复默认
        </el-button>
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
import applicationApi from '@/api/application'
import applicationXpackApi from '@/api/application-xpack'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
const { user } = useStore()

const route = useRoute()
const {
  params: { id }
} = route

const emit = defineEmits(['refresh'])

const defaultSetting = {
  show_source: true,
  show_history: true,
  draggable: false,
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

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      show_source: false
    }
    imgUrl.value = {
      avatar: "",
      float_icon: ""
    }
  }
})

function resetForm() {
  form.value = {
    ...defaultSetting
  }
  imgUrl.value = {
    avatar: "",
    float_icon: ""
  }
}

const onChange = (file: any, fileList: UploadFiles, attr: string) => {
  //1、判断文件大小是否合法，文件限制不能大于 200KB
  const isLimit = file?.size / 1024 < 200
  if (!isLimit) {
    // @ts-ignore
    MsgError(t('views.applicationOverview.appInfo.EditAvatarDialog.fileSizeExceeded'))
    return false
  }
  xpackForm.value[attr] = file.raw
  imgUrl.value[attr] = URL.createObjectURL(file.raw)
}

const open = (data: any) => {
  if (user.isEnterprise()) {
    xpackForm.value.show_source = data.show_source
    xpackForm.value.show_history = data.show_history
    xpackForm.value.draggable = data.draggable
    xpackForm.value.show_guide = data.show_guide
    xpackForm.value.avatar = data.avatar
    xpackForm.value.float_icon = data.float_icon
    imgUrl.value.avatar = data.avatar
    imgUrl.value.float_icon = data.float_icon
    form.value = xpackForm.value
  } else {
    form.value.show_source = data.show_source
  }

  dialogVisible.value = true
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (user.isEnterprise()) {
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
      } else {
        const obj = {
          show_source: form.value.show_source
        }
        applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
          emit('refresh')
          // @ts-ignore
          MsgSuccess(t('views.applicationOverview.appInfo.LimitDialog.settingSuccessMessage'))
          dialogVisible.value = false
        })
      }
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
