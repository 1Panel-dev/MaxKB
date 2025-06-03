<template>
  <el-drawer v-model="visible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <h4>{{ drawerTitle }}</h4>
      </div>
    </template>

    <el-form
      v-if="dataLoaded"
      ref="formRef"
      :model="form[configType]"
      label-width="120px"
      :rules="rules[configType]"
      label-position="top"
      require-asterisk-position="right"
    >
      <h4 class="title-decoration-1 mb-16">{{ infoTitle }}</h4>

      <template v-for="(item, key) in configFields[configType]" :key="key">
        <el-form-item :label="item.label" :prop="key">
          <el-input
            v-model="form[configType][key]"
            :type="isPasswordField(key) ? (passwordVisible[key] ? 'text' : 'password') : 'text'"
            :placeholder="item.placeholder"
            :show-password="isPasswordField(key)"
          >
          </el-input>
        </el-form-item>
      </template>
      <div v-if="configType === 'wechat'" class="flex align-center mb-16">
        <span class="lighter mr-8">{{
          $t('views.application.applicationAccess.wecomSetting.authenticationSuccessful')
        }}</span>
        <el-switch v-if="configType === 'wechat'" v-model="form[configType].is_certification" />
      </div>

      <h4 class="title-decoration-1 mb-16">
        {{ $t('views.application.applicationAccess.callback') }}
      </h4>
      <el-form-item label="URL" prop="callback_url">
        <el-input
          v-model="form[configType].callback_url"
          :placeholder="$t('views.application.applicationAccess.callbackTip')"
          readonly
        >
          <template #append>
            <el-button @click="copyClick(form[configType].callback_url)">
              <AppIcon iconName="app-copy"></AppIcon>
            </el-button>
          </template>
        </el-input>
        <el-text type="info" v-if="configType === 'wechat'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="primary"
            href="https://mp.weixin.qq.com/advanced/advanced?action=dev&t=advanced/dev"
            target="_blank"
            >{{ $t('views.application.applicationAccess.wechatPlatform') }}</a
          >{{ $t('views.application.applicationAccess.wechatSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'dingtalk'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="primary"
            href="https://open-dev.dingtalk.com/fe/app?hash=%23%2Fcorp%2Fapp#/corp/app"
            target="_blank"
            >{{ $t('views.application.applicationAccess.dingtalkPlatform') }}</a
          >{{ $t('views.application.applicationAccess.dingtalkSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'wecom'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a
            class="primary"
            href="https://work.weixin.qq.com/wework_admin/frame#apps"
            target="_blank"
            >{{ $t('views.application.applicationAccess.wecomPlatform') }}</a
          >{{ $t('views.application.applicationAccess.wecomSetting.urlInfo') }}
        </el-text>
        <el-text type="info" v-if="configType === 'feishu'">
          {{ $t('views.application.applicationAccess.copyUrl') }}
          <a class="primary" href="https://open.feishu.cn/app/" target="_blank">{{
            $t('views.application.applicationAccess.larkPlatform')
          }}</a
          >{{ $t('views.application.applicationAccess.larkSetting.urlInfo') }}
        </el-text>
      </el-form-item>
    </el-form>

    <template #footer>
      <div>
        <el-button @click="closeDrawer">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit" :disabled="loading">
          {{ $t('common.save') }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import applicationApi from '@/api/application'
import { useRoute } from 'vue-router'
import { MsgError, MsgSuccess } from '@/utils/message'
import { copyClick } from '@/utils/clipboard'
import { t } from '@/locales'

type PlatformType = 'wechat' | 'dingtalk' | 'wecom' | 'feishu' | 'slack'

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const dataLoaded = ref(false)
const configType = ref<PlatformType>('wechat')
const route = useRoute()
const emit = defineEmits(['refresh'])
const {
  params: { id }
} = route as any

const form = reactive<any>({
  wechat: {
    app_id: '',
    app_secret: '',
    token: '',
    encoding_aes_key: '',
    is_certification: false,
    callback_url: ''
  },
  dingtalk: { client_id: '', client_secret: '', callback_url: '' },
  wecom: {
    app_id: '',
    agent_id: '',
    secret: '',
    token: '',
    encoding_aes_key: '',
    callback_url: ''
  },
  feishu: { app_id: '', app_secret: '', verification_token: '', callback_url: '' },
  slack: { signing_secret: '', bot_user_token: '', callback_url: '' }
})

const rules = reactive<{ [propName: string]: any }>({
  wechat: {
    app_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.appIdPlaceholder'),
        trigger: 'blur'
      }
    ],
    app_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.appSecretPlaceholder'),
        trigger: 'blur'
      }
    ],
    token: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.tokenPlaceholder'),
        trigger: 'blur'
      }
    ],
    encoding_aes_key: [
      {
        required: true,
        message: t('views.application.applicationAccess.wechatSetting.aesKeyPlaceholder'),
        trigger: 'blur'
      }
    ]
  },
  dingtalk: {
    client_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.dingtalkSetting.clientIdPlaceholder'),
        trigger: 'blur'
      }
    ],
    client_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.dingtalkSetting.clientSecretPlaceholder'),
        trigger: 'blur'
      }
    ]
  },
  wecom: {
    app_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.cropIdPlaceholder'),
        trigger: 'blur'
      }
    ],
    agent_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.agentIdPlaceholder'),
        trigger: 'blur'
      }
    ],
    secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.secretPlaceholder'),
        trigger: 'blur'
      }
    ],
    token: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.tokenPlaceholder'),
        trigger: 'blur'
      }
    ],
    encoding_aes_key: [
      {
        required: true,
        message: t('views.application.applicationAccess.wecomSetting.encodingAesKeyPlaceholder'),
        trigger: 'blur'
      }
    ]
  },
  feishu: {
    app_id: [
      {
        required: true,
        message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
        trigger: 'blur'
      }
    ],
    app_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
        trigger: 'blur'
      }
    ],
    verification_token: [
      {
        required: false,
        message: t('views.application.applicationAccess.larkSetting.verificationTokenPlaceholder'),
        trigger: 'blur'
      }
    ]
  },
  slack: {
    signing_secret: [
      {
        required: true,
        message: t('views.application.applicationAccess.slackSetting.signingSecretPlaceholder'),
        trigger: 'blur'
      }
    ],
    bot_user_token: [
      {
        required: true,
        message: t('views.application.applicationAccess.slackSetting.botUserTokenPlaceholder'),
        trigger: 'blur'
      }
    ]
  }
})

