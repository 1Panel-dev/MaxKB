<template>
  <div class="p-16-24">
    <el-breadcrumb separator-icon="ArrowRight">
      <el-breadcrumb-item>{{ t('views.system.resource_management.label') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.application.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card class="mt-16" style="height: calc(var(--app-main-height) + 20px)">
      <div class="flex-between mb-16">
        <div class="complex-search">
          <el-select
            class="complex-search__left"
            v-model="search_type"
            style="width: 120px"
            @change="search_type_change"
          >
            <el-option :label="$t('common.creator')" value="create_user"/>

            <el-option :label="$t('common.name')" value="name"/>
            <el-option :label="$t('common.type')" value="type"/>
          </el-select>
          <el-input
            v-if="search_type === 'name'"
            v-model="search_form.name"
            @change="getList"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
          <el-select
            v-else-if="search_type === 'create_user'"
            v-model="search_form.create_user"
            @change="getList"
            clearable
            filterable
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name"/>
          </el-select>
          <el-select
            v-else-if="search_type === 'type'"
            v-model="search_form.type"
            @change="getList"
            clearable
            filterable
            style="width: 220px"
          >
            <el-option v-for="u in type_options" :key="u.id" :value="u.value" :label="u.label"/>
          </el-select>
        </div>
      </div>

      <app-table
        :data="applicationList"
        :pagination-config="paginationConfig"
        @sizeChange="getList"
        @changePage="getList"
        :maxTableHeight="260"
      >
        <!-- <el-table-column type="selection" width="55" /> -->
        <el-table-column width="220" :label="$t('common.name')" show-overflow-tooltip>
          <template #default="scope">
            <div class="table-name flex align-center">
              <el-icon size="24" class="mr-8">
                <el-avatar shape="square" :size="24" style="background: none" class="mr-8">
                  <img :src="resetUrl(scope.row?.icon)" alt=""/>
                </el-avatar>
              </el-icon>
              {{ scope.row.name }}
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="tool_type"
          :label="$t('common.type')"
          width="160"
        >
          <template #default="scope">
            <el-tag class="warning-tag" v-if="isWorkFlow(scope.row.type)">
              {{ $t('views.application.senior') }}
            </el-tag>
            <el-tag class="blue-tag" v-else>
              {{ $t('views.application.simple') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          width="150"
          prop="is_publish"
          :label="$t('common.status.label')"
          show-overflow-tooltip
        >
          <template #header>
            <div>
              <span>{{ $t('common.status.label') }}</span>
              <el-popover :width="100" trigger="click" :visible="statusVisible">
                <template #reference>
                  <el-button
                    style="margin-top: -2px"
                    :type="statusArr && statusArr.length > 0 ? 'primary' : ''"
                    link
                    @click="statusVisible = !statusVisible"
                  >
                    <el-icon>
                      <Filter/>
                    </el-icon>
                  </el-button>
                </template>
                <div class="filter">
                  <div class="form-item mb-16">
                    <div @click.stop>
                      <el-checkbox-group
                        v-model="statusArr"
                        style="display: flex; flex-direction: column"
                      >
                        <el-checkbox
                          v-for="item in statusOptions"
                          :key="item.value"
                          :label="item.label"
                          :value="item.value"
                        />
                      </el-checkbox-group>
                    </div>
                  </div>
                </div>
                <div class="text-right">
                  <el-button size="small" @click="filterStatusChange('clear')"
                  >{{ $t('common.clear') }}
                  </el-button>
                  <el-button type="primary" @click="filterStatusChange" size="small"
                  >{{ $t('common.confirm') }}
                  </el-button>
                </div>
              </el-popover>
            </div>
          </template>
          <template #default="scope">
            <div v-if="scope.row.is_publish" class="flex align-center">
              <el-icon class="color-success mr-8" style="font-size: 16px">
                <SuccessFilled/>
              </el-icon>
              <span class="color-text-primary">
                {{ $t('common.status.published') }}
              </span>
            </div>
            <div v-else class="flex align-center">
              <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
              <span class="color-text-primary">
                {{ $t('common.status.unpublished') }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          v-if="user.isEE()"
          width="150"
          prop="workspace_name"
          :label="$t('views.workspace.title')"
          show-overflow-tooltip
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
                      <Filter/>
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
                      <el-empty v-else :description="$t('common.noData')"/>
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

        <el-table-column prop="nick_name" :label="$t('common.creator')" show-overflow-tooltip/>
        <el-table-column :label="$t('views.application.publishTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.update_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.createTime')" width="180">
          <template #default="{ row }">
            {{ datetimeFormat(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.operation')" align="left" width="120" fixed="right">
          <template #default="{ row }">
            <el-tooltip
              effect="dark"
              :content="$t('views.application.operation.toChat')"
              placement="top"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  :title="$t('views.application.operation.toChat')"
                  @click.stop="toChat(row)"
                >
                  <AppIcon iconName="app-create-chat"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip
              effect="dark"
              :content="$t('views.system.resource_management.management')"
              placement="top"
              v-if="managePermission()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  :title="$t('views.system.resource_management.management')"
                  @click="
                    router.push({
                      path: `/application/resource-management/${row.id}/${row.type}/overview`,
                    })
                  "
                >
                  <AppIcon iconName="app-admin-operation"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-dropdown trigger="click" v-if="MoreFilledPermission()">
              <el-button text @click.stop type="primary">
                <AppIcon iconName="app-more"></AppIcon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    @click.stop="openAuthorization(row)"
                    v-if="permissionPrecise.auth()"
                  >
                    <AppIcon
                      iconName="app-resource-authorization"
                      class="color-secondary"
                    ></AppIcon>
                    {{ $t('views.system.resourceAuthorization.title') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="exportApplication(row)"
                    v-if="permissionPrecise.export()"
                  >
                    <AppIcon iconName="app-export" class="color-secondary"></AppIcon>
                    {{ $t('common.export') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="deleteApplication(row)"
                    v-if="permissionPrecise.delete()"
                  >
                    <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                    {{ $t('common.delete') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </app-table>
    </el-card>
    <ResourceAuthorizationDrawer
      :type="SourceTypeEnum.APPLICATION"
      ref="ResourceAuthorizationDrawerRef"
    />
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, reactive, computed, watch} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import ApplicationResourceApi from '@/api/system-resource-management/application'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import {t} from '@/locales'
import {isAppIcon, resetUrl} from '@/utils/common'
import useStore from '@/stores'
import {datetimeFormat} from '@/utils/time'
import {loadPermissionApi} from '@/utils/dynamics-api/permission-api.ts'
import {isWorkFlow} from '@/utils/application.ts'
import UserApi from '@/api/user/user.ts'
import permissionMap from '@/permission'
import {MsgSuccess, MsgConfirm, MsgError} from '@/utils/message'
import {SourceTypeEnum} from '@/enums/common'

const router = useRouter()
const route = useRoute()
const {user, application} = useStore()

const permissionPrecise = computed(() => {
  return permissionMap['application']['systemManage']
})

const managePermission = () => {
  return (
    permissionPrecise.value.overview_read() ||
    permissionPrecise.value.access_read() ||
    permissionPrecise.value.edit() ||
    permissionPrecise.value.chat_log_read() ||
    permissionPrecise.value.chat_user_read()
  )
}

const MoreFilledPermission = () => {
  return (
    permissionPrecise.value.export() ||
    permissionPrecise.value.delete() ||
    permissionPrecise.value.auth()
  )
}

const ResourceAuthorizationDrawerRef = ref()

function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

const apiInputParams = ref([])

function toChat(row: any) {
  row?.work_flow?.nodes
    ?.filter((v: any) => v.id === 'base-node')
    .map((v: any) => {
      apiInputParams.value = v.properties.api_input_field_list
        ? v.properties.api_input_field_list.map((v: any) => {
          return {
            name: v.variable,
            value: v.default_value,
          }
        })
        : v.properties.input_field_list
          ? v.properties.input_field_list
            .filter((v: any) => v.assignment_method === 'api_input')
            .map((v: any) => {
              return {
                name: v.variable,
                value: v.default_value,
              }
            })
          : []
    })
  const apiParams = mapToUrlParams(apiInputParams.value)
    ? '?' + mapToUrlParams(apiInputParams.value)
    : ''
  ApplicationResourceApi.getAccessToken(row.id, loading).then((res: any) => {
    window.open(application.location + res?.data?.access_token + apiParams)
  })
}

function mapToUrlParams(map: any[]) {
  const params = new URLSearchParams()

  map.forEach((item: any) => {
    params.append(encodeURIComponent(item.name), encodeURIComponent(item.value))
  })

  return params.toString() // 返回 URL 查询字符串
}

function deleteApplication(row: any) {
  MsgConfirm(
    `${t('views.application.delete.confirmTitle')}${row.name} ?`,
    row.resource_count > 0 ? t('views.application.delete.resourceCountMessage', row.resource_count) : '',
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      ApplicationResourceApi.delApplication(row.id, loading).then(() => {
        const index = applicationList.value.findIndex((v) => v.id === row.id)
        applicationList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {
    })
}

const exportApplication = (application: any) => {
  ApplicationResourceApi.exportApplication(application.id, application.name, loading).catch((e) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
  type: '',
})
const user_options = ref<any[]>([])
const type_options = ref<any[]>([
  {
    label: t('views.application.senior'),
    value: 'WORK_FLOW',
  },
  {
    label: t('views.application.simple'),
    value: 'SIMPLE',
  },
])
const loading = ref(false)
const applicationList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])
const statusVisible = ref(false)
const statusArr = ref<any[]>([])
const statusOptions = ref<any[]>([
  {
    label: t('common.status.published'),
    value: true,
  },
  {
    label: t('common.status.unpublished'),
    value: false,
  },
])

const filterText = ref('')
const filterData = ref<any[]>([])

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
  {immediate: true},
)

function filterWorkspaceChange(val: string) {
  if (val === 'clear') {
    workspaceArr.value = []
  }
  filterText.value = ''
  getList()
  workspaceVisible.value = false
}

function filterStatusChange(val: string) {
  if (val === 'clear') {
    statusArr.value = []
  }
  getList()
  statusVisible.value = false
}

async function getWorkspaceList() {
  if (user.isEE()) {
    const res = await loadPermissionApi('workspace').getSystemWorkspaceList(loading)
    workspaceOptions.value = res.data.map((item: any) => ({
      label: item.name,
      value: item.id,
    }))
  }
}

const search_type_change = () => {
  search_form.value = {name: '', create_user: '', type: ''}
}

function getList() {
  const params: any = {}
  if (search_form.value[search_type.value]) {
    params[search_type.value] = search_form.value[search_type.value]
  }
  if (workspaceArr.value.length > 0) {
    params['workspace_ids'] = JSON.stringify(workspaceArr.value)
  }
  if (statusArr.value.length > 0) {
    params['status'] = JSON.stringify(statusArr.value)
  }
  ApplicationResourceApi.getApplication(paginationConfig, params, loading).then((res: any) => {
    paginationConfig.total = res.data?.total
    applicationList.value = res.data?.records
  })
}

onMounted(() => {
  getWorkspaceList()
  getList()

  UserApi.getAllMemberList('').then((res: any) => {
    user_options.value = res.data
  })
})
</script>

<style lang="scss" scoped></style>
