template
<template>
  <el-drawer v-model="visible" size="60%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <h4>{{ currentPlatform.name + '设置' }}</h4>
      </div>
    </template>

    <el-form
      :model="currentPlatform.config"
      label-width="120px"
      label-position="top"
      require-asterisk-position="right"
      ref="formRef"
    >
      <el-form-item
        v-for="(value, key) in currentPlatform.config"
        :key="key"
        :label="formatFieldName(key)"
        :prop="key"
        :rules="getValidationRules(key)"
      >
        <el-input v-model="currentPlatform.config[key]" :default-value="''"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">取 消</el-button>
        <el-button @click="validateConnection">校 验</el-button>
        <el-button type="primary" @click="validateForm">保 存</el-button>
      </span>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElForm } from 'element-plus'
import platformApi from '@/api/platform-source'
import { MsgError, MsgSuccess } from '@/utils/message'

const visible = ref(false)
const loading = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

interface PlatformConfig {
  [key: string]: string
}

interface Platform {
  key: string
  logoSrc: string
  name: string
  isActive: boolean
  isValid: boolean
  config: PlatformConfig
}

const currentPlatform = reactive<Platform>({
  key: '',
  logoSrc: '',
  name: '',
  isActive: false,
  isValid: false,
  config: {}
})

const formatFieldName = (key?: string): string => {
  const fieldNames: { [key: string]: string } = {
    app_key: 'APP Key',
    app_secret: 'APP Secret',
    corp_id: 'Corp ID',
    agent_id: 'Agent ID',
    callback_url: '回调地址'
  }
  return (
    fieldNames[key as keyof typeof fieldNames] ||
    (key ? key.charAt(0).toUpperCase() + key.slice(1) : '')
  )
}

const getValidationRules = (key: string) => {
  switch (key) {
    case 'app_key':
      return [{ required: true, message: '请输入 APP Key', trigger: ['blur', 'change'] }]
    case 'app_secret':
      return [{ required: true, message: '请输入 APP Secret', trigger: ['blur', 'change'] }]
    case 'corp_id':
      return [{ required: true, message: '请输入 Corp ID', trigger: ['blur', 'change'] }]
    case 'agent_id':
      return [{ required: true, message: '请输入 Agent ID', trigger: ['blur', 'change'] }]
    case 'callback_url':
      return [
        { required: true, message: '请输入回调地址', trigger: ['blur', 'change'] },
        { pattern: /^https?:\/\/.+/, message: '请输入有效的 URL 地址', trigger: ['blur', 'change'] }
      ]
    default:
      return []
  }
}

const open = async (platform: Platform) => {
  visible.value = true
  loading.value = true
  Object.assign(currentPlatform, platform)

  // 设置默认的 callback_url
  let defaultCallbackUrl = window.location.origin

  // 根据平台设置特定的 callback_url
  switch (platform.key) {
    case 'wecom':
    case 'dingtalk':
      currentPlatform.config.callback_url = defaultCallbackUrl
      break
    case 'lark':
      currentPlatform.config.callback_url = `${defaultCallbackUrl}/api/feishu`
      break
    default:
      break
  }
}
defineExpose({ open })

const validateForm = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      saveConfig()
    } else {
      MsgError('请填写所有必填项并确保格式正确')
    }
  })
}

function validateConnection() {
  platformApi.validateConnection(currentPlatform, loading).then((res: any) => {
    if (res.data) {
      MsgSuccess('校验成功')
    } else {
      MsgError('校验失败')
    }
  })
}

function saveConfig() {
  platformApi.updateConfig(currentPlatform, loading).then((res: any) => {
    MsgSuccess('保存成功')

    visible.value = false
  })
}
</script>

<style lang="scss" scoped>
// 保持原有的样式
</style>
