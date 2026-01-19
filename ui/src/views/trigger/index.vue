<template>
  <div class="document p-16-24">
    <h2 class="mb-16">{{ $t('view.trigger.name', '触发器') }}</h2>
    <el-card style="--el-card-padding: 0">
      <div class="main-calc-height">
        <div class="p-24">
          <div class="flex-between">
            <div>
              <el-button
                type="primary"
                @click="
                  router.push({
                    path: `/knowledge/document/upload/${folderId}/${type}`,
                    query: { id: id },
                  })
                "
                >{{ $t('common.create') }}
              </el-button>
            </div>
          </div>
          <app-table
            ref="multipleTableRef"
            class="mt-16 document-table"
            :data="triggerData"
            :pagination-config="paginationConfig"
            @sizeChange="handleSizeChange"
            @changePage="getList"
            v-loading="loading"
            :row-key="(row: any) => row.id"
            :maxTableHeight="300"
          >
            <el-table-column type="selection" width="55" :reserve-selection="true" />
            <el-table-column
              prop="name"
              :label="$t('views.trigger.table.name', '名称')"
              min-width="280"
            >
            </el-table-column>
            <el-table-column
              prop="desc"
              :label="$t('views.trigger.table.desc', '描述')"
              min-width="280"
            >
            </el-table-column>
            <el-table-column
              prop="is_active"
              :label="$t('views.trigger.table.status', '状态')"
              min-width="280"
            >
            </el-table-column>
            <el-table-column
              prop="trigger_type"
              :label="$t('views.trigger.table.type', '类型')"
              align="right"
              min-width="90"
            >
            </el-table-column>

            <el-table-column
              prop="update_time"
              :label="$t('views.document.table.updateTime')"
              width="175"
              sortable
            >
              <template #default="{ row }">
                {{ datetimeFormat(row.update_time) }}
              </template>
            </el-table-column>
            <el-table-column align="left" width="160" fixed="right" :label="$t('common.operation')">
              <template #default="{ row }">
                <span @click.stop>
                  <el-switch :loading="loading" size="small" v-model="row.is_active" />
                </span>
                <el-divider direction="vertical" />
                <el-tooltip effect="dark" :content="$t('common.edit')" placement="top">
                  <span class="mr-4">
                    <el-button type="primary" text>
                      <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                    </el-button>
                  </span>
                </el-tooltip>
                <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                  <span class="mr-4">
                    <el-button type="primary" text>
                      <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                    </el-button>
                  </span>
                </el-tooltip>
              </template>
            </el-table-column>
          </app-table>
        </div>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import type { ElTable } from 'element-plus'
import ImportDocumentDialog from './component/ImportDocumentDialog.vue'
import SelectKnowledgeDialog from './component/SelectKnowledgeDialog.vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import triggerAPI from '@/api/trigger/trigger'
import { TaskType, State } from '@/utils/status'
import { t } from '@/locales'
import permissionMap from '@/permission'
import { datetimeFormat } from '@/utils/time'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const route = useRoute()
const router = useRouter()
const {
  params: { id, folderId, type }, // id为knowledgeID
} = route as any
const { common } = useStore()
const loading = ref(false)
const paginationConfig = ref({
  current_page: 1,
  page_size: 10,
  total: 0,
})

const multipleSelection = ref<any[]>([])
const triggerData = ref<any[]>([])
const elUploadRef = ref()

function handleSizeChange() {
  paginationConfig.value.current_page = 1
  getList()
}

function getList(bool?: boolean) {
  const param = {}
  triggerAPI
    .pageTrigger(paginationConfig.value, param, bool ? undefined : loading)
    .then((res: any) => {
      triggerData.value = res.data.records
      paginationConfig.value.total = res.data.total
    })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped>
.document {
  .mul-operation {
    position: fixed;
    margin-left: var(--sidebar-width);
    bottom: 0;
    right: 24px;
    width: calc(100% - var(--sidebar-width) - 48px);
    padding: 16px 24px;
    box-sizing: border-box;
    background: #ffffff;
    z-index: 22;
    box-shadow: 0px -2px 4px 0px rgba(31, 35, 41, 0.08);
  }
  .document-table {
    :deep(.el-table__row) {
      cursor: pointer;
    }
  }
}
</style>
