<template>
  <card-box :title="model.name" shadow="hover" class="model-card">
    <template #header>
      <div class="flex align-center">
        <span style="height: 32px; width: 32px" :innerHTML="icon" class="mr-12"></span>
        <auto-tooltip :content="model.name" style="max-width: 40%">
          {{ model.name }}
        </auto-tooltip>
        <div class="flex align-center" v-if="model.status === 'ERROR'">
          <el-tag type="danger" class="ml-8">失败</el-tag>
          <el-tooltip effect="dark" :content="model?.meta?.message" placement="top">
            <el-icon class="danger ml-4" size="20"><Warning /></el-icon>
          </el-tooltip>
        </div>
      </div>
    </template>

    <div class="border-t mt-16">
      <ul>
        <li class="flex mt-16">
          <el-text type="info">模型类型</el-text>
          <span class="ellipsis ml-16"> {{ model.model_type }}</span>
        </li>
        <li class="flex mt-12">
          <el-text type="info">基础模型</el-text>
          <span class="ellipsis ml-16"> {{ model.model_name }}</span>
        </li>
      </ul>
    </div>
    <!-- progress -->
    <div class="progress-mask" v-if="model.status === 'DOWNLOAD'">
      <!-- <el-progress type="circle" :percentage="progress" />
      <p>正在下载 <span class="dotting"></span></p> -->
      <el-progress type="dashboard" :percentage="progress" class="percentage">
        <template #default="{ percentage }">
          <span class="percentage-value">{{ percentage }}%</span>
          <span class="percentage-label">正在下载 <span class="dotting"></span></span>
        </template>
      </el-progress>
    </div>

    <template #mouseEnter>
      <div class="operation-button">
        <el-tooltip effect="dark" content="修改" placement="top">
          <el-button text @click.stop="openEditModel">
            <el-icon>
              <component :is="model.status === 'ERROR' ? 'RefreshRight' : 'EditPen'" />
            </el-icon>
          </el-button>
        </el-tooltip>

        <el-tooltip effect="dark" content="删除" placement="top">
          <el-button text @click.stop="deleteModel">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </template>
    <EditModel ref="eidtModelRef" @submit="emit('change')"></EditModel>
  </card-box>
</template>
<script setup lang="ts">
import type { Provider, Model } from '@/api/type/model'
import ModelApi from '@/api/model'
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import EditModel from '@/views/template/component/EditModel.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

const props = defineProps<{
  model: Model
  provider_list: Array<Provider>
}>()
const downModel = ref<Model>()

const progress = computed(() => {
  if (downModel.value) {
    const down_model_chunk = downModel.value.meta['down_model_chunk']
    if (down_model_chunk) {
      const maxObj = down_model_chunk.reduce((prev: any, current: any) => {
        return (prev.index || 0) > (current.index || 0) ? prev : current
      })
      return maxObj.progress?.toFixed(1)
    }
    return 0
  }
  return 0
})
const emit = defineEmits(['change'])
const eidtModelRef = ref<InstanceType<typeof EditModel>>()
let interval: any
const deleteModel = () => {
  MsgConfirm(`删除模型 `, `是否删除模型：${props.model.name} ?`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      ModelApi.deleteModel(props.model.id).then(() => {
        emit('change')
      })
    })
    .catch(() => {})
}
const openEditModel = () => {
  const provider = props.provider_list.find((p) => p.provider === props.model.provider)
  if (provider) {
    eidtModelRef.value?.open(provider, props.model)
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
    if (props.model.status === 'DOWNLOAD') {
      ModelApi.getModelMetaById(props.model.id).then((ok) => {
        downModel.value = ok.data
      })
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
  min-height: 153px;
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
    background-color: rgba(122, 122, 122, 0.8);
    width: 100%;
    height: 100%;
    z-index: 111;
    text-align: center;
    .percentage {
      top: 50%;
      transform: translateY(-50%);
      margin-top: 5px;
    }

    .percentage-value {
      display: block;
      margin-top: 10px;
      font-size: 28px;
      color: #ffffff;
    }
    .percentage-label {
      display: block;
      margin-top: 10px;
      font-size: 12px;
      color: #ffffff;
    }
  }
}
</style>
