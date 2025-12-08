<template>
  <el-drawer v-model="debugVisible" size="60%" :append-to-body="true">
    <template #header>
      <h4>{{ $t('views.document.tag.setting') }}</h4>
    </template>
    <div class="flex-between mb-16">
      <div>
        <el-button type="primary" @click="openAddTagDialog()">
          {{ $t('views.document.tag.addTag') }}
        </el-button>
        <el-button :disabled="multipleSelection.length === 0" @click="batchDelete">
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
    >
      <el-table-column type="selection" width="55" />
      <el-table-column :label="$t('views.document.tag.key')">
        <template #default="{ row }">
          <div class="flex-between">
            {{ row.key }}
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="$t('views.document.tag.value')" class-name="border-l">
        <template #default="{ row }">
          {{ row.value }}
        </template>
      </el-table-column>
      <el-table-column :label="$t('common.operation')" align="left" width="100" fixed="right">
        <template #default="{ row }">
          <el-tooltip effect="dark" :content="$t('common.delete')">
            <el-button type="primary" text @click.stop="delTagValue(row)">
              <AppIcon iconName="app-delete" />
            </el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </el-drawer>
  <AddTagDialog ref="addTagDialogRef" @addTags="addTags" :apiType="apiType" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { MsgConfirm } from '@/utils/message.ts'
import { t } from '@/locales'
import AddTagDialog from '@/views/document/tag/MulAddTagDialog.vue'

const emit = defineEmits(['refresh'])
const route = useRoute()
const {
  params: { id, folderId }, // id为knowledgeID
} = route as any

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const isShared = computed(() => {
  return folderId === 'share'
})

const document_id = ref('')
const loading = ref(false)
const debugVisible = ref(false)
const filterText = ref('')
const tags = ref<Array<any>>([])

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

function batchDelete() {
  const tagsToDelete = multipleSelection.value.reduce((acc, item) => {
    // 找出当前选中项的key对应的所有value id
    const sameKeyItems = tableData.value.filter((data) => data.key === item.key)
    const sameKeyIds = sameKeyItems.map((data) => data.id)
    return [...acc, ...sameKeyIds]
  }, [] as string[])

  loadSharedApi({ type: 'document', systemType: apiType.value })
    .delMulDocumentTag(id, document_id.value, tagsToDelete, loading)
    .then(() => {
      getList()
    })
}

function delTagValue(row: any) {
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .delMulDocumentTag(id, document_id.value, [row.id], loading)
    .then(() => {
      getList()
    })
}

function getList() {
  const params = {
    ...(filterText.value && { name: filterText.value }),
  }
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .getDocumentTags(id, document_id.value, params, loading)
    .then((res: any) => {
      tags.value = res.data
    })
}

const addTagDialogRef = ref()

function openAddTagDialog() {
  addTagDialogRef.value?.open()
}

function addTags(tags: any) {
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .postDocumentTags(id, document_id.value, tags, loading)
    .then(() => {
      addTagDialogRef.value?.close()
      getList()
    })
}

const open = (doc: any) => {
  filterText.value = ''
  debugVisible.value = true
  document_id.value = doc.id

  getList()
}

defineExpose({
  open,
})
</script>
<style lang="scss"></style>
