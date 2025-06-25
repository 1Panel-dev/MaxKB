<template>
  <LayoutContainer class="knowledge-manage">
    <template #left>
      <h4 class="p-16 pb-0">{{ $t('views.knowledge.title') }}</h4>
      <folder-tree
        :source="FolderSource.KNOWLEDGE"
        :data="folderList"
        :currentNodeKey="currentFolder?.id"
        @handleNodeClick="folderClickHandel"
        class="p-8"
        :shareTitle="$t('views.shared.shared_knowledge')"
        :showShared="permissionPrecise['is_share']()"
        @refreshTree="refreshFolder"
      />
    </template>
    <KnowledgeListContainer>
      <template #header>
        <FolderBreadcrumb :folderList="folderList" @click="folderClickHandel" />
      </template>
    </KnowledgeListContainer>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, shallowRef, nextTick, computed } from 'vue'
import KnowledgeListContainer from '@/views/knowledge/component/KnowledgeListContainer.vue'
import { FolderSource } from '@/enums/common'
import permissionMap from '@/permission'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
const route = useRoute()
const { folder, knowledge } = useStore()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})
const loading = ref(false)

const folderList = ref<any[]>([])
const currentFolder = ref<any>({})

function getFolder(bool?: boolean) {
  const params = {}
  folder.asyncGetFolder(FolderSource.KNOWLEDGE, params, loading).then((res: any) => {
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
  knowledge.setKnowledgeList([])
}

function refreshFolder() {
  getFolder()
}

onMounted(() => {
  getFolder(true)
})
</script>

<style lang="scss" scoped></style>
