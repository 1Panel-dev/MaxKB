<template>
  <el-dialog
    :title="$t('views.application.dialog.addKnowledge')"
    v-model="dialogVisible"
    width="1000"
    append-to-body
    class="addKnowledge-dialog"
    align-center
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId, titleClass }">
      <div class="flex-between mb-8">
        <div class="flex">
          <h4 :id="titleId" :class="titleClass" class="mr-8">
            {{ $t('views.application.dialog.addKnowledge') }}
          </h4>
          <el-text type="info">
            {{ $t('views.application.dialog.addKnowledgePlaceholder') }}
          </el-text>
        </div>

        <el-button link class="mr-24" @click="refresh">
          <el-icon :size="18"><Refresh /></el-icon>
        </el-button>
      </div>
    </template>
    <LayoutContainer class="application-manage">
      <template #left>
        <folder-tree
          :data="folderList"
          :currentNodeKey="currentFolder?.id"
          @handleNodeClick="folderClickHandle"
          v-loading="folderLoading"
          :canOperation="false"
          showShared
          :shareTitle="$t('views.shared.shared_knowledge')"
          :treeStyle="{ height: 'calc(100vh - 240px)' }"
        />
      </template>
      <div class="layout-bg">
        <div class="flex-between p-16 ml-8">
          <h4>{{ currentFolder?.name }}</h4>
          <el-input
            v-model="searchValue"
            :placeholder="$t('common.search')"
            prefix-icon="Search"
            class="w-240 mr-8"
            clearable
          />
        </div>

        <el-scrollbar>
          <div class="p-16-24 pt-0" style="height: calc(100vh - 200px)">
            <el-row :gutter="12" v-loading="loading || apiLoading" v-if="filterData.length">
              <el-col
                :span="12"
                v-for="(item, index) in filterData.filter((v: any) => v.resource_type !== 'folder')"
                :key="index"
                class="mb-16"
              >
                <CardCheckbox
                  value-field="id"
                  :data="item"
                  v-model="checkList"
                  @change="changeHandle"
                >
                  <span class="ellipsis cursor ml-12" :title="item.name"> {{ item.name }}</span>
                </CardCheckbox>
              </el-col>
            </el-row>
            <el-empty :description="$t('common.noData')" v-else />
          </div>
        </el-scrollbar>
      </div>
    </LayoutContainer>

    <template #footer>
      <div class="flex-between">
        <div class="flex">
          <el-text class="color-secondary mr-8" v-if="checkList.length > 0">
            {{ $t('common.selected') }} {{ checkList.length }}
          </el-text>
          <el-button link type="primary" v-if="checkList.length > 0" @click="clearCheck">
            {{ $t('common.clear') }}
          </el-button>
        </div>
        <span>
          <el-button @click.prevent="dialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="submitHandle">
            {{ $t('common.add') }}
          </el-button>
        </span>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import useStore from '@/stores'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { uniqueArray } from '@/utils/array'
const route = useRoute()
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => [],
  },
  loading: Boolean,
})

const emit = defineEmits(['addData'])
const { folder, user } = useStore()
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const dialogVisible = ref<boolean>(false)
const checkList = ref<Array<string>>([])
const currentEmbedding = ref('')
const searchValue = ref('')
const searchData = ref<Array<any>>([])
const knowledgeList = ref<Array<any>>([])
const apiLoading = ref(false)

const filterData = computed(() => {
  return currentEmbedding.value
    ? searchData.value.filter((v) => v.embedding_model_id === currentEmbedding.value)
    : searchData.value
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
    currentEmbedding.value = ''
    searchValue.value = ''
    searchData.value = []
    knowledgeList.value = []
  }
})

watch(searchValue, (val) => {
  if (val) {
    searchData.value = knowledgeList.value.filter(
      (v) => v.name.includes(val) && v.folder_id === currentFolder.value?.id,
    )
  } else {
    searchData.value = knowledgeList.value.filter((v) => v.folder_id === currentFolder.value?.id)
  }
})

function changeHandle() {
  if (checkList.value.length > 0) {
    currentEmbedding.value = knowledgeList.value?.find(
      (v) => v.id === checkList.value[0],
    )?.embedding_model_id
  } else if (checkList.value.length === 0) {
    currentEmbedding.value = ''
  }
}
function clearCheck() {
  checkList.value = []
  currentEmbedding.value = ''
}

const open = (checked: any) => {
  checkList.value = checked
  getFolder()
  if (checkList.value.length > 0) {
    currentEmbedding.value = props.data.filter(
      (v) => v.id === checkList.value[0],
    )[0].embedding_model_id
  }

  dialogVisible.value = true
}

const submitHandle = () => {
  emit(
    'addData',
    knowledgeList.value.filter((item: any) => checkList.value.includes(item.id)),
  )
  dialogVisible.value = false
}

const refresh = () => {
  searchValue.value = ''
  knowledgeList.value = []
  getList()
}

const folderList = ref<any[]>([])
const currentFolder = ref<any>({})
const folderLoading = ref(false)
// 文件
function folderClickHandle(row: any) {
  if (row.id === currentFolder.value?.id) {
    return
  }
  currentFolder.value = row
  getList()
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder('KNOWLEDGE', params, folderLoading).then((res: any) => {
    folderList.value = res.data
    currentFolder.value = res.data?.[0] || {}
    getList()
  })
}

function getList() {
  const folder_id = currentFolder.value?.id || user.getWorkspaceId()
  loadSharedApi({
    type: 'knowledge',
    isShared: folder_id === 'share',
    systemType: apiType.value,
  })
    .getKnowledgeList({ folder_id }, apiLoading)
    .then((res: any) => {
      knowledgeList.value = uniqueArray([...knowledgeList.value, ...res.data], 'id')
      searchData.value = res.data
    })
}

defineExpose({ open })
</script>
<style lang="scss">
.addKnowledge-dialog {
  padding: 0;
  .el-dialog__header {
    padding: 12px 20px 4px 24px;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  .el-dialog__footer {
    padding: 12px 24px 12px 24px;
    border-top: 1px solid var(--el-border-color-light);
  }

  .el-dialog__headerbtn {
    top: 2px;
    right: 6px;
  }
}
</style>
