<template>
  <div class="resource-manage_tool p-16-24">
    <el-breadcrumb separator-icon="ArrowRight">
      <el-breadcrumb-item>{{ t('views.system.resource_management.label') }}</el-breadcrumb-item>
      <el-breadcrumb-item>
        <h5 class="ml-4 color-text-primary">{{ t('views.tool.title') }}</h5>
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

            <el-option :label="$t('views.model.modelForm.modeName.label')" value="name" />
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
            style="width: 220px"
          >
            <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.username" />
          </el-select>
        </div>
      </div>

      <app-table
        :data="toolList"
        :pagination-config="paginationConfig"
        @sizeChange="getList"
        @changePage="getList"
      >
        <!-- <el-table-column type="selection" width="55" /> -->
        <el-table-column width="220" :label="$t('common.name')">
          <template #default="scope">
            <div class="table-name flex align-center">
              <el-icon size="24" class="mr-8">
                <el-avatar
                  v-if="isAppIcon(scope.row?.icon)"
                  shape="square"
                  :size="24"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="scope.row?.icon" alt="" />
                </el-avatar>
                <el-avatar v-else class="avatar-green" shape="square" :size="24">
                  <img src="@/assets/node/icon_tool.svg" style="width: 58%" alt="" />
                </el-avatar>
              </el-icon>
              {{ scope.row.name }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="tool_type" :label="$t('views.system.resource_management.type')">
          <template #default="scope">
            {{ $t(ToolType[scope.row.tool_type as keyof typeof ToolType]) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('common.status.label')" width="120">
          <template #default="{ row }">
            <div v-if="row.is_active" class="flex align-center">
              <el-icon class="color-success mr-8" style="font-size: 16px">
                <SuccessFilled />
              </el-icon>
              <span class="color-secondary">
                {{ $t('common.status.enabled') }}
              </span>
            </div>
            <div v-else class="flex align-center">
              <AppIcon iconName="app-disabled" class="color-secondary mr-8"></AppIcon>
              <span class="color-secondary">
                {{ $t('common.status.disabled') }}
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
import { onMounted, ref, reactive, computed } from 'vue'
import ToolResourceApi from '@/api/system-resource-management/tool'
import { t } from '@/locales'
import { isAppIcon } from '@/utils/common'
import { ToolType } from '@/enums/tool'
import useStore from '@/stores'
import { datetimeFormat } from '@/utils/time'
import {loadPermissionApi} from "@/utils/dynamics-api/permission-api.ts";

const { user } = useStore()

const search_type = ref('name')
const search_form = ref<any>({
  name: '',
  create_user: '',
})
const user_options = ref<any[]>([])

const loading = ref(false)
const changeStateloading = ref(false)
const toolList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})
const workspaceOptions = ref<any[]>([])
const workspaceVisible = ref(false)
const workspaceArr = ref<any[]>([])
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
  search_form.value = { name: '', create_user: '' }
}

function getList() {
  const params = {
    [search_type.value]: search_form.value[search_type.value],
  }
  ToolResourceApi.getToolListPage(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data?.total
    toolList.value = res.data?.records
  })
}

onMounted(() => {
  getWorkspaceList()
  getList()
})
</script>

<style lang="scss" scoped></style>
