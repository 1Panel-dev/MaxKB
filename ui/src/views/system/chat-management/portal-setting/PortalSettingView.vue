<script setup lang="ts">
import { computed, reactive, ref, useTemplateRef } from 'vue'
import PortalApi from '@/api/admin/system/chat-management/portal-setting.ts'
import type { PortalSetting, PortalSettingPayload } from '@/api/types'
import LogoIcon from '@/components/mk-logo/LogoIcon.vue'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import PortalPreview from './components/PortalPreview.vue'
import ButtonEditPortal from './components/ButtonEditPortal.vue'
import ButtonPortalAuthSetting from './components/ButtonPortalAuthSetting.vue'
import ButtonPortalCorsSetting from './components/ButtonPortalCorsSetting.vue'
import perm from '@/permission/index.ts'

type AccessField = 'enable_public_access' | 'enable_api' | 'enable_knowledge_base_api' | 'enable_auth' | 'enable_cors'

const portalSetting = reactive<PortalSetting>({
  id: '',
  name: '智能体门户',
  description: '',
  logo: '',
  tab_logo: '',
  enable_public_access: true,
  enable_api: true,
  enable_knowledge_base_api: true,
  enable_auth: false,
  auth_config: {
    login_value: ['LOCAL'],
    max_attempts: 1,
    failed_attempts: 5,
    lock_time: 10,
  },
  enable_cors: false,
  cors_config: {},
})
const saving = ref(false)
// 跨域地址暂存于页面，待接口协议确定后接入 cors_config。
const portalCorsOrigins = ref<string[]>([])

const portalAccessUrl = new URL('/portal', window.location.origin).href
const portalApiUrl = new URL('/api/portal', window.location.origin).href

/* 接口尚未接入，页面使用默认配置；保存回填时保留现有配置对象。 */
function savePortalSetting(payload: PortalSettingPayload | FormData) {
  // saving.value = true
  // return PortalApi.putPortalSetting(payload)
  //   .then((setting) => {
  //     Object.assign(portalSetting, setting)
  //     MsgSuccess('保存成功')
  //   })
  //   .finally(() => {
  //     saving.value = false
  //   })
}

function handleAccessChange(field: AccessField, value: string | number | boolean) {
  if (saving.value) return
  if (field === 'enable_auth' && value && !portalSetting.auth_config.login_value?.length) {
    authSettingButtonRef.value?.open(true)
    return
  }
  // 使用服务端确认的值渲染开关，失败时保留原配置。
  return savePortalSetting({ [field]: Boolean(value) })
}

/* 认证接口暂未接入，保存到当前页面配置供再次打开回填。 */
function savePortalAuthSetting(payload: PortalSettingPayload) {
  Object.assign(portalSetting, payload)
  MsgSuccess('已应用到当前页面')
  return Promise.resolve()
}

/* 编辑草稿预览与认证入口联动 */

const authSettingButtonRef = useTemplateRef<InstanceType<typeof ButtonPortalAuthSetting>>('authSettingButtonRef')
const previewName = computed(() => portalSetting.name)
const previewLogo = computed(() => portalSetting.logo)
</script>

<template>
  <MkViewLayout title="门户访问设置">
    <div class="flex min-w-215 flex-1 gap-4">
      <div class="w-95 shrink-0 space-y-4">
        <el-card shadow="never" body-class="flex-between gap-3">
          <div class="flex-align-center min-w-0 gap-2">
            <img v-if="previewLogo" :src="previewLogo" alt="门户 Logo" class="size-6 shrink-0 object-contain" />
            <LogoIcon v-else :height="24" class="shrink-0" />
            <h4 class="truncate" :title="previewName">{{ previewName }}</h4>
          </div>
          <!-- 编辑门户名称与 Logo -->
          <ButtonEditPortal v-if="perm.system.portal.edit()" ref="editPortalButtonRef" :setting="portalSetting" :saving="saving" :save="savePortalSetting" />
        </el-card>
        <el-card shadow="never">
          <div class="space-y-4">
            <h4>访问设置</h4>
            <!-- 门户公开访问链接 -->
            <div>
              <div class="flex-between mb-2 gap-2">
                <span>门户公开访问链接</span>
                <el-switch
                  :model-value="portalSetting.enable_public_access"
                  size="small"
                  @change="handleAccessChange('enable_public_access', $event)"
                />
              </div>
              <el-input :model-value="portalAccessUrl">
                <template #suffix>
                  <!-- 复制门户公开访问链接 -->
                  <el-button text @click="copyText(portalAccessUrl)" class="-mr-1">
                    <MkIcon name="icon_copy_outlined" class="text-N600" />
                  </el-button>
                </template>
              </el-input>
            </div>
            <!-- 智能体后端 API 访问 -->
            <div>
              <div class="flex-between mb-2 gap-2">
                <span>智能体后端 API 访问</span>
                <el-switch :model-value="portalSetting.enable_api" size="small" @change="handleAccessChange('enable_api', $event)" />
              </div>
              <el-input :model-value="portalApiUrl">
                <template #suffix>
                  <!-- 复制智能体后端 API 访问 -->
                  <el-button text @click="copyText(portalApiUrl)" class="-mr-1">
                    <MkIcon name="icon_copy_outlined" class="text-N600" />
                  </el-button>
                </template>
              </el-input>
            </div>
            <!-- 知识库后端 API 检索 -->
            <div>
              <div class="flex-between mb-2 gap-2">
                <span>知识库后端 API 检索</span>
                <el-switch
                  :model-value="portalSetting.enable_knowledge_base_api"
                  size="small"
                  @change="handleAccessChange('enable_knowledge_base_api', $event)"
                />
              </div>
              <el-input :model-value="portalApiUrl">
                <template #suffix>
                  <!-- 复制知识库后端 API 检索 -->
                  <el-button text @click="copyText(portalApiUrl)" class="-mr-1">
                    <MkIcon name="icon_copy_outlined" class="text-N600" />
                  </el-button>
                </template>
              </el-input>
            </div>
            <div class="flex-between gap-2">
              <span>身份认证</span>
              <div class="flex-align-center gap-2">
                <!-- 配置身份认证 -->
                <ButtonPortalAuthSetting ref="authSettingButtonRef" :setting="portalSetting" :saving="saving" :save="savePortalAuthSetting" />
                <el-switch :model-value="portalSetting.enable_auth" size="small" @change="handleAccessChange('enable_auth', $event)" />
              </div>
            </div>
            <div class="flex-between gap-2">
              <span>跨域设置</span>
              <div class="flex-align-center gap-2">
                <!-- 配置跨域地址 -->
                <ButtonPortalCorsSetting v-model="portalCorsOrigins" :disabled="saving" />
                <el-switch :model-value="portalSetting.enable_cors" size="small" @change="handleAccessChange('enable_cors', $event)" />
              </div>
            </div>
          </div>
        </el-card>
      </div>
      <PortalPreview :name="previewName" :logo="previewLogo" />
    </div>
  </MkViewLayout>
</template>
