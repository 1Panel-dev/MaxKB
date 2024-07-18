<template>
  <el-dialog
    v-model="aboutDialogVisible"
    class="about-dialog border-r-4"
    :class="!isDefaultTheme ? 'custom-header' : ''"
  >
    <template #header="{ titleId, titleClass }">
      <div class="logo flex-center" :id="titleId" :class="titleClass">
        <LogoFull height="59px" />
      </div>
    </template>
    <div class="about-ui" v-loading="loading">
      <div class="flex">
        <span class="label">授权给</span><span>{{ licenseInfo?.corporation || '-' }}</span>
      </div>
      <div class="flex">
        <span class="label">ISV</span><span>{{ licenseInfo?.isv || '-' }}</span>
      </div>
      <div class="flex">
        <span class="label">到期时间</span>
        <span
          >{{ licenseInfo?.expired || '-' }}
          <span class="danger" v-if="licenseInfo?.expired && fromNowDate(licenseInfo?.expired)"
            >（{{ fromNowDate(licenseInfo?.expired) }}）</span
          ></span
        >
      </div>
      <div class="flex">
        <span class="label">版本</span><span>{{ user.isXPack ? '专业版' : '社区版' }}</span>
      </div>
      <div class="flex">
        <span class="label">版本号</span
        ><span>{{ licenseInfo?.licenseVersion || user.version }}</span>
      </div>
      <div class="flex">
        <span class="label">序列号</span><span>{{ licenseInfo?.serialNo || '-' }}</span>
      </div>
      <div class="flex">
        <span class="label">备注</span><span>{{ licenseInfo?.remark || '-' }}</span>
      </div>

      <div class="mt-16 flex align-center" v-if="user.isXPack">
        <el-upload
          ref="uploadRef"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="onChange"
        >
          <el-button class="border-primary">更新 License</el-button>
        </el-upload>

        <el-button class="border-primary ml-16" @click="toSupport">获取技术支持</el-button>
      </div>
    </div>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import licenseApi from '@/api/license'
import { fromNowDate } from '@/utils/time'
import useStore from '@/stores'
const { user } = useStore()
const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})

const aboutDialogVisible = ref(false)
const loading = ref(false)
const licenseInfo = ref<any>(null)

const open = () => {
  if (user.isXPack) {
    getLicenseInfo()
  }

  aboutDialogVisible.value = true
}

const onChange = (file: any) => {
  let fd = new FormData()
  fd.append('license_file', file.raw)
  licenseApi.putLicense(fd, loading).then((res: any) => {
    getLicenseInfo()
  })
}
function getLicenseInfo() {
  licenseApi.getLicense(loading).then((res: any) => {
    licenseInfo.value = res.data?.license
  })
}

function toSupport() {
  const url = 'https://support.fit2cloud.com/'
  window.open(url, '_blank')
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.about-dialog {
  padding: 0 0 24px 0;
  width: 600px;
  font-weight: 400;
  .el-dialog__header {
    background: var(--app-header-bg-color);
    margin-right: 0;
    height: 140px;
    box-sizing: border-box;
    border-radius: 4px 4px 0 0;
  }
  .el-dialog__title {
    height: 140px;
    box-sizing: border-box;
  }
  .about-ui {
    width: 450px;
    margin: 0 auto;
    font-weight: 400;
    font-size: 14px;
    margin-top: 24px;
    line-height: 36px;

    .label {
      width: 150px;
      text-align: left;
      color: var(--app-text-color-secondary);
    }
  }
  &.custom-header {
    .el-dialog__header {
      background: var(--el-color-primary-light-9) !important;
    }
  }
}
</style>
