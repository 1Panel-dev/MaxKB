<template>
  <card-box :title="model.name" shadow="hover" class="model-card">
    <template #header>
      <div class="flex">
        <span style="height: 32px; width: 32px" :innerHTML="icon" class="mr-12"></span>
        <div style="width: calc(100% - 32px - 4px - var(--app-base-px))">
          <div class="flex" style="height: 22px">
            <auto-tooltip :content="model.name" style="max-width: 40%">
              {{ model.name }}
            </auto-tooltip>
            <span v-if="currentModel.status === 'ERROR'">
              <el-tooltip effect="dark" :content="errMessage" placement="top">
                <el-icon class="danger ml-4" size="18"><Warning /></el-icon>
              </el-tooltip>
            </span>
            <span v-if="currentModel.status === 'PAUSE_DOWNLOAD'">
              <el-tooltip
                effect="dark"
                :content="`${$t('views.template.templateForm.form.base_model.label')}: ${props.model.model_name} ${$t('views.template.tip.downloadError')}`"
                placement="top"
              >
                <el-icon class="danger ml-4" size="18"><Warning /></el-icon>
              </el-tooltip>
            </span>
          </div>
          <div class="mt-4">
            <el-tag v-if="model.permission_type === 'PRIVATE'" type="danger" class="danger-tag">{{
              $t('common.private')
            }}</el-tag>
            <el-tag v-else type="info" class="info-tag"> {{ $t('common.public') }}</el-tag>
          </div>
        </div>
      </div>
    </template>

    <div class="mt-16">
      <ul>
        <li class="flex mt-16">
          <el-text type="info">{{
            $t('views.template.templateForm.form.model_type.label')
          }}</el-text>
          <span class="ellipsis ml-16">
            {{ $t(modelType[model.model_type as keyof typeof modelType]) }}</span
          >
        </li>
        <li class="flex mt-12">
          <el-text type="info">{{
            $t('views.template.templateForm.form.base_model.label')
          }}</el-text>
          <span class="ellipsis-1 ml-16" style="height: 20px; width: 70%">
            {{ model.model_name }}</span
          >
        </li>
        <li class="flex mt-12">
          <el-text type="info">{{ $t('common.creator') }}</el-text>
          <span class="ellipsis-1 ml-16" style="height: 20px; width: 70%">
            {{ model.username }}</span
          >
        </li>
      </ul>
    </div>
    <!-- progress -->
    <div class="progress-mask" v-if="currentModel.status === 'DOWNLOAD'">
      <DownloadLoading class="percentage" />

      <div class="percentage-label flex-center">
        {{ $t('views.template.download.downloading') }} <span class="dotting"></span>
        <el-button
          link
          type="primary"
          class="ml-16"
          :disabled="!is_permisstion"
          @click.stop="cancelDownload"
          >{{ $t('views.template.download.cancelDownload') }}</el-button
        >
      </div>
    </div>

    <template #mouseEnter>
      <div class="operation-button">
        <el-tooltip effect="dark" :content="$t('common.modify')" placement="top">
          <el-button text :disabled="!is_permisstion" @click.stop="openEditModel">
            <el-icon>
              <el-icon><EditPen /></el-icon>
            </el-icon>
          </el-button>
        </el-tooltip>
        <el-dropdown trigger="click">
          <el-button text @click.stop>
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-if="
                  currentModel.model_type === 'TTS' ||
                  currentModel.model_type === 'LLM' ||
                  currentModel.model_type === 'IMAGE' ||
                  currentModel.model_type === 'TTI'
                "
                :disabled="!is_permisstion"
                icon="Setting"
                @click.stop="openParamSetting"
              >
                {{ $t('views.template.templateForm.title.paramSetting') }}
              </el-dropdown-item>
              <el-dropdown-item
                icon="Delete"
                :disabled="!is_permisstion"
                text
                @click.stop="deleteModel"
              >
                {{ $t('common.delete') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </template>
    <EditModel ref="editModelRef" @submit="emit('change')"></EditModel>
    <ParamSettingDialog ref="paramSettingRef" :model="model" />
  </card-box>
</template>
<script setup lang="ts">
import type { Provider, Model } from '@/api/type/model'
import ModelApi from '@/api/model'
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import EditModel from '@/views/template/component/EditModel.vue'
import DownloadLoading from '@/components/loading/DownloadLoading.vue'
import { MsgConfirm } from '@/utils/message'
import { modelType } from '@/enums/model'
import useStore from '@/stores'
import ParamSettingDialog from './ParamSettingDialog.vue'
import { t } from '@/locales'
const props = defineProps<{
  model: Model
  provider_list: Array<Provider>
  updateModelById: (model_id: string, model: Model) => void
}>()

const { user } = useStore()
const downModel = ref<Model>()

const is_permisstion = computed(() => {
  return user.userInfo?.id == props.model.user_id
})
const currentModel = computed(() => {
  if (downModel.value) {
    return downModel.value
  } else {
    return props.model
  }
})

const errMessage = computed(() => {
  if (currentModel.value.meta && currentModel.value.meta.message) {
    if (currentModel.value.meta.message === 'pull model manifest: file does not exist') {
      return `${currentModel.value.model_name} ${t('views.template.tip.noModel')}`
    }
    return currentModel.value.meta.message
  }
  return ''
})
const emit = defineEmits(['change', 'update:model'])
const editModelRef = ref<InstanceType<typeof EditModel>>()
let interval: any
const deleteModel = () => {
  MsgConfirm(
    t('views.template.delete.confirmTitle'),
    `${t('views.template.delete.confirmMessage')}${props.model.name} ?`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      ModelApi.deleteModel(props.model.id).then(() => {
        emit('change')
      })
    })
    .catch(() => {})
}

const cancelDownload = () => {
  ModelApi.pauseDownload(props.model.id).then(() => {
    downModel.value = undefined
    emit('change')
  })
}
const openEditModel = () => {
  const provider = props.provider_list.find((p) => p.provider === props.model.provider)
  if (provider) {
    editModelRef.value?.open(provider, props.model)
  }
}
const icon = computed(() => {
  return props.provider_list.find((p) => p.provider === props.model.provider)?.icon
})

/**
 * 初始化轮询
 */
const initInterval = () => {
  interval = setInterval(() => {
    if (currentModel.value.status === 'DOWNLOAD') {
      ModelApi.getModelMetaById(props.model.id).then((ok) => {
        downModel.value = ok.data
      })
    } else {
      if (downModel.value) {
        props.updateModelById(props.model.id, downModel.value)
        downModel.value = undefined
      }
    }
  }, 6000)
}

/**
 * 关闭轮询
 */
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
  }
}

const paramSettingRef = ref<InstanceType<typeof ParamSettingDialog>>()
const openParamSetting = () => {
  paramSettingRef.value?.open()
}

onMounted(() => {
  initInterval()
})
onBeforeUnmount(() => {
  // 清除定时任务
  closeInterval()
})
</script>
<style lang="scss" scoped>
.model-card {
  min-height: 135px;
  min-width: auto;
  .operation-button {
    position: absolute;
    right: 12px;
    top: 18px;
    height: auto;
    .el-button + .el-button {
      margin-left: 4px;
    }
  }
  .progress-mask {
    position: absolute;
    top: 0;
    left: 0;
    background-color: rgba(255, 255, 255, 0.9);
    width: 100%;
    height: 100%;
    z-index: 99;
    text-align: center;
    .percentage {
      margin-top: 55px;
      margin-bottom: 16px;
    }

    // .percentage-value {
    //   display: flex;
    //   font-size: 13px;
    //   align-items: center;
    //   color: var(--app-text-color-secondary);
    // }
    .percentage-label {
      margin-top: 50px;
      margin-left: 10px;
      font-size: 13px;
      color: var(--app-text-color-secondary);
    }
  }
}
</style>
