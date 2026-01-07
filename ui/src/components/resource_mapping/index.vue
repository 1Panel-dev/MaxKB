<template>
  <el-drawer
    v-model="visible"
    :title="$t('views.system.resourceMapping.title')"
    size="60%"
    :append-to-body="true"
  >
    <div class="lighter mb-12">
      {{ currentSourceName }}
    </div>
    <div class="flex align-center mb-16">
      <KnowledgeIcon
        v-if="currentSourceType === 'KNOWLEDGE'"
        class="mr-12"
        :size="24"
        :type="currentSource.type"
      />
      <el-avatar
        v-else-if="currentSourceType === 'TOOL' && isAppIcon(currentSource?.icon)"
        shape="square"
        :size="24"
        style="background: none"
        class="mr-12"
      >
        <img :src="resetUrl(currentSource?.icon, resetUrl('./favicon.ico'))" alt="" />
      </el-avatar>
      <ToolIcon
        v-else-if="currentSourceType === 'TOOL'"
        class="mr-12"
        :size="24"
        :type="currentSource.tool_type"
      />

      <span
        v-else-if="currentSourceType === 'MODEL'"
        style="height: 24px; width: 24px"
        :innerHTML="getProviderIcon(currentSource)"
        class="mr-12"
      ></span>
      {{ currentSource.name }}
    </div>
    <div class="lighter mb-12">
      {{ $t('views.system.resourceMapping.sub_title') }}
    </div>
    <div class="flex-between mb-16">
      <div class="flex-between complex-search">
        <el-select class="complex-search__left" v-model="searchType" style="width: 100px">
          <el-option :label="$t('common.name')" value="resource_name" />
          <el-option :label="$t('common.creator')" value="user_name" />
          <el-option :label="$t('common.type')" value="source_type" />
        </el-select>
        <el-input
          v-if="searchType === 'resource_name'"
          v-model="query.resource_name"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
          @keyup.enter="pageResourceMapping()"
        />
        <el-input
          v-if="searchType === 'user_name'"
          v-model="query.user_name"
          :placeholder="$t('common.search')"
          style="width: 220px"
          clearable
          @keyup.enter="pageResourceMapping()"
        />
        <el-select
          v-else-if="searchType === 'source_type'"
          v-model="query.source_type"
          @change="pageResourceMapping()"
          filterable
          clearable
          multiple
          :reserve-keyword="false"
          collapse-tags
          collapse-tags-tooltip
          style="width: 220px"
          :placeholder="$t('common.search')"
        >
          <el-option :label="$t('views.application.title')" value="APPLICATION" />
          <el-option :label="$t('views.knowledge.title')" value="KNOWLEDGE" />
        </el-select>
      </div>
    </div>

    <app-table
      ref="multipleTableRef"
      class="mt-16"
      :data="tableData"
      :pagination-config="paginationConfig"
      @sizeChange="handleSizeChange"
      @changePage="pageResourceMapping"
      :maxTableHeight="200"
      :row-key="(row: any) => row.id"
      v-loading="loading"
    >
      <el-table-column prop="name" :label="$t('common.name')" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <el-button link @click="toSetting(row)">
            <div class="flex align-center">
              <KnowledgeIcon
                v-if="row.source_type === 'KNOWLEDGE'"
                class="mr-8"
                :size="22"
                :type="row.icon"
              />
              <el-avatar
                v-else-if="row.source_type === 'APPLICATION' && isAppIcon(row?.icon)"
                shape="square"
                :size="22"
                style="background: none"
                class="mr-8"
              >
                <img :src="resetUrl(row?.icon, resetUrl('./favicon.ico'))" alt="" />
              </el-avatar>

              <span>{{ row.name }}</span>
            </div>
          </el-button>
        </template>
      </el-table-column>
      <el-table-column
        prop="desc"
        min-width="120"
        show-overflow-tooltip
        :label="$t('common.desc')"
      />
      <el-table-column
        prop="source_type"
        min-width="120"
        show-overflow-tooltip
        :label="$t('common.type')"
      >
        <template #default="{ row }">
          {{
            row.source_type === 'APPLICATION'
              ? $t('views.application.title')
              : $t('views.knowledge.title')
          }}
        </template>
      </el-table-column>
      <el-table-column
        prop="workspace_name"
        min-width="120"
        show-overflow-tooltip
        :label="$t('views.workspace.title')"
        v-if="showWorkspace"
      >
        <template #header>
          <div>
            <span>{{ $t('views.workspace.title') }}</span>
            <el-popover :width="200" trigger="click" :visible="workspaceVisible">
              <template #reference>
                <el-button
                  style="margin-top: -2px"
                  :type="workspaceArr && workspaceArr.length > 0 ? 'primary' : ''"
                  link
                  @click="workspaceVisible = !workspaceVisible"
                >
                  <el-icon>
                    <Filter />
                  </el-icon>
                </el-button>
              </template>
              <div class="filter">
                <div class="form-item mb-16 ml-4">
                  <div @click.stop>
                    <el-input
                      v-model="filterText"
                      :placeholder="$t('common.search')"
                      prefix-icon="Search"
                      clearable
                    />
                    <el-scrollbar height="300" v-if="filterData.length">
                      <el-checkbox-group
                        v-model="workspaceArr"
                        style="display: flex; flex-direction: column"
                      >
                        <el-checkbox
                          v-for="item in filterData"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                        />
                      </el-checkbox-group>
                    </el-scrollbar>
                    <el-empty v-else :description="$t('common.noData')" />
                  </div>
                </div>
              </div>
              <div class="text-right">
                <el-button size="small" @click="filterWorkspaceChange('clear')"
                  >{{ $t('common.clear') }}
                </el-button>
                <el-button type="primary" @click="filterWorkspaceChange" size="small"
                  >{{ $t('common.confirm') }}
                </el-button>
              </div>
            </el-popover>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="username"
        min-width="120"
        show-overflow-tooltip
        :label="$t('common.creator')"
      />
    </app-table>
  </el-drawer>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { isAppIcon, resetUrl } from '@/utils/common'
