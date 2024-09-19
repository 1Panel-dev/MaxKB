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
      <div v-if="configType === 'wechat'" class="flex align-center" style="margin-bottom: 8px">
        <span class="el-form-item__label">认证通过</span>
        <el-switch v-if="configType === 'wechat'" v-model="form[configType].is_certification" />
      </div>

      <h4 class="title-decoration-1 mb-16">回调地址</h4>
      <el-form-item label="URL" prop="callback_url">
        <el-input v-model="form[configType].callback_url" placeholder="请输入回调地址" readonly>
          <template #append>
            <el-button @click="copyClick(form[configType].callback_url)">
              <AppIcon iconName="app-copy"></AppIcon>
            </el-button>
          </template>
        </el-input>
        <el-text type="info" v-if="configType === 'wechat'">
          复制链接填入到
          <a
            class="primary"
            href="https://mp.weixin.qq.com/advanced/advanced?action=dev&t=advanced/dev"
            target="_blank"
            >微信公众平台</a
          >-设置与开发-基本配置-服务器配置的 "服务器地址URL" 中
        </el-text>
        <el-text type="info" v-if="configType === 'dingtalk'">
          复制链接填入到
          <a
            class="primary"
            href="https://open-dev.dingtalk.com/fe/app?hash=%23%2Fcorp%2Fapp#/corp/app"
            target="_blank"
            >钉钉开放平台</a
          >-机器人页面，设置 "消息接收模式" 为 HTTP模式 ，并把下面URL填写到"消息接收地址"中
        </el-text>
        <el-text type="info" v-if="configType === 'wecom'">
          复制链接填入到
          <a
            class="primary"
            href="https://work.weixin.qq.com/wework_admin/frame#apps"
            target="_blank"
            >企业微信后台</a
          >-应用管理-自建-创建的应用-接受消息-设置 API 接收的 "URL" 中
        </el-text>
        <el-text type="info" v-if="configType === 'feishu'">
          复制链接填入到
          <a class="primary" href="https://open.feishu.cn/app/" target="_blank">飞书开放平台</a
          >-事件与回调-事件配置-配置订阅方式的 "请求地址" 中
        </el-text>
      </el-form-item>
    </el-form>

    <template #footer>
      <div>
        <el-button @click="closeDrawer">取消</el-button>
        <el-button type="primary" @click="submit" :disabled="loading">保存</el-button>
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

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const dataLoaded = ref(false)
const configType = ref<'wechat' | 'dingtalk' | 'wecom' | 'feishu'>('wechat')
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
  feishu: { app_id: '', app_secret: '', verification_token: '', callback_url: '' }
})

const rules = reactive<{ [propName: string]: any }>({
  wechat: {
    app_id: [{ required: true, message: '请输入开发者ID', trigger: 'blur' }],
    app_secret: [{ required: true, message: '请输入开发者密码', trigger: 'blur' }],
    token: [{ required: true, message: '请输入令牌', trigger: 'blur' }],
    encoding_aes_key: [{ required: true, message: '请输入消息加解密密钥', trigger: 'blur' }]
  },
  dingtalk: {
    client_id: [{ required: true, message: '请输入Client ID', trigger: 'blur' }],
    client_secret: [{ required: true, message: '请输入Client Secret', trigger: 'blur' }]
  },
  wecom: {
    app_id: [{ required: true, message: '请输入企业ID', trigger: 'blur' }],
    agent_id: [{ required: true, message: '请输入Agent ID', trigger: 'blur' }],
    secret: [{ required: true, message: '请输入Secret', trigger: 'blur' }],
    token: [{ required: true, message: '请输入Token', trigger: 'blur' }],
    encoding_aes_key: [{ required: true, message: '请输入EncodingAESKey', trigger: 'blur' }]
  },
  feishu: {
    app_id: [{ required: true, message: '请输入App ID', trigger: 'blur' }],
    app_secret: [{ required: true, message: '请输入App Secret', trigger: 'blur' }],
    verification_token: [{ required: false, message: '请输入Verification Token', trigger: 'blur' }]
  }
})

const configFields: { [propName: string]: { [propName: string]: any } } = {
  wechat: {
    app_id: { label: '开发者ID (APP ID)', placeholder: '请输入开发者ID' },
    app_secret: { label: '开发者密码 (APP Secret)', placeholder: '请输入开发者密码' },
    token: { label: '令牌 (Token)', placeholder: '请输入令牌' },
    encoding_aes_key: { label: '消息加解密密钥', placeholder: '请输入消息加解密密钥' }
  },
  dingtalk: {
    client_id: { label: 'Client ID', placeholder: '' },
    client_secret: { label: 'Client Secret', placeholder: '' }
  },
  wecom: {
    app_id: { label: '企业ID', placeholder: '' },
    agent_id: { label: 'Agent ID', placeholder: '' },
    secret: { label: 'Secret', placeholder: '' },
    token: { label: 'Token', placeholder: '' },
    encoding_aes_key: { label: 'EncodingAESKey', placeholder: '' }
  },
  feishu: {
    app_id: { label: 'App ID', placeholder: '' },
    app_secret: { label: 'App Secret', placeholder: '' },
    verification_token: { label: 'Verification Token', placeholder: '' }
  }
}

const passwordFields = new Set(['app_secret', 'client_secret', 'secret'])

const drawerTitle = computed(
  () =>
    ({
      wechat: '公众号配置',
      dingtalk: '钉钉应用配置',
      wecom: '企业微信应用配置',
      feishu: '飞书应用配置'
    })[configType.value]
)

const infoTitle = computed(
  () =>
    ({
      wechat: '应用信息',
      dingtalk: '应用信息',
      wecom: '应用信息',
      feishu: '应用信息'
    })[configType.value]
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
        await applicationApi.updatePlatformConfig(id, configType.value, form[configType.value])
        MsgSuccess('配置保存成功')
        closeDrawer()
        emit('refresh')
      } catch {
        MsgError('保存失败，请检查输入或稍后再试')
      }
    }
  })
}

const open = async (id: string, type: 'wechat' | 'dingtalk' | 'wecom' | 'feishu') => {
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
    MsgError('加载配置失败，请检查输入或稍后再试')
  } finally {
    loading.value = false
    form[configType.value].callback_url = `${window.location.origin}/api/${type}/${id}`
  }
}

defineExpose({ open })
</script>

<style lang="scss"></style>
