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
      <template v-for="(item, key) in configFields[configType]" :key="key">
        <el-form-item :label="item.label" :prop="key">
          <el-input v-model="form[configType][key]" :placeholder="item.placeholder" />
        </el-form-item>
      </template>
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

const form = reactive({
  wechat: { app_id: '', app_secret: '', token: '', encoding_aes_key: '', callback_url: '' },
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

const rules = reactive({
  wechat: {
    app_id: [{ required: true, message: '请输入开发者ID', trigger: 'blur' }],
    app_secret: [{ required: true, message: '请输入开发者密码', trigger: 'blur' }],
    token: [{ required: true, message: '请输入令牌', trigger: 'blur' }],
    encoding_aes_key: [{ required: true, message: '请输入消息加解密密钥', trigger: 'blur' }],
    callback_url: [{ required: true, message: '请输入回调地址', trigger: 'blur' }]
  },
  dingtalk: {
    client_id: [{ required: true, message: '请输入Client ID', trigger: 'blur' }],
    client_secret: [{ required: true, message: '请输入Client Secret', trigger: 'blur' }],
    callback_url: [{ required: true, message: '请输入回调地址', trigger: 'blur' }]
  },
  wecom: {
    app_id: [{ required: true, message: '请输入企业ID', trigger: 'blur' }],
    agent_id: [{ required: true, message: '请输入Agent ID', trigger: 'blur' }],
    secret: [{ required: true, message: '请输入Secret', trigger: 'blur' }],
    token: [{ required: true, message: '请输入Token', trigger: 'blur' }],
    encoding_aes_key: [{ required: true, message: '请输入EncodingAESKey', trigger: 'blur' }],
    callback_url: [{ required: true, message: '请输入回调地址', trigger: 'blur' }]
  },
  feishu: {
    app_id: [{ required: true, message: '请输入App ID', trigger: 'blur' }],
    app_secret: [{ required: true, message: '请输入App Secret', trigger: 'blur' }],
    verification_token: [{ required: false, message: '请输入Verification Token', trigger: 'blur' }],
    callback_url: [{ required: true, message: '请输入回调地址', trigger: 'blur' }]
  }
})

const configFields = {
  wechat: {
    app_id: { label: '开发者ID (APP ID)', placeholder: '请输入开发者ID' },
    app_secret: { label: '开发者密码 (APP Secret)', placeholder: '请输入开发者密码' },
    token: { label: '令牌 (Token)', placeholder: '请输入令牌' },
    encoding_aes_key: { label: '消息加解密密钥', placeholder: '请输入消息加解密密钥' },
    callback_url: { label: '回调地址', placeholder: '请输入回调地址' }
  },
  dingtalk: {
    client_id: { label: 'Client ID', placeholder: '' },
    client_secret: { label: 'Client Secret', placeholder: '' },
    callback_url: { label: '回调地址', placeholder: '' }
  },
  wecom: {
    app_id: { label: '企业ID', placeholder: '' },
    agent_id: { label: 'Agent ID', placeholder: '' },
    secret: { label: 'Secret', placeholder: '' },
    token: { label: 'Token', placeholder: '' },
    encoding_aes_key: { label: 'EncodingAESKey', placeholder: '' },
    callback_url: { label: '回调地址', placeholder: '' }
  },
  feishu: {
    app_id: { label: 'App ID', placeholder: '' },
    app_secret: { label: 'App Secret', placeholder: '' },
    verification_token: { label: 'Verification Token', placeholder: '' },
    callback_url: { label: '回调地址', placeholder: '' }
  }
}

const drawerTitle = computed(() => {
  const titles = {
    wechat: '公众号配置',
    dingtalk: '钉钉应用配置',
    wecom: '企业微信应用配置',
    feishu: '飞书配置'
  }
  return titles[configType.value] || ''
})

const closeDrawer = () => {
  visible.value = false
}

const submit = () => {
  if (loading.value) return

  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        await applicationApi.updatePlatformConfig(id, configType.value, form[configType.value])
        MsgSuccess('配置保存成功')
        closeDrawer()
        emit('refresh')
      } catch (error) {
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
      dataLoaded.value = true
    }
  } catch (error) {
    MsgError('加载配置失败，请检查输入或稍后再试')
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>

<style lang="scss">
/* 可以在这里添加自定义样式 */
</style>
