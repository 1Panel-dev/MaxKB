<template>
  <LayoutContainer class="tool-manage">
    <template #left>
      <h4 class="p-16 pb-0">{{ $t('views.tool.title') }}</h4>
      <folder-tree
        :source="FolderSource.TOOL"
        :data="folderList"
        :currentNodeKey="currentFolder?.id"
        @handleNodeClick="folderClickHandel"
        @refreshTree="refreshFolder"
        :shareTitle="$t('views.system.shared.shared_tool')"
        :showShared="permissionPrecise['is_share']()"
        class="p-8"
      />
    </template>
    <ToolListContainer>
      <template #header>
        <FolderBreadcrumb :folderList="folderList" @click="folderClickHandel" />
      </template>
    </ToolListContainer>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import ToolListContainer from '@/views/tool/component/ToolListContainer.vue'
import { FolderSource } from '@/enums/common'
import permissionMap from '@/permission'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
const route = useRoute()
const { folder, tool } = useStore()

const type = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['tool'][type.value]
})

const loading = ref(false)

const folderList = ref<any[]>([])
const currentFolder = ref<any>({})

function getFolder(bool?: boolean) {
  const params = {}
  folder.asyncGetFolder(FolderSource.TOOL, params, loading).then((res: any) => {
    folderList.value = res.data
    if (bool) {
      // 初始化刷新
      currentFolder.value = res.data?.[0] || {}
      folder.setCurrentFolder(currentFolder.value)
    }
  })
}

function folderClickHandel(row: any) {
  currentFolder.value = row
  folder.setCurrentFolder(currentFolder.value)
  tool.setToolList([])
}

function refreshFolder() {
  getFolder()
}

onMounted(() => {
  getFolder(true)
})
</script>

<style lang="scss" scoped></style>