import useStore from '@/stores'
import { t } from '@/locales'
import type { Provider } from '@/api/type/model'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'
import permissionMap from '@/permission'
import { MsgError } from '@/utils/message'

const route = useRoute()
const router = useRouter()
const { model, user } = useStore()
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
  } else if (route.path.includes('shared')) {
    return 'systemShare'
  } else {
    return 'workspace'
  }
})

const showWorkspace = computed(() => (user.isPE() || user.isEE()) && route.path.includes('shared'))

const currentSourceName = computed(() => {
  if (currentSourceType.value === 'TOOL') {
    return t('views.tool.title')
  } else if (currentSourceType.value === 'MODEL') {
    return t('views.model.title')
  } else {
    return t('views.knowledge.title')
  }
})

const pageResourceMapping = () => {
  const workspaceId = user.getWorkspaceId() || 'default'
  const params: any = {}
  if (query.value[searchType.value]) {
    params[searchType.value] = query.value[searchType.value]
  }
  if (workspaceArr.value.length > 0) {
    params.workspace_ids = JSON.stringify(workspaceArr.value)
  }
  loadSharedApi({ type: 'resourceMapping', systemType: apiType.value })
    .getResourceMapping(
      workspaceId,
      currentSourceType.value,
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
  pageResourceMapping()
}

const currentSourceType = ref<string>()
const currentSourceId = ref<string>()
const currentSource = ref<any>()
const open = (source: string, data: any) => {
  visible.value = true
  currentSourceType.value = source
  currentSourceId.value = data.id
  currentSource.value = data
  pageResourceMapping()
  if (currentSourceType.value === 'MODEL') {
    getProvider()
  }
  getWorkspaceList()
}
const close = () => {
  visible.value = false
  paginationConfig.current_page = 1
}

const getProviderIcon = computed(() => {
  return (row: any) => {
    return provider_list.value.find((p) => p.provider === row.provider)?.icon
  }
})

const provider_list = ref<Array<Provider>>([])

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    provider_list.value = res?.data
  })
}

