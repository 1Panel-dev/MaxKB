<template>
  <card-box :title="model.name" shadow="hover" class="model-card">
    <template #icon>
      <span style="height: 32px; width: 32px" :innerHTML="icon" class="mr-12"></span>
    </template>
    <div class="border-t mt-16">
      <ul>
        <li class="flex mt-16">
          <el-text type="info">模型类型</el-text>
          <span class="ellipsis ml-16"> {{ model.model_type }}</span>
        </li>
        <li class="flex mt-12">
          <el-text type="info">模型名称</el-text>
          <span class="ellipsis ml-16"> {{ model.model_name }}</span>
        </li>
      </ul>
    </div>

    <template #mouseEnter>
      <div class="operation-button">
        <el-tooltip effect="dark" content="修改" placement="top">
          <el-button text @click.stop="openEditModel">
            <el-icon><EditPen /></el-icon>
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
import { computed, ref } from 'vue'
import EditModel from '@/views/template/component/EditModel.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
const props = defineProps<{
  model: Model
  provider_list: Array<Provider>
}>()
const emit = defineEmits(['change'])
const eidtModelRef = ref<InstanceType<typeof EditModel>>()
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
}
</style>
