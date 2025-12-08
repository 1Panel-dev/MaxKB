<template>
  <el-dialog
    v-model="aboutDialogVisible"
    class="about-dialog border-r-6"
    :class="!isDefaultTheme ? 'dialog-custom-header' : ''"
  >
    <template #header="{ titleId, titleClass }">
      <div class="logo flex-center" :id="titleId" :class="titleClass">
        <LogoFull height="59px"/>
      </div>
    </template>
    <div class="about-ui" v-loading="loading">
      <div class="flex">
        <span class="label">{{ $t('layout.about.authorize') }}</span
        ><span>{{ licenseInfo?.corporation || '-' }}</span>
      </div>
      <div class="flex">
        <span class="label">{{ $t('layout.about.expiredTime') }}</span>
        <span
        >{{ licenseInfo?.expired || '-' }}
          <span class="color-danger"
                v-if="licenseInfo?.expired && fromNowDate(licenseInfo?.expired)"
          >（{{ fromNowDate(licenseInfo?.expired) }}）</span>
        </span
        >
      </div>
      <div class="flex">
        <span class="label">{{ $t('layout.about.edition.label') }}</span>
        <span>{{
            editionText
          }}</span>
      </div>
      <div class="flex">
        <span class="label">{{ $t('layout.about.version') }}</span
        ><span>{{ user.version }}</span>
      </div>
      <div class="flex">
        <span class="label">{{ $t('layout.about.serialNo') }}</span
        ><span>{{ licenseInfo?.serialNo || '-' }}</span>
      </div>
      <div class="flex">
        <span class="label">{{ $t('layout.about.remark') }}</span
        ><span>{{ licenseInfo?.remark || '-' }}</span>
      </div>
      <div class="mt-16 flex align-center" v-if="user.showXpack()">
        <el-upload
          ref="uploadRef"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="onChange"
          v-if="hasPermission([
            RoleConst.ADMIN,
            PermissionConst.ABOUT_UPDATE
          ],'OR')"
        >
          <el-button class="border-primary mr-16"
          >{{ $t('layout.about.update') }} License
          </el-button
          >
        </el-upload>
      </div>
    </div>
    <div class="border-t text-center mt-16 p-16 pb-0">
      <el-text type="info">{{ $t('layout.copyright') }}</el-text>
    </div>
  </el-dialog>
</template>
<script setup lang="ts">
import {ref, computed, watch} from 'vue'
import licenseApi from '@/api/system/license'
import {fromNowDate} from '@/utils/time'
import {Role} from '@/utils/permission/type'
import useStore from '@/stores'
import { t } from '@/locales'
import { hasPermission } from '@/utils/permission'
import { PermissionConst, RoleConst } from '@/utils/permission/data'
const {user, theme} = useStore()
const isDefaultTheme = computed(() => {
  return theme.isDefaultTheme()
})

const aboutDialogVisible = ref(false)
const loading = ref(false)
const licenseInfo = ref<any>(null)
const isUpdate = ref(false)

watch(aboutDialogVisible, (bool) => {
  if (!bool) {
    if (isUpdate.value) {
      window.location.reload()
    }
    isUpdate.value = false
  }
})
const open = () => {
  if (user.showXpack()) {
    getLicenseInfo()
  }

  aboutDialogVisible.value = true
}


const onChange = (file: any) => {
  const fd = new FormData()
  fd.append('license_file', file.raw)
  licenseApi.putLicense(fd, loading).then((res: any) => {
    getLicenseInfo()
    isUpdate.value = true
  })
}

const editionText = computed(() => {
  if (!user) return '-'
  if (user.getEditionName() === 'PE') {
    return t('layout.about.edition.professional')
  } else if (user.getEditionName() === 'EE') {
    return t('layout.about.edition.enterprise')
  } else {
    return t('layout.about.edition.community')
  }
})
function getLicenseInfo() {
  licenseApi.getLicense(loading).then((res: any) => {
    licenseInfo.value = res.data?.license
  })
}

defineExpose({open})
</script>
<style lang="scss" scope>
.about-dialog {
  padding: 0 0 24px 0;
  width: 620px;
  font-weight: 400;

  .el-dialog__header {
    background: var(--app-header-bg-color);
    margin-right: 0;
    height: 140px;
    box-sizing: border-box;
    border-radius: 4px 4px 0 0;

    &.show-close {
      padding-right: 0;
    }
  }

  .el-dialog__title {
    height: 140px;
    box-sizing: border-box;
  }

  .about-ui {
    margin: 0 auto;
    font-weight: 400;
    font-size: 14px;
    margin-top: 24px;
    line-height: 36px;
    padding: 0 40px;

    .label {
      width: 150px;
      text-align: left;
      color: var(--app-text-color-secondary);
    }
  }

  &.dialog-custom-header {
    .el-dialog__header {
      background: var(--el-color-primary-light-9) !important;
    }
  }
}
</style>
