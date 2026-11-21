<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LicenseInfo } from '@/api/types'
import type { UploadFile, UploadInstance } from 'element-plus'
import LicenseApi from '@/api/admin/auth/license'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import { useStore } from '@/stores/admin'
import { perm } from '@/permission'

defineOptions({ name: 'AboutDialog' })

const { t } = useI18n({ useScope: 'global' })

const { auth } = useStore()
const dialogVisible = ref(false)
const loading = ref(false)
const licenseInfo = ref<LicenseInfo | null>(null)
const licenseUpdated = ref(false)
const uploadRef = ref<UploadInstance>()
const copyrightYear = new Date().getFullYear()

// 版本与授权信息展示。
const editionText = computed(() => {
  const edition = auth.baseProfile?.edition
  if (edition === 'PE') return t('layout.about.editions.professional')
  if (edition === 'EE') return t('layout.about.editions.enterprise')
  return t('layout.about.editions.community')
})

const expirationNotice = computed(() => {
  if (!licenseInfo.value?.expired) return null
  const remainingTime = new Date(licenseInfo.value.expired).getTime() - Date.now()
  if (!Number.isFinite(remainingTime)) return null
  if (remainingTime < 0) return { text: t('layout.about.expiration.expired'), expired: true }
  if (remainingTime < 60000) return { text: t('layout.about.expiration.soon'), expired: false }
  if (remainingTime < 3600000) return { text: t('layout.about.expiration.minutes', { count: Math.floor(remainingTime / 60000) }), expired: false }
  if (remainingTime < 86400000) return { text: t('layout.about.expiration.hours', { count: Math.floor(remainingTime / 3600000) }), expired: false }
  if (remainingTime <= 7 * 86400000)
    return { text: t('layout.about.expiration.days', { count: Math.floor(remainingTime / 86400000) }), expired: false }
  return null
})

const licenseFields = computed(() => [
  { key: 'corporation', label: t('layout.about.fields.corporation'), value: licenseInfo.value?.corporation || '-' },
  { key: 'expired', label: t('layout.about.fields.expiresAt'), value: licenseInfo.value?.expired || '-' },
  { key: 'edition', label: t('layout.about.fields.edition'), value: editionText.value },
  { key: 'version', label: t('layout.about.fields.version'), value: auth.baseProfile?.version || '-' },
  { key: 'serialNo', label: t('layout.about.fields.serialNo'), value: licenseInfo.value?.serialNo || '-' },
  { key: 'remark', label: t('layout.about.fields.remark'), value: licenseInfo.value?.remark || '-' },
])

function loadLicense() {
  return LicenseApi.getLicense().then((profile) => {
    licenseInfo.value = profile.license ?? null
  })
}

function open() {
  dialogVisible.value = true
  if (!auth.showXpack) return
  loading.value = true
  return loadLicense().finally(() => {
    loading.value = false
  })
}

// 更新成功后刷新授权展示，关闭弹窗时重新加载平台档案与权限。
function updateLicense(file: UploadFile) {
  if (!file.raw || loading.value) return
  const payload = new FormData()
  payload.append('license_file', file.raw)
  loading.value = true
  return LicenseApi.putLicense(payload)
    .then(() => {
      licenseUpdated.value = true
      // 上传期间已关闭弹窗时，也要应用最新授权。
      if (!dialogVisible.value) {
        window.location.reload()
        return
      }
      return loadLicense()
    })
    .finally(() => {
      loading.value = false
      uploadRef.value?.clearFiles()
    })
}

function handleClosed() {
  if (licenseUpdated.value) window.location.reload()
  licenseUpdated.value = false
  licenseInfo.value = null
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="dialogVisible"
    :title="t('layout.about.title')"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    @closed="handleClosed"
  >
    <div v-loading="loading" class="overflow-hidden rounded-xl border">
      <div class="flex-center h-30 bg-primary/10">
        <LogoFull :height="40" class="max-w-full!" />
      </div>
      <div class="p-6">
        <dl class="space-y-4">
          <template v-for="field in licenseFields" :key="field.key">
            <div class="grid grid-cols-[100px_minmax(0,1fr)] gap-x-4">
              <dt class="text-N600">{{ field.label }}</dt>
              <dd class="m-0 wrap-anywhere">
                {{ field.value }}
                <span v-if="field.key === 'expired' && expirationNotice" :class="expirationNotice.expired ? 'text-danger' : 'text-warning'">
                  （{{ expirationNotice.text }}）
                </span>
              </dd>
            </div>
          </template>
        </dl>
        <!-- 上传并更新 License -->
        <el-upload
          v-if="auth.showXpack && perm.system.other.license()"
          ref="uploadRef"
          class="mt-6"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :disabled="loading"
          :on-change="updateLicense"
        >
          <el-button type="primary" plain :loading="loading" :disabled="loading">{{ t('layout.about.updateLicense') }}</el-button>
        </el-upload>
      </div>
    </div>
    <p class="mb-0 mt-4 text-center text-sm text-N500">
      2014–{{ copyrightYear }} {{ t('layout.about.copyright') }} © {{ t('layout.about.company') }}
    </p>
  </MkDialog>
</template>
