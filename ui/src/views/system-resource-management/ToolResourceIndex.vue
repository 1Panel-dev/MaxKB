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
        <el-table-column type="selection" width="55" />
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
        <el-table-column
          prop="tool_type"
          :label="$t('views.application.form.appType.label')"
          width="120"
        />
        <el-table-column :label="$t('common.status.label')" width="120">
          <template #default="scope">
            <div class="flex align-center">
              <AppIcon
                :iconName="scope.row.is_active ? 'app-close_colorful' : 'app-succeed'"
              ></AppIcon>
              {{ $t(scope.row.is_active ? 'views.tool.enabled' : 'common.status.disable') }}
            </div>
          </template>
        </el-table-column>
        <!-- <el-table-column width="100" property="workspace_name">
            <template #header>
              <div class="flex align-center">
                {{ $t('views.role.member.workspace') }}

                <el-popover placement="bottom">
                  <template #reference
                    ><el-icon style="margin-left: 4px; cursor: pointer" size="16">
                      <AppIcon iconName="app-filter_outlined"></AppIcon> </el-icon
                  ></template>
                  <div>
                    <el-checkbox
                      v-model="checkAll"
                      :indeterminate="isIndeterminate"
                      @change="handleCheckAllChange"
                    >
                      {{ $t('views.document.feishu.allCheck') }}
                    </el-checkbox>
                    <el-checkbox-group
                      v-model="checkedWorkspaces"
                      @change="handleCheckedWorkspacesChange"
                    >
                      <el-checkbox
                        v-for="workspace in workspaces"
                        :key="workspace"
                        :label="workspace"
                        :value="workspace"
                      >
                        {{ workspace }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </el-popover>
              </div>
            </template>
          </el-table-column> -->
        <el-table-column prop="nick_name" :label="$t('common.creator')" />
        <!-- <el-table-column
          prop="update_time"
          sortable
          width="180"
          :formatter="formatter"
          :label="$t('views.document.table.updateTime')"
        />
        <el-table-column
          width="180"
          prop="create_time"
          sortable
          :formatter="formatter"
          :label="$t('common.createTime')"
        /> -->
      </app-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { cloneDeep, get } from 'lodash'
import ToolApi from '@/api/system-resource-management/tool'
import { t } from '@/locales'
import { isAppIcon } from '@/utils/common'

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

const search_type_change = () => {
  search_form.value = { name: '', create_user: '' }
}

function getList() {
  const params = {
    [search_type.value]: search_form.value[search_type.value],
  }
  ToolApi.getToolListPage(paginationConfig, params, loading).then((res) => {
    paginationConfig.total = res.data?.total
    toolList.value = res.data?.records
  })
}

onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.resource-manage_tool {
}
</style>
