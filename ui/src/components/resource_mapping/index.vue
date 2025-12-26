<template>
  <el-drawer
    v-model="visible"
    :title="$t('views.system.resourceMapping.title', '关联资源')"
    size="60%"
    :append-to-body="true"
  >
    <div class="flex-between mb-16">
      <div class="flex-between complex-search">
        <el-select class="complex-search__left" v-model="searchType" style="width: 100px">
          <el-option
            :label="$t('views.userManage.userForm.resourceName.label', '名称')"
            value="resource_name"
          />
          <el-option
            :label="$t('views.userManage.userForm.user_name.label', '创建者')"
            value="user_name"
          />
          <el-option
            :label="$t('views.userManage.userForm.source_type.label', '资源类型')"
            value="source_type"
          />
        </el-select>
        <el-input
          v-if="searchType === 'resource_name'"
          v-model="query.resource_name"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
          @keyup.enter="pageResouceMapping()"
        />
        <el-input
          v-if="searchType === 'user_name'"
          v-model="query.user_name"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
          @keyup.enter="pageResouceMapping()"
        />
        <el-select
          v-else-if="searchType === 'source_type'"
          v-model="query.source_type"
          @change="pageResouceMapping()"
          filterable
          clearable
          multiple
          :reserve-keyword="false"
          collapse-tags
          collapse-tags-tooltip
          style="width: 220px"
        >
          <el-option label="应用" value="APPLICATION" />
          <el-option label="知识库" value="KNOWLEDGE" />
        </el-select>
      </div>
    </div>

    <app-table
      ref="multipleTableRef"
      class="mt-16"
      :data="tableData"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="pageResouceMapping"
      :maxTableHeight="200"
      :row-key="(row: any) => row.id"
      v-loading="loading"
    >
      <el-table-column prop="name" label="名称" min-width="120" show-overflow-tooltip />
      <el-table-column prop="desc" min-width="120" show-overflow-tooltip label="描述" />
      <el-table-column prop="source_type" min-width="120" show-overflow-tooltip label="资源类型" />
      <el-table-column prop="username" min-width="120" show-overflow-tooltip label="创建者" />
    </app-table>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import useStore from '@/stores'
const route = useRoute()
const { user } = useStore()
const searchType = ref<string>('resource_name')
const query = ref<any>({
  resource_name: '',
  user_name: '',
  source_type: '',
})
const loading = ref<boolean>(false)
const tableData = ref<Array<any>>()
const visible = ref<boolean>(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const pageResouceMapping = () => {
  const workspaceId = user.getWorkspaceId() || 'default'
  const params: any = {}
  if (query.value[searchType.value]) {
    params[searchType.value] = query.value[searchType.value]
  }
  loadSharedApi({ type: 'resourceMapping', systemType: apiType.value })
    .getResourceMapping(
      workspaceId,
      currentSource.value,
      currentSourceId.value,
      paginationConfig,
      params,
      loading,
    )
    .then((res: any) => {
      tableData.value = res.data.records || []
      paginationConfig.total = res.data.total || 0
    })
}
function handleSizeChange() {
  paginationConfig.current_page = 1
  pageResouceMapping()
}
const currentSource = ref<string>()
const currentSourceId = ref<string>()
const open = (source: string, sourceId: string) => {
  visible.value = true
  currentSource.value = source
  currentSourceId.value = sourceId
  pageResouceMapping()
}
const close = () => {
  visible.value = false
  paginationConfig.current_page = 1
}
defineExpose({
  open,
  close,
})
</script>
<style lang="scss" scoped></style>
