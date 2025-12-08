<template>
  <LayoutContainer showCollapse resizable class="tool-manage">
    <template #left>
      <h4 class="p-12-16 pb-0 mt-12">{{ $t('views.tool.title') }}</h4>

      <folder-tree
        :source="SourceTypeEnum.TOOL"
        :data="folderList"
        :currentNodeKey="folder.currentFolder?.id"
        @handleNodeClick="folderClickHandle"
        @refreshTree="refreshFolder"
        :shareTitle="$t('views.shared.shared_tool')"
        :showShared="permissionPrecise['is_share']()"
        :draggable="true"
      />
    </template>
    <ToolListContainer @refreshFolder="refreshFolder">
      <template #header>
        <el-space wrap>
          <h2 v-if="folder.currentFolder?.id === 'share'">
            {{ $t('views.shared.shared_tool') }}
          </h2>
          <FolderBreadcrumb :folderList="folderList" @click="folderClickHandle" v-else />
          <el-divider direction="vertical" />
          <el-radio-group v-model="toolType" @change="radioChange" class="app-radio-button-group">
            <el-radio-button value="">{{ $t('views.tool.all') }}</el-radio-button>
            <el-radio-button value="CUSTOM">{{ $t('views.tool.title') }}</el-radio-button>
            <el-radio-button value="MCP">MCP</el-radio-button>
          </el-radio-group>
        </el-space>
      </template>
    </ToolListContainer>
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import ToolListContainer from '@/views/tool/component/ToolListContainer.vue'
import { SourceTypeEnum } from '@/enums/common'
import permissionMap from '@/permission'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import bus from '@/bus'
const route = useRoute()
const { folder, tool } = useStore()

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
  return permissionMap['tool'][apiType.value]
})

const loading = ref(false)
const toolType = ref('')

const folderList = ref<any[]>([])

function getFolder(bool?: boolean) {
  const params = {}
  folder.asyncGetFolder(SourceTypeEnum.TOOL, params, loading).then((res: any) => {
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
  tool.setToolList([])
}

function radioChange() {
  tool.setToolType(toolType.value)
}

function refreshFolder() {
  getFolder()
}

onMounted(() => {
  getFolder(folder.currentFolder?.id ? false : true)
})
</script>

<style lang="scss" scoped></style>
