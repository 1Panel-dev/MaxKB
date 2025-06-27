<template>
  <div class="p-16-24">
    <el-breadcrumb separator-icon="ArrowRight">
      <el-breadcrumb-item>{{ t('views.system.resource_management.label') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.model.title') }}</h5>
      </el-breadcrumb-item>
    </el-breadcrumb>
    <el-card class="mt-16">
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
            clearable
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.username" />
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
      >
        <!-- <el-table-column type="selection" width="55" /> -->
        <el-table-column width="220" :label="$t('common.name')">
          <template #default="{ row }">
            {{ row.name }}
          </template>
        </el-table-column>
        <el-table-column
          prop="provider"
          :label="$t('views.system.resource_management.type')"
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
                  <div class="form-item mb-16">
                    <div @click.stop>
                      <el-scrollbar height="300" style="margin: 0 0 0 10px">
                        <el-checkbox-group
                          v-model="workspaceArr"
                          style="display: flex; flex-direction: column"
                        >
                          <el-checkbox
                            v-for="item in workspaceOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          />
                        </el-checkbox-group>
                      </el-scrollbar>
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
      </app-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onBeforeMount, onMounted, ref, reactive, nextTick, computed } from 'vue'
import { cloneDeep, get } from 'lodash'
import type { Provider, Model } from '@/api/type/model'
import ModelResourceApi from '@/api/system-resource-management/model'
import { modelTypeList } from '@/views/model/component/data'
import { modelType } from '@/enums/model'
import { t } from '@/locales'
import useStore from '@/stores'
import WorkspaceApi from '@/api/workspace/workspace.ts'
import { datetimeFormat } from '@/utils/time'

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
const changeStateloading = ref(false)
const modelList = ref<Array<Model>>([])
const user_options = ref<any[]>([])
const provider_list = ref<Array<Provider>>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})

const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])

const getRowProvider = computed(() => {
  return (row: any) => {
    return provider_list.value.find((p) => p.provider === row.provider)
  }
})
function filterWorkspaceChange(val: string) {
  if (val === 'clear') {
    workspaceArr.value = []
  }
  getList()
  workspaceVisible.value = false
}
async function getWorkspaceList() {
  if (user.isEE()) {
    const res = await WorkspaceApi.getSystemWorkspaceList(loading)
    workspaceOptions.value = res.data.map((item: any) => ({
      label: item.name,
      value: item.id,
    }))
  }
}
const search_type_change = () => {
  model_search_form.value = { name: '', create_user: '', model_type: '' }
}

function getList() {
  ModelResourceApi.getModelListPage(paginationConfig, model_search_form.value, loading).then(
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
})
</script>

<style lang="scss" scoped></style>
