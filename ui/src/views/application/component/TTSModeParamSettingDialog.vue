<template>
  <el-dialog
    align-center
    :title="$t('common.paramSetting')"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <DynamicsForm
      v-model="form_data"
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      :render_data="model_form_field"
      ref="dynamicsFormRef"
    >
    </DynamicsForm>

    <template #footer>
      <div class="flex-between">
        <el-button @click="testPlay" :loading="playLoading">
          <AppIcon iconName="app-video-play" class="mr-4"></AppIcon>
          {{ $t('views.application.applicationForm.form.voicePlay.listeningTest') }}
        </el-button>

        <span class="dialog-footer">
          <el-button @click.prevent="dialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="submit" :loading="loading">
            {{ $t('common.confirm') }}
          </el-button>
        </span>
      </div>
    </template>
  </el-dialog>
  <!-- 先渲染，不然不能播放   -->
  <audio ref="audioPlayer" controls hidden="hidden"></audio>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import modelAPi from '@/api/model'
import applicationApi from '@/api/application'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { keys } from 'lodash'
import { app } from '@/main'
import { MsgError } from '@/utils/message'

const {
  params: { id }
} = app.config.globalProperties.$route as any

const tts_model_id = ref('')
const model_form_field = ref<Array<FormField>>([])
const emit = defineEmits(['refresh'])
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const form_data = ref<any>({})
const dialogVisible = ref(false)
const loading = ref(false)
const playLoading = ref(false)
const getApi = (model_id: string, application_id?: string) => {
  return application_id
    ? applicationApi.getModelParamsForm(application_id, model_id, loading)
    : modelAPi.getModelParamsForm(model_id, loading)
}
const open = (model_id: string, application_id?: string, model_setting_data?: any) => {
  form_data.value = {}
  tts_model_id.value = model_id
  const api = getApi(model_id, application_id)
  api.then((ok) => {
    model_form_field.value = ok.data
    const resp = ok.data
      .map((item: any) => ({
        [item.field]: item.show_default_value !== false ? item.default_value : undefined
      }))
      .reduce((x, y) => ({ ...x, ...y }), {})
    // 删除不存在的字段
    if (model_setting_data) {
      Object.keys(model_setting_data).forEach((key) => {
        if (!(key in resp)) {
          delete model_setting_data[key]
        }
      })
    }
    model_setting_data = { ...resp, ...model_setting_data }
    // 渲染动态表单
    dynamicsFormRef.value?.render(model_form_field.value, model_setting_data)
  })
  dialogVisible.value = true
}

const reset_default = (model_id: string, application_id?: string) => {
  const api = getApi(model_id, application_id)
  api.then((ok) => {
    model_form_field.value = ok.data
    const model_setting_data = ok.data
      .map((item) => ({
        [item.field]: item.show_default_value !== false ? item.default_value : undefined
      }))
      .reduce((x, y) => ({ ...x, ...y }), {})

    emit('refresh', model_setting_data)
  })
}

const submit = async () => {
  dynamicsFormRef.value?.validate().then(() => {
    emit('refresh', form_data.value)
    dialogVisible.value = false
  })
}

const audioPlayer = ref<HTMLAudioElement | null>(null)
const testPlay = () => {
  const data = {
    ...form_data.value,
    tts_model_id: tts_model_id.value
  }
  applicationApi
    .playDemoText(id as string, data, playLoading)
    .then(async (res: any) => {
      if (res.type === 'application/json') {
        const text = await res.text()
        MsgError(text)
        return
      }
      // 创建 Blob 对象
      const blob = new Blob([res], { type: 'audio/mp3' })

      // 创建对象 URL
      const url = URL.createObjectURL(blob)

      // 检查 audioPlayer 是否已经引用了 DOM 元素
      if (audioPlayer.value instanceof HTMLAudioElement) {
        audioPlayer.value.src = url
        audioPlayer.value.play() // 自动播放音频
      } else {
        console.error('audioPlayer.value is not an instance of HTMLAudioElement')
      }
    })
    .catch((err) => {
      console.log('err: ', err)
    })
}

defineExpose({ open, reset_default })
</script>

<style lang="scss" scoped></style>
