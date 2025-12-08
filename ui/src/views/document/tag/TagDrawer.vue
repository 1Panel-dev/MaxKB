<template>
  <el-drawer v-model="debugVisible" size="60%" :append-to-body="true">
    <template #header>
      <h4>{{ $t('views.document.tag.label') }}</h4>
    </template>
    <div class="flex-between mb-16">
      <div>
        <el-button
          type="primary"
          @click="openCreateTagDialog()"
          v-if="permissionPrecise.tag_create(id)"
          >{{ $t('views.document.tag.create') }}
        </el-button>
        <el-button
          :disabled="multipleSelection.length === 0"
          @click="batchDelete"
          v-if="permissionPrecise.tag_delete(id)"
        >
          {{ $t('common.delete') }}
        </el-button>
      </div>
      <el-input
        v-model="filterText"
        prefix-icon="Search"
        class="w-240"
        @change="getList"
        clearable
        :placeholder="$t('common.search')"
      />
    </div>
    <el-table
      :data="tableData"
      :span-method="spanMethod"
      v-loading="loading"
      @selection-change="handleSelectionChange"
      @cell-mouse-enter="cellMouseEnter"
      @cell-mouse-leave="cellMouseLeave"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column :label="$t('views.document.tag.key')">
        <template #default="{ row }">
          <div class="flex-between">
            {{ row.key }}
            <div v-if="currentMouseId === row.id">
              <span class="mr-4">
                <el-tooltip effect="dark" :content="$t('views.document.tag.addValue')">
                  <el-button
                    type="primary"
                    text
                    @click.stop="openCreateTagDialog(row)"
                    v-if="permissionPrecise.tag_create(id)"
                  >
                    <AppIcon iconName="app-add-outlined" />
                  </el-button>
                </el-tooltip>
              </span>
              <span class="mr-4">
                <el-tooltip effect="dark" :content="$t('views.document.tag.edit')">
                  <el-button
                    type="primary"
                    text
                    @click.stop="editTagKey(row)"
                    v-if="permissionPrecise.tag_edit(id)"
                  >
                    <AppIcon iconName="app-edit" />
                  </el-button>
                </el-tooltip>
              </span>
              <el-tooltip effect="dark" :content="$t('common.delete')">
                <el-button
                  type="primary"
                  text
                  @click.stop="delTag(row)"
                  v-if="permissionPrecise.tag_delete(id)"
                >
                  <AppIcon iconName="app-delete" />
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="$t('views.document.tag.value')" class-name="border-l">
        <template #default="{ row }">
          <div class="flex-between">
            {{ row.value }}
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="$t('common.operation')" align="left" width="100" fixed="right">
        <template #default="{ row }">
          <span class="mr-4">
            <el-tooltip effect="dark" :content="$t('views.document.tag.editValue')">
              <el-button
                type="primary"
                text
                @click.stop="editTagValue(row)"
                v-if="permissionPrecise.tag_edit(id)"
              >
                <AppIcon iconName="app-edit" />
              </el-button>
            </el-tooltip>
          </span>
          <el-tooltip effect="dark" :content="$t('common.delete')">
            <el-button
              type="primary"
              text
              @click.stop="delTagValue(row)"
              v-if="permissionPrecise.tag_delete(id)"
            >
              <AppIcon iconName="app-delete" />
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </el-drawer>
  <CreateTagDialog ref="createTagDialogRef" @refresh="getList" />
  <EditTagDialog ref="editTagDialogRef" @refresh="getList" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import CreateTagDialog from './CreateTagDialog.vue'
import { MsgConfirm } from '@/utils/message.ts'
import { t } from '@/locales'
import EditTagDialog from '@/views/document/tag/EditTagDialog.vue'
import permissionMap from '@/permission'

const emit = defineEmits(['refresh'])

const route = useRoute()
const {
  params: { id, folderId }, // id为knowledgeID
} = route as any

const isShared = computed(() => {
  return folderId === 'share'
})

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
const debugVisible = ref(false)
const filterText = ref('')
const tags = ref<Array<any>>([])
const currentMouseId = ref<number | null>(null)

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}

function cellMouseLeave() {
  currentMouseId.value = null
}

// 将原始数据转换为表格数据
const tableData = computed(() => {
  const result: any[] = []
  tags.value.forEach((tag: any) => {
    if (tag.values && tag.values.length > 0) {
      tag.values.forEach((value: any, index: number) => {
        result.push({
          id: value.id,
          key: tag.key,
          value: value.value,
          keyIndex: index, // 用于判断是否为第一行
        })
      })
    }
  })
  return result
})

// 合并单元格方法
const spanMethod = ({ row, column, rowIndex, columnIndex }: any) => {
  if (columnIndex === 0 || columnIndex === 1) {
    // key列 (由于添加了选择列，索引变为1)
    if (row.keyIndex === 0) {
      // 计算当前key有多少个值
      const sameKeyCount = tableData.value.filter((item) => item.key === row.key).length
      return {
        rowspan: sameKeyCount,
        colspan: 1,
      }
    } else {
      return {
        rowspan: 0,
        colspan: 0,
      }
    }
  }
}

const multipleSelection = ref<any[]>([])
const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

const createTagDialogRef = ref()

function openCreateTagDialog(row?: any) {
  createTagDialogRef.value?.open(row)
}

function batchDelete() {
  MsgConfirm(t('views.document.tag.deleteConfirm'), t('views.document.tag.deleteTip'), {
    confirmButtonText: t('common.delete'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      const tagsToDelete = multipleSelection.value.map((item) => item.id)
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .delMulTag(id, tagsToDelete)
        .then(() => {
          getList()
        })
    })
    .catch(() => {})
}

const editTagDialogRef = ref()

function editTagKey(row: any) {
  editTagDialogRef.value?.open(row, true)
}

function delTag(row: any) {
  MsgConfirm(t('views.document.tag.deleteConfirm') + row.key, t('views.document.tag.deleteTip'), {
    confirmButtonText: t('common.delete'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .delTag(id, row.id, 'key')
        .then(() => {
          getList()
        })
    })
    .catch(() => {})
}

function editTagValue(row: any) {
  editTagDialogRef.value?.open(row, false)
}

function delTagValue(row: any) {
  MsgConfirm(t('views.document.tag.deleteConfirm') + row.value, t('views.document.tag.deleteTip'), {
    confirmButtonText: t('common.delete'),
    confirmButtonClass: 'danger',
  })
    .then(() => {
      loadSharedApi({ type: 'knowledge', systemType: apiType.value })
        .delTag(id, row.id, 'one')
        .then(() => {
          getList()
        })
    })
    .catch(() => {})
}

function getList() {
  const params = {
    ...(filterText.value && { name: filterText.value }),
  }
  loadSharedApi({ type: 'knowledge', systemType: apiType.value, isShared: isShared.value })
    .getTags(id, params, loading)
    .then((res: any) => {
      tags.value = res.data
    })
}

const open = () => {
  filterText.value = ''
  debugVisible.value = true
  getList()
}

defineExpose({
  open,
})
</script>
<style lang="scss"></style>
