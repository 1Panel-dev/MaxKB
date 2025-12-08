<template>
  <div class="p-16-24">
    <el-breadcrumb separator-icon="ArrowRight">
      <el-breadcrumb-item>{{ t('views.system.resource_management.label') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.model.title') }}</h5>
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
            <el-option :label="$t('common.creator')" value="create_user" />
            <el-option :label="$t('views.model.modelForm.model_type.label')" value="model_type" />
            <el-option :label="$t('views.model.modelForm.modeName.label')" value="name" />
          </el-select>
          <el-input
            v-if="search_type === 'name'"
            v-model="model_search_form.name"
            @change="getList"
            :placeholder="$t('common.searchBar.placeholder')"
            style="width: 220px"
            clearable
          />
          <el-select
            v-else-if="search_type === 'create_user'"
            v-model="model_search_form.create_user"
            @change="getList"
            filterable
            clearable
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.nick_name" />
          </el-select>
          <el-select
            v-else-if="search_type === 'model_type'"
            v-model="model_search_form.model_type"
            clearable
            @change="getList"
            style="width: 220px"
          >
            <template v-for="item in modelTypeList" :key="item.value">
              <el-option :label="item.text" :value="item.value" />
            </template>
          </el-select>
        </div>
      </div>

      <app-table
        :data="modelList"
        :pagination-config="paginationConfig"
        @sizeChange="getList"
        @changePage="getList"
        :maxTableHeight="260"
      >
        <!-- <el-table-column type="selection" width="55" /> -->
        <el-table-column width="220" :label="$t('common.name')" show-overflow-tooltip>
          <template #default="{ row }">
            <el-space :size="8">
              <span
                style="width: 24px; height: 24px; display: inline-block"
                :innerHTML="getRowProvider(row)?.icon"
              >
              </span>
              <span> {{ row.name }}</span>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column
          prop="provider"
          :label="$t('views.model.provider')"
          show-overflow-tooltip
          width="150"
        >
          <template #default="{ row }">
            <el-space :size="8">
              <span
                style="width: 24px; height: 24px; display: inline-block"
                :innerHTML="getRowProvider(row)?.icon"
              >
              </span>
              <span> {{ getRowProvider(row)?.name }}</span>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column width="120" :label="$t('views.model.modelForm.model_type.label')">
          <template #default="{ row }">
            {{ $t(modelType[row.model_type as keyof typeof modelType]) }}
          </template>
        </el-table-column>
        <el-table-column
          width="220"
          :label="$t('views.model.modelForm.base_model.label')"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.model_name }}
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
        <el-table-column prop="nick_name" :label="$t('common.creator')" show-overflow-tooltip />
        <el-table-column :label="$t('views.document.table.updateTime')" width="180">
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
              :content="$t('common.modify')"
              placement="top"
              v-if="permissionPrecise.modify()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  :title="$t('common.modify')"
                  @click.stop="openEditModel(row)"
                >
                  <AppIcon iconName="app-edit"></AppIcon>
                </el-button>
              </span>
            </el-tooltip>
            <el-tooltip
              effect="dark"
              :content="$t('views.system.resourceAuthorization.title')"
              placement="top"
              v-if="permissionPrecise.auth()"
            >
              <span class="mr-8">
                <el-button
                  type="primary"
                  text
                  :title="$t('views.system.resourceAuthorization.title')"
                  @click.stop="openAuthorization(row)"
                >
                  <AppIcon iconName="app-resource-authorization"></AppIcon>
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
                    @click.stop="openParamSetting(row)"
                    v-if="
                      ['TTS','LLM','IMAGE','TTI','STT','EMBEDDING'].includes(row.model_type) &&
                      permissionPrecise.paramSetting()
                    "
                  >
                    <AppIcon iconName="app-setting" class="color-secondary"></AppIcon>
                    {{ $t('views.model.modelForm.title.paramSetting') }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    @click.stop="deleteModel(row)"
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
    <EditModel ref="editModelRef" @submit="getList"></EditModel>
    <ParamSettingDialog ref="paramSettingRef" />
    <ResourceAuthorizationDrawer
      :type="SourceTypeEnum.MODEL"
      ref="ResourceAuthorizationDrawerRef"
    />
  </div>
</template>

<script lang="ts" setup>
import { onBeforeMount, onMounted, ref, reactive, watch, computed } from 'vue'
import type { Provider, Model } from '@/api/type/model'
import EditModel from '@/views/model/component/EditModel.vue'
import ParamSettingDialog from '@/views/model/component/ParamSettingDialog.vue'
import ModelResourceApi from '@/api/system-resource-management/model'
import ResourceAuthorizationDrawer from '@/components/resource-authorization-drawer/index.vue'
import { SourceTypeEnum } from '@/enums/common'
import { modelTypeList } from '@/views/model/component/data'
import { modelType } from '@/enums/model'
import { t } from '@/locales'
import useStore from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { loadPermissionApi } from '@/utils/dynamics-api/permission-api.ts'
import UserApi from '@/api/user/user.ts'
import permissionMap from '@/permission'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

const { user, model } = useStore()

const search_type = ref('name')
const model_search_form = ref<{
  name: string
  create_user: string
  model_type: string
}>({
  name: '',
  create_user: '',
  model_type: '',
})

const loading = ref(false)
const modelList = ref<Array<Model>>([])
const user_options = ref<any[]>([])
const provider_list = ref<Array<Provider>>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0,
})

