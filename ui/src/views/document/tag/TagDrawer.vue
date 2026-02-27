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
      ref="tableRef"
      :data="pagedTableData"
      :span-method="spanMethod"
      v-loading="loading"
      :max-height="tableMaxHeight"
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
    <div class="app-table__pagination mt-16">
      <el-pagination
        v-model:current-page="pageNum"
        v-model:page-size="pageSize"
        :total="groupedByKey.length"
        layout="total, prev, pager, next, sizes"
        :page-sizes="[10, 20, 50, 100]"
      />
    </div>
  </el-drawer>
  <CreateTagDialog ref="createTagDialogRef" @refresh="handleDialogRefresh" />
  <EditTagDialog ref="editTagDialogRef" @refresh="handleDialogRefresh" />
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import CreateTagDialog from './CreateTagDialog.vue'
import { MsgConfirm } from '@/utils/message.ts'
import { t } from '@/locales'
import EditTagDialog from '@/views/document/tag/EditTagDialog.vue'
import permissionMap from '@/permission'

const emit = defineEmits(['refresh', 'tag-changed'])

function notifyTagChanged() {
  emit('tag-changed')
}

function handleDialogRefresh() {
  getList()
  notifyTagChanged()
}

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
const pageNum = ref(1)
const pageSize = ref(20)
const tableMaxHeight = computed(() => `calc(100vh - 260px)`)

function cellMouseEnter(row: any) {
  currentMouseId.value = row.id
}

function cellMouseLeave() {
  currentMouseId.value = null
}

// 1) 仍然把后端全量 tags 转成“扁平行”，每行带上 keyIndex
const tableData = computed(() => {
  const result: any[] = []
  tags.value.forEach((tag: any) => {
    if (tag.values && tag.values.length > 0) {
      tag.values.forEach((value: any, index: number) => {
        result.push({
          id: value.id,
          key: tag.key,
          value: value.value,
          keyIndex: index, // 同一个 key 下第几行
        })
      })
    }
  })
  return result
})

// 2) 按 key 分组（保持 key 的出现顺序）
const groupedByKey = computed(() => {
  const map = new Map<string, any[]>()
  for (const row of tableData.value) {
    if (!map.has(row.key)) map.set(row.key, [])
    map.get(row.key)!.push(row)
  }
  // 每个元素代表一个 key 分组
  return Array.from(map.entries()).map(([key, rows]) => ({ key, rows }))
})

// 3) 按“key 分组”做分页：每页 pageSize 个 key
const pagedGroups = computed(() => {
  const start = (pageNum.value - 1) * pageSize.value
  const end = start + pageSize.value
  return groupedByKey.value.slice(start, end)
})

// 4) 当前页表格数据：把当前页的若干个 key 分组展开为行
const pagedTableData = computed(() => {
  return pagedGroups.value.flatMap((g) => g.rows)
})

// 5) 合并单元格：只在当前页内合并，同一个 key 的第一行 rowspan=该 key 在当前页的行数
const spanMethod = ({ row, columnIndex }: any) => {
  // 注意：你现在有 selection 列，所以 key 列索引是 1；如需同时合并 value 列按需调整
  if (columnIndex === 0 || columnIndex === 1) {
    if (row.keyIndex === 0) {
      const sameKeyCount = pagedTableData.value.filter((item) => item.key === row.key).length
      return { rowspan: sameKeyCount, colspan: 1 }
    }
    return { rowspan: 0, colspan: 0 }
  }
}

const multipleSelection = ref<any[]>([])
const tableRef = ref<any>(null)
const syncingSelection = ref(false)

const handleSelectionChange = async (val: any[]) => {
  if (syncingSelection.value) return

  // 当前已选中的 id 集合（用于判断哪些行刚刚被取消）
  const selectedIds = new Set(val.map((r) => r.id))

  // 找出“刚被取消选中的行”
  const deselectedRows = multipleSelection.value.filter((r) => !selectedIds.has(r.id))
  if (deselectedRows.length === 0) {
    multipleSelection.value = val
    return
  }

  // 取消选中时：把同 key 分组里其它行也一并取消
  syncingSelection.value = true
  await nextTick()

  for (const dr of deselectedRows) {
    const sameGroupRows = pagedTableData.value.filter((r) => r.key === dr.key)
    for (const r of sameGroupRows) {
      if (!selectedIds.has(r.id)) continue
      tableRef.value?.toggleRowSelection?.(r, false)
    }
  }

  await nextTick()
  syncingSelection.value = false

  // 以表格最终状态为准更新缓存（这里直接用传入 val 可能已过期）
  // 简化：重新从表格取 selection（Element Plus 有 store，没暴露就用 val\+补丁）
  multipleSelection.value = pagedTableData.value.filter((r) =>
    tableRef.value?.getSelectionRows
      ? tableRef.value.getSelectionRows().some((s: any) => s.id === r.id)
      : selectedIds.has(r.id),
  )
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
          notifyTagChanged()
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
          notifyTagChanged()
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
          notifyTagChanged()
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
      pageNum.value = 1
    })
}

const open = () => {
  filterText.value = ''
  debugVisible.value = true
  pageNum.value = 1
  getList()
}

defineExpose({
  open,
})
</script>
<style lang="scss"></style>
