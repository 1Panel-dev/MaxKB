<template>
  <card-box
    style="
      --app-card-box-description-height: 100%;
      --card-min-height: 153px;
      --card-min-width: 20px;
      width: 100%;
    "
    :title="model.name"
  >
    <template #icon>
      <AppAvatar
        class="mr-12"
        shape="square"
        style="--el-avatar-bg-color: rgba(255, 255, 255, 0)"
        :size="32"
      >
        <span style="height: 24px; width: 24px" :innerHTML="icon"></span
      ></AppAvatar>
    </template>
    <template #description>
      <el-descriptions :column="1" label-align="center">
        <el-descriptions-item label="模型类型" label-class-name="ellipsis-1">
          <span class="ellipsis-1"> {{ model.model_type }}</span></el-descriptions-item
        >
        <el-descriptions-item label="模型名称" label-class-name="ellipsis-1">
          <span class="ellipsis-1">{{ model.model_name }}</span></el-descriptions-item
        >
      </el-descriptions>
    </template>
    <template #mouseEnter>
      <el-tooltip effect="dark" content="修改" placement="top">
        <el-button text @click.stop="openEditModel" class="edit-button">
          <el-icon><Edit /></el-icon> </el-button
      ></el-tooltip>
      <el-tooltip effect="dark" content="删除" placement="top">
        <el-button text @click.stop="deleteModel" class="delete-button">
          <el-icon><Delete /></el-icon>
        </el-button>
      </el-tooltip>
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
:deep(.el-descriptions__cell) {
  display: flex;
  flex-wrap: nowrap;
}
.delete-button {
  position: absolute;
  right: 12px;
  top: 18px;
  height: auto;
}
.edit-button {
  position: absolute;
  right: 30px;
  top: 18px;
  height: auto;
}
</style>