const MoreFilledPermission = () => {
  return permissionPrecise.value.delete() || permissionPrecise.value.modify()
}

const ResourceAuthorizationDrawerRef = ref()
function openAuthorization(item: any) {
  ResourceAuthorizationDrawerRef.value.open(item.id)
}

const deleteModel = (row: any) => {
  MsgConfirm(
    `${t('views.model.delete.confirmTitle')}${row.name} ?`,
    t('views.model.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      ModelResourceApi.deleteModel(row.id).then(() => {
        getList()
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

const paramSettingRef = ref<InstanceType<typeof ParamSettingDialog>>()
const openParamSetting = (row: any) => {
  paramSettingRef.value?.open(row)
}

const editModelRef = ref<InstanceType<typeof EditModel>>()
const openEditModel = (row: any) => {
  const provider = provider_list.value.find((p) => p.provider === row.provider)
  if (provider) {
    editModelRef.value?.open(provider, row)
  }
}

const permissionPrecise = computed(() => {
  return permissionMap['model']['systemManage']
})

const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])

const getRowProvider = computed(() => {
  return (row: any) => {
    return provider_list.value.find((p) => p.provider === row.provider)
  }
})

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
  { immediate: true },
)

function filterWorkspaceChange(val: string) {
  if (val === 'clear') {
    workspaceArr.value = []
  }
  getList()
  workspaceVisible.value = false
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
  model_search_form.value = { name: '', create_user: '', model_type: '' }
}

function getRequestParams() {
  const obj: any = {
    name: model_search_form.value.name,
    create_user: model_search_form.value.create_user,
    model_type: model_search_form.value.model_type,
  }
  if (workspaceArr.value.length > 0) {
    obj['workspace_ids'] = JSON.stringify(workspaceArr.value)
  }
  return obj
}

function getList() {
  ModelResourceApi.getModelListPage(paginationConfig, getRequestParams(), loading).then(
    (res: any) => {
      paginationConfig.total = res.data?.total
      modelList.value = res.data?.records
    },
  )
}

function getProvider() {
  model.asyncGetProvider(loading).then((res: any) => {
    provider_list.value = res?.data
    getList()
  })
}

onMounted(() => {
  getWorkspaceList()
  getProvider()

  UserApi.getAllMemberList('').then((res: any) => {
    user_options.value = res.data
  })
})
</script>

<style lang="scss" scoped></style>
