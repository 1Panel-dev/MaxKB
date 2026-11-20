<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PortalSetting, PortalSettingPayload } from '@/api/types'
import PortalApi from '@/api/admin/system/chat-management/portal-setting.ts'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import ButtonEditPortal from './components/ButtonEditPortal.vue'
import ButtonPortalAuthSetting from './components/ButtonPortalAuthSetting.vue'
import ButtonPortalCorsSetting from './components/ButtonPortalCorsSetting.vue'
import PortalPreview from './components/PortalPreview.vue'
import { useStore } from '@/stores'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import { perm } from '@/permission'

type AccessField = 'enable_public_access' | 'enable_api' | 'enable_agent_mcp_service' | 'enable_knowledge_base_api' | 'enable_auth' | 'enable_cors'

const { t } = useI18n({ useScope: 'global' })
const portalSetting = reactive<PortalSetting>({
  id: '',
  name: t('portal.name.default'),
  description: '',
  logo: '',
  enable_public_access: true,
  enable_api: true,
  enable_agent_mcp_service: true,
  enable_knowledge_base_api: true,
  enable_auth: false,
  auth_config: {
    login_value: ['LOCAL'],
    max_attempts: 1,
    failed_attempts: 5,
    lock_time: 10,
  },
  enable_cors: false,
  cross_domain_list: [],
})
const loading = ref(false)
const saving = ref(false)
const { auth } = useStore()
const portalAccessUrl = new URL(`${CHAT_API_BASE_PATH.replace(/\/api$/, '')}/portal`, window.location.origin).href

/* 进入页面加载门户配置，失败时保留默认配置 */
function loadPortalSetting() {
  loading.value = true
  return PortalApi.getPortalSetting()
    .then((setting) => Object.assign(portalSetting, setting))
    .finally(() => {
      loading.value = false
    })
}

/* 保存门户配置：接口返回完整配置，成功后整体回填作为页面唯一数据来源 */
function savePortalSetting(payload: PortalSettingPayload | FormData): Promise<void> {
  if (!canEditPortal.value || saving.value) return Promise.resolve()

  saving.value = true
  return PortalApi.putPortalSetting(payload)
    .then((setting) => {
      Object.assign(portalSetting, setting)
      MsgSuccess(t('common.messages.saveSuccess'))
    })
    .finally(() => {
      saving.value = false
    })
}

function handleAccessChange(field: AccessField, value: string | number | boolean) {
  if (!canEditPortal.value || saving.value) return
  if (field === 'enable_auth' && value && !portalSetting.auth_config.login_value?.length) {
    handleOpenAuthSetting(true)
    return
  }
  // 使用服务端确定的值渲染开关，失败时保留原配置。
  return savePortalSetting({ [field]: Boolean(value) })
}

/* 认证配置保存 */
function savePortalAuthSetting(payload: PortalSettingPayload) {
  return savePortalSetting(payload)
}

/* 跨域地址保存 */
function savePortalCorsSetting(origins: string[]) {
  return savePortalSetting({ cross_domain_list: origins })
}

function handleOpenAuthSetting(enableAfterSave = false) {
  if (!canEditPortal.value || saving.value) return

  authSettingButtonRef.value?.open(enableAfterSave)
}

/* 编辑草稿预览与认证入口联动 */

const authSettingButtonRef = useTemplateRef<InstanceType<typeof ButtonPortalAuthSetting>>('authSettingButtonRef')
const portalCorsOrigins = computed({
  get: () => portalSetting.cross_domain_list ?? [],
  set: (origins: string[]) => {
    portalSetting.cross_domain_list = origins
  },
})
const previewName = computed(() => portalSetting.name)

onMounted(() => loadPortalSetting())

// 权限 控制
const canEditPortal = computed(() => perm.system.portal.edit())
// Logo 为授权功能，授权无效（含社区版）时仅可查看，禁止上传或更换 Logo
const canEditLogo = computed(() => perm.system.portal.edit() && (auth.isPE || auth.isEE))
</script>

