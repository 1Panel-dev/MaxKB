<template>
  <LayoutContainer showCollapse resizable class="knowledge-manage">
    <template #left>
      <h4 class="p-12-16 pb-0 mt-12">{{ $t('views.knowledge.title') }}</h4>

      <folder-tree
        :source="SourceTypeEnum.KNOWLEDGE"
        :data="folderList"
        :currentNodeKey="folder.currentFolder?.id"
        @handleNodeClick="folderClickHandle"
        :shareTitle="$t('views.shared.shared_knowledge')"
        :showShared="permissionPrecise['is_share']()"
        @refreshTree="refreshFolder"
        :draggable="true"
      />
    </template>
    <KnowledgeListContainer @refreshFolder="refreshFolder">
      <template #header>
        <h2 v-if="folder.currentFolder?.id === 'share'">
          {{ $t('views.shared.shared_knowledge') }}
        </h2>
        <FolderBreadcrumb :folderList="folderList" @click="folderClickHandle" v-else />
      </template>
    </KnowledgeListContainer>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, shallowRef, nextTick, computed } from 'vue'
import KnowledgeListContainer from '@/views/knowledge/component/KnowledgeListContainer.vue'
import { SourceTypeEnum } from '@/enums/common'
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

function getFolder(bool?: boolean) {
  const params = {}
  folder.asyncGetFolder(SourceTypeEnum.KNOWLEDGE, params, loading).then((res: any) => {
    folderList.value = res.data
    if (bool) {
      // 初始化刷新
      folder.setCurrentFolder(res.data?.[0] || {})
    }
  })
}

function folderClickHandle(row: any) {
  if (row.id === folder.currentFolder?.id) {
    return
  }
  folder.setCurrentFolder(row)
  knowledge.setKnowledgeList([])
}

function refreshFolder() {
  getFolder()
}

onMounted(() => {
  getFolder(folder.currentFolder?.id ? false : true)
})
</script>

<style lang="scss" scoped></style>
