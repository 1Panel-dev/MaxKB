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

        <div class="flex align-center mr-8">
          <el-input
            v-model="searchValue"
            :placeholder="$t('common.search')"
            prefix-icon="Search"
            class="w-240 mr-8"
            clearable
          />
          <el-divider direction="vertical" />
          <el-button link class="mr-16" @click="refresh">
            <el-icon class="mr-4" :size="18"><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </template>
    <LayoutContainer class="application-manage">
      <template #left>
        <folder-tree
          :data="folderList"
          :currentNodeKey="currentFolder?.id"
          @handleNodeClick="folderClickHandel"
          class="p-8"
          v-loading="folderLoading"
          :canOperation="false"
          showShared
          :shareTitle="$t('views.system.shared.shared_knowledge')"
          :treeStyle="{ height: 'calc(100vh - 320px)' }"
        />
      </template>
      <div class="layout-bg h-full">
        <el-scrollbar>
          <div class="p-16-24">
            <el-row :gutter="12" v-loading="loading">
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
          </div>
        </el-scrollbar>
      </div>
    </LayoutContainer>

    <template #footer>
      <div class="flex-between">
        <div class="flex">
          <el-text type="info" class="color-secondary mr-8" v-if="checkList.length > 0">
            {{ $t('views.application.dialog.selected') }} {{ checkList.length }}
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
import useStore from '@/stores'
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => [],
  },
  loading: Boolean,
})

const emit = defineEmits(['addData', 'refresh'])
const { folder, user, knowledge } = useStore()

const dialogVisible = ref<boolean>(false)
const checkList = ref([])
const currentEmbedding = ref('')
const searchValue = ref('')
const searchDate = ref<any[]>([])
const loading = ref(false)

const filterData = computed(() => {
  return currentEmbedding.value
    ? searchDate.value.filter((v) => v.embedding_model_id === currentEmbedding.value)
    : searchDate.value
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
    currentEmbedding.value = ''
    searchValue.value = ''
  }
})

watch(searchValue, (val) => {
  if (val) {
    searchDate.value = props.data.filter((v) => v.name.includes(val))
  } else {
    searchDate.value = props.data
  }
})

function changeHandle() {
  if (checkList.value.length > 0) {
    currentEmbedding.value = props.data.filter(
      (v) => v.id === checkList.value[0],
    )[0].embedding_model_id
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
  emit('addData', checkList.value)
  dialogVisible.value = false
}

const refresh = () => {
  emit('refresh')
}

const folderList = ref<any[]>([])
const knowledgeList = ref<any[]>([])
const currentFolder = ref<any>({})
const folderLoading = ref(false)
// 文件
function folderClickHandel(row: any) {
  currentFolder.value = row
  knowledgeList.value = []
  if (currentFolder.value.id === 'share') return
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
  knowledge.asyncGetFolderKnowledge(folder_id, loading).then((res: any) => {
    searchDate.value = res.data
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
    top: 6px;
    right: 6px;
  }
}
</style>