const configFields: { [propName: string]: { [propName: string]: any } } = {
  wechat: {
    app_id: {
      label: t('views.application.applicationAccess.wechatSetting.appId'),
      placeholder: ''
    },
    app_secret: {
      label: t('views.application.applicationAccess.wechatSetting.appSecret'),
      placeholder: ''
    },
    token: { label: t('views.application.applicationAccess.wechatSetting.token'), placeholder: '' },
    encoding_aes_key: {
      label: t('views.application.applicationAccess.wechatSetting.aesKey'),
      placeholder: ''
    }
  },
  dingtalk: {
    client_id: { label: 'Client ID', placeholder: '' },
    client_secret: { label: 'Client Secret', placeholder: '' }
  },
  wecom: {
    app_id: {
      label: t('views.application.applicationAccess.wecomSetting.cropId'),
      placeholder: ''
    },
    agent_id: { label: 'Agent ID', placeholder: '' },
    secret: { label: 'Secret', placeholder: '' },
    token: { label: 'Token', placeholder: '' },
    encoding_aes_key: { label: 'EncodingAESKey', placeholder: '' }
  },
  feishu: {
    app_id: { label: 'App ID', placeholder: '' },
    app_secret: { label: 'App Secret', placeholder: '' },
    verification_token: { label: 'Verification Token', placeholder: '' }
  },
  slack: {
    signing_secret: { label: 'Signing Secret', placeholder: '' },
    bot_user_token: { label: 'Bot User Token', placeholder: '' }
  }
}

const passwordFields = new Set([
  'app_secret',
  'client_secret',
  'secret',
  'bot_user_token',
  'signing_secret'
])

const drawerTitle = computed(
  () =>
    ({
      wechat: t('views.application.applicationAccess.wechatSetting.title'),
      dingtalk: t('views.application.applicationAccess.dingtalkSetting.title'),
      wecom: t('views.application.applicationAccess.wecomSetting.title'),
      feishu: t('views.application.applicationAccess.larkSetting.title'),
      slack: t('views.application.applicationAccess.slackSetting.title')
    }[configType.value])
)

const infoTitle = computed(
  () =>
    ({
      wechat: t('views.applicationOverview.appInfo.header'),
      dingtalk: t('views.applicationOverview.appInfo.header'),
      wecom: t('views.applicationOverview.appInfo.header'),
      feishu: t('views.applicationOverview.appInfo.header'),
      slack: t('views.applicationOverview.appInfo.header')
    }[configType.value])
)

const passwordVisible = reactive<Record<string, boolean>>(
  Object.keys(configFields[configType.value]).reduce(
    (acc, key) => {
      if (passwordFields.has(key)) {
        acc[key] = false
      }
      return acc
    },
    {} as Record<string, boolean>
  )
)

const isPasswordField = (key: any) => passwordFields.has(key)

const closeDrawer = () => {
  visible.value = false
}

const submit = async () => {
  if (loading.value) return

  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        applicationApi
          .updatePlatformConfig(id, configType.value, form[configType.value], loading)
          .then(() => {
            MsgSuccess(t('common.saveSuccess'))
            closeDrawer()
            emit('refresh')
          })
      } catch {
        MsgError(t('views.application.tip.saveErrorMessage'))
      }
    }
  })
}

const open = async (id: string, type: PlatformType) => {
  visible.value = true
  configType.value = type
  loading.value = true
  dataLoaded.value = false
  formRef.value?.resetFields()
  try {
    const res = await applicationApi.getPlatformConfig(id, type)
    if (res.data) {
      form[configType.value] = res.data
    }
    dataLoaded.value = true
  } catch {
    MsgError(t('views.application.tip.loadingErrorMessage'))
  } finally {
    loading.value = false
    form[configType.value].callback_url = `${window.location.origin}/api/${type}/${id}`
  }
}

defineExpose({ open })
</script>