const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])

const filterText = ref('')
const filterData = ref<any[]>([])

function filterWorkspaceChange(val: string) {
  if (val === 'clear') {
    workspaceArr.value = []
  }
  filterText.value = ''
  pageResourceMapping()
  workspaceVisible.value = false
}

async function getWorkspaceList() {
  if (user.isEE() && showWorkspace.value) {
    const res = await loadPermissionApi('workspace').getSystemWorkspaceList(loading)
    workspaceOptions.value = res.data.map((item: any) => ({
      label: item.name,
      value: item.id,
    }))
  }
}

const hasResourceWorkspacePermission = (row: any) => {
  return permissionMap[row.source_type.toLowerCase() as 'application' | 'knowledge'][
    'workspace'
  ].jump_read(row.id)
}

const hasResourceSystemManagePermission = (row: any) => {
  return permissionMap[row.source_type.toLowerCase() as 'application' | 'knowledge'][
    'systemManage'
  ].jump_read()
}
const hasResourceSharedPermission = () => {
  return permissionMap['knowledge']['systemShare'].jump_read()
}

function hasJumpPermission(from: string, row: any) {
  if (row.source_type === 'KNOWLEDGE') {
    if (from === 'shared') {
      if (row.workspace_id === 'None') {
        return hasResourceSharedPermission()
      } else {
        return hasResourceSystemManagePermission(row)
      }
    } else if (from === 'resource-management') {
      return hasResourceSystemManagePermission(row)
    } else if (from === 'workspace') {
      return hasResourceWorkspacePermission(row)
    }
  }

  if (row.source_type === 'APPLICATION') {
    if (['shared', 'resource-management'].includes(from)) {
      return hasResourceSystemManagePermission(row)
    } else if (from === 'workspace') {
      return hasResourceWorkspacePermission(row)
    }
  }
  return false
}

function toSetting(row: any) {
  let from = ''
  if (route.path.includes('resource-management')) {
    from = 'resource-management'
  } else if (route.path.includes('shared')) {
    from = 'shared'
  } else {
    from = 'workspace'
  }
  if (row.source_type === 'KNOWLEDGE') {
    if (!hasJumpPermission(from, row)) {
      MsgError(t('common.noTargetPermission'))
      return
    }
    const newUrl = router.resolve({
      path: `/knowledge/${row.source_id}/${from === 'shared' ? (row.workspace_id === 'None' ? 'shared' : 'resource-management') : from}/${row.type}/document`,
    }).href
    window.open(newUrl)
  } else if (row.source_type === 'APPLICATION') {
    if (!hasJumpPermission(from, row)) {
      MsgError(t('common.noTargetPermission'))
      return
    }
    if (row.type === 'WORK_FLOW') {
      const newUrl = router.resolve({
        path: `/application/${from === 'shared' ? 'resource-management' : from}/${row.source_id}/workflow`,
      }).href
      window.open(newUrl)
    } else {
      const newUrl = router.resolve({
        path: `/application/${from === 'shared' ? 'resource-management' : from}/${row.source_id}/SIMPLE/setting`,
      }).href
      window.open(newUrl)
    }
  }
}

watch(
  [() => workspaceOptions.value, () => filterText.value],
  () => {
    if (!filterText.value.length) {
      filterData.value = workspaceOptions.value
    }
    filterData.value = workspaceOptions.value.filter((v: any) =>
      v.label.toLowerCase().includes(filterText.value.toLowerCase()),
    )
  },
  { immediate: true },
)

defineExpose({
  open,
  close,
})
</script>
<style lang="scss" scoped></style>
