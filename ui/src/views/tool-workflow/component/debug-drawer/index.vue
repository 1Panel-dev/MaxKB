<template>
  <el-drawer
    v-model="drawer"
    title="调试"
    direction="rtl"
    :before-close="close"
    :destroy-on-close="true"
  >
    <Parameters
      v-if="active == 'parameters'"
      ref="paramtersRef"
      :workflow="toolDetail?.work_flow"
    ></Parameters>
    <Result
      v-else
      ref="resultRef"
      :isShared="isShared"
      :apiType="apiType"
      :toolDetail="toolDetail"
    ></Result>
    <template #footer v-if="active == 'parameters'">
      <el-button @click="close">取消</el-button>
      <el-button type="primary" @click="run">运行</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import Parameters from '../debug/parameters/index.vue'
import Result from '../debug/result/index.vue'

const route = useRoute()
const {
  params: { folderId },
  /*
  folderId 可以区分 resource-management shared还是 workspace
  */
} = route as any
const isShared = computed(() => {
  return folderId === 'share'
})
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else if (route.path.includes('share/')) {
    return 'workspaceShare'
  } else {
    return 'workspace'
  }
})
const active = ref<string>('parameters')
const toolDetail = ref<any>()
function getDetail(toolId: string) {
  loadSharedApi({ type: 'tool', isShared: isShared.value, systemType: apiType.value })
    .getToolById(toolId)
    .then((res: any) => {
      toolDetail.value = res.data
    })
}
const drawer = ref<boolean>(false)
const open = (toolId: any) => {
  drawer.value = true
  getDetail(toolId)
}
const close = () => {
  drawer.value = false
  active.value = 'parameters'
}
const paramtersRef = ref<InstanceType<typeof Parameters>>()
const resultRef = ref<InstanceType<typeof Result>>()
const run = () => {
  paramtersRef.value?.validate()?.then(() => {
    const parameters = paramtersRef.value?.getData()
    active.value = 'result'
    nextTick(() => {
      resultRef.value?.execute(toolDetail.value.id, parameters)
    })
  })
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