<template>
  <MkViewLayout :title="t('portal.title')" :loading="loading">
    <div class="flex min-w-215 flex-1 gap-4">
      <div class="w-95 shrink-0 space-y-4">
        <el-card shadow="never">
          <div class="flex-between gap-3">
            <div class="flex-align-center min-w-0 gap-2">
              <PortalIcon :icon="portalSetting.logo ?? undefined" />
              <h4 class="truncate" :title="previewName">{{ previewName }}</h4>
            </div>
            <!-- 编辑门户名称与 Logo -->
            <ButtonEditPortal
              :setting="portalSetting"
              :saving="saving"
              :disabled="!canEditPortal"
              :logo-disabled="!canEditLogo"
              :save="savePortalSetting"
            />
          </div>
        </el-card>
        <el-card shadow="never">
          <div class="space-y-4">
            <h4>{{ t('portal.access.title') }}</h4>
            <!-- 门户公开访问链接 -->
            <div>
              <div class="flex-between mb-2 gap-2">
                <MkTooltip placement="right" :content="t('portal.access.web.description')">
                  <span>{{ t('portal.access.web.label') }}</span>
                </MkTooltip>
                <el-switch
                  :disabled="!canEditPortal || saving"
                  :model-value="portalSetting.enable_public_access"
                  size="small"
                  @change="handleAccessChange('enable_public_access', $event)"
                />
              </div>
              <el-input :model-value="portalAccessUrl" readonly>
                <template #suffix>
                  <!-- 复制门户公开访问链接 -->
                  <el-button text :disabled="!canEditPortal" @click="copyText(portalAccessUrl)" class="-mr-1">
                    <MkIcon name="icon_copy_outlined" />
                  </el-button>
                </template>
              </el-input>
            </div>
            <!-- 智能体后端 API 访问 -->

            <div class="flex-between gap-2">
              <span class="flex-align-center gap-1">
                {{ t('portal.access.agentApi.label') }}
                <MkTooltip placement="right" :content="t('portal.access.agentApi.description')">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
              <el-switch
                :disabled="!canEditPortal || saving"
                :model-value="portalSetting.enable_api"
                size="small"
                @change="handleAccessChange('enable_api', $event)"
              />
            </div>

            <!-- 智能体 MCP 服务 -->

            <div class="flex-between gap-2">
              <span class="flex-align-center gap-1">
                {{ t('portal.access.agentMcp.label') }}
                <MkTooltip placement="right" :content="t('portal.access.agentMcp.description')">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
              <el-switch
                :disabled="!canEditPortal || saving"
                :model-value="portalSetting.enable_agent_mcp_service"
                size="small"
                @change="handleAccessChange('enable_agent_mcp_service', $event)"
              />
            </div>

            <!-- 知识库 MCP 服务 -->

            <div class="flex-between gap-2">
              <span class="flex-align-center gap-1">
                {{ t('portal.access.knowledgeMcp.label') }}
                <MkTooltip placement="right" :content="t('portal.access.knowledgeMcp.description')">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
              <el-switch
                :disabled="!canEditPortal || saving"
                :model-value="portalSetting.enable_knowledge_base_api"
                size="small"
                @change="handleAccessChange('enable_knowledge_base_api', $event)"
              />
            </div>

            <div class="flex-between gap-2" v-if="auth.isPE || auth.isEE">
              <span>{{ t('auth.loginSettings.title') }}</span>
              <div class="flex-align-center gap-2">
                <!-- 配置登录设置 -->
                <ButtonPortalAuthSetting
                  ref="authSettingButtonRef"
                  :setting="portalSetting"
                  :saving="saving"
                  :disabled="!canEditPortal"
                  :save="savePortalAuthSetting"
                />
              </div>
            </div>
            <div class="flex-between gap-2">
              <span>{{ t('portal.cors.title') }}</span>
              <div class="flex-align-center gap-2">
                <!-- 配置跨域地址 -->
                <ButtonPortalCorsSetting v-model="portalCorsOrigins" :saving="saving" :disabled="!canEditPortal" :save="savePortalCorsSetting" />
                <el-switch
                  :disabled="!canEditPortal || saving"
                  :model-value="portalSetting.enable_cors"
                  size="small"
                  @change="handleAccessChange('enable_cors', $event)"
                />
              </div>
            </div>
          </div>
        </el-card>
      </div>
      <PortalPreview :name="previewName" :logo="portalSetting.logo" />
    </div>
  </MkViewLayout>
</template>
