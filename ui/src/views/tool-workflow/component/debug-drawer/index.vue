<template>
  <el-drawer v-model="drawer" title="调试" direction="rtl" :before-close="close">
    <Parameters ref="paramtersRef" :workflow="toolDetail?.work_flow"></Parameters>
    <template #footer>
      <el-button>取消</el-button>
      <el-button type="primary" @click="run">运行</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import Parameters from '../debug/parameters/index.vue'
const router = useRouter()
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
}
const paramtersRef = ref<InstanceType<typeof Parameters>>()
const run = () => {
  paramtersRef.value?.validate()?.then(() => {
    console.log(paramtersRef.value?.getData())
  })
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
