<template>
  <el-dialog
    v-model="dialogVisible"
    width="1200"
    append-to-body
    class="tool-store-dialog"
    align-center
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId }">
      <div class="dialog-header flex-between mb-8">
        <h4 :id="titleId" class="medium w-240 mr-8">
          {{ $t('views.tool.toolStore.title') }}
        </h4>
        <el-radio-group v-model="toolType" @change="radioChange" class="app-radio-button-group">
          <el-radio-button value="INTERNAL">{{
            $t('views.tool.toolStore.internal')
          }}</el-radio-button>
          <el-radio-button value="APPSTORE">{{ $t('views.tool.toolStore.title') }}</el-radio-button>
        </el-radio-group>

        <div class="flex align-center" style="margin-right: 28px">
          <el-input
            v-model="searchValue"
            :placeholder="$t('common.search')"
            prefix-icon="Search"
            class="w-240 mr-8"
            clearable
            @change="getList"
          />
          <el-divider direction="vertical" />
        </div>
      </div>
    </template>

    <LayoutContainer v-loading="loading">
      <template #left>
        <el-anchor
          direction="vertical"
          :offset="130"
          type="default"
          container=".category-scrollbar"
          @click="handleClick"
        >
          <el-anchor-link
            v-for="category in categories"
            :key="category.id"
            :href="`#category-${category.id}`"
            :title="category.title"
          />
        </el-anchor>
      </template>

      <el-scrollbar class="layout-bg" wrap-class="p-16-24 category-scrollbar">
        <template v-if="filterList === null">
          <div v-for="category in categories" :key="category.id">
            <h4
              class="title-decoration-1 mb-16 mt-8 color-text-primary"
              :id="`category-${category.id}`"
            >
              {{ category.title }}
            </h4>
            <el-row :gutter="16">
              <el-col v-for="tool in category.tools" :key="tool.id" :span="12" class="mb-16">
                <ToolCard
                  :tool="tool"
                  :addLoading="addLoading"
                  :get-sub-title="getSubTitle"
                  @handleAdd="handleOpenAdd(tool)"
                  @handleDetail="handleDetail(tool)"
                />
              </el-col>
            </el-row>
          </div>
        </template>
        <div v-else>
          <h4 class="color-text-primary medium mb-16">
            <span class="color-primary">{{ searchValue }}</span>
            {{ t('views.tool.toolStore.searchResult', { count: filterList.length }) }}
          </h4>
          <el-row :gutter="16" v-if="filterList.length">
            <el-col v-for="tool in filterList" :key="tool.id" :span="12" class="mb-16">
              <ToolCard
                :tool="tool"
                :addLoading="addLoading"
                :get-sub-title="getSubTitle"
                @handleAdd="handleOpenAdd(tool)"
                @handleDetail="handleDetail(tool)"
              />
            </el-col>
          </el-row>
          <el-empty v-else :description="$t('common.noData')" />
        </div>
      </el-scrollbar>
    </LayoutContainer>
  </el-dialog>
  <InternalDescDrawer ref="internalDescDrawerRef" @addTool="handleOpenAdd" />
  <AddInternalToolDialog ref="addInternalToolDialogRef" @refresh="handleAdd" />
</template>

<script setup lang="ts">
import { onBeforeMount, ref, watch } from 'vue'
import ToolStoreApi from '@/api/tool/store'
import { t } from '@/locales'
import ToolCard from './ToolCard.vue'
import { MsgSuccess } from '@/utils/message'
import InternalDescDrawer from './InternalDescDrawer.vue'
import AddInternalToolDialog from './AddInternalToolDialog.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import useStore from '@/stores'
const { user } = useStore()
interface ToolCategory {
  id: string
  title: string
  tools: any[]
}
const props = defineProps({
  apiType: {
    type: String as () => 'workspace' | 'systemShare' | 'systemManage',
    default: 'workspace',
  },
})
const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const loading = ref(false)
const searchValue = ref('')
const folderId = ref('')
const toolType = ref('APPSTORE')
const defaultCategories = ref<ToolCategory[]>([
  // 第一版不上
  // {
  //   id: 'recommend',
  //   title: t('views.tool.toolStore.recommend'),
  //   tools: []
  // },
  {
    id: 'web_search',
    title: t('views.tool.toolStore.webSearch'),
    tools: [],
  },
  {
    id: 'database_search',
    title: t('views.tool.toolStore.databaseQuery'),
    tools: [],
  },
  // {
  //   id: 'image',
  //   title: t('views.tool.toolStore.image'),
  //   tools: []
  // },
  // {
  //   id: 'developer',
  //   title: t('views.tool.toolStore.developer'),
  //   tools: []
  // },
  // {
  //   id: 'communication',
  //   title: t('views.tool.toolStore.communication'),
  //   tools: []
  // }
])
const categories = ref<ToolCategory[]>([...defaultCategories.value])

const filterList = ref<any>(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    toolType.value = 'APPSTORE'
  }
})

function getSubTitle(tool: any) {
  return categories.value.find((i) => i.id === tool.label)?.title ?? ''
}

function open(id: string) {
  folderId.value = id
  filterList.value = null
  dialogVisible.value = true

  getList()
}

async function getList() {
  if (toolType.value === 'INTERNAL') {
    await getInternalToolList()
  } else {
    await getStoreToolList()
  }
}

async function getInternalToolList() {
  try {
    categories.value = defaultCategories.value
    const res = await ToolStoreApi.getInternalToolList({ name: searchValue.value }, loading)
    if (searchValue.value.length) {
      filterList.value = res.data
    } else {
      filterList.value = null
      categories.value.forEach((category) => {
        // if (category.id === 'recommend') {
        //   category.tools = res.data
        // } else {
        category.tools = res.data.filter((tool: any) => tool.label === category.id)
        // }
      })
    }
  } catch (error) {
    console.error(error)
  }
}

async function getStoreToolList() {
  try {
    const res = await ToolStoreApi.getStoreToolList({ name: searchValue.value }, loading)
    const tags = res.data.additionalProperties.tags
    const storeTools = res.data.apps
    //
    storeTools.forEach((tool: any) => {
      tool.desc = tool.description
    })
    if (searchValue.value.length) {
      filterList.value = res.data.apps
    } else {
      filterList.value = null
      categories.value = tags.map((tag: any) => ({
        id: tag.key,
        title: tag.name, // 国际化
        tools: storeTools.filter((tool: any) => tool.label === tag.key),
      }))
    }
  } catch (error) {
    console.error(error)
  }
}

const handleClick = (e: MouseEvent) => {
  e.preventDefault()
}

const internalDescDrawerRef = ref<InstanceType<typeof InternalDescDrawer>>()
async function handleDetail(tool: any) {
  if (toolType.value === 'INTERNAL') {
    const index = tool.icon.replace('icon.png', 'detail.md')
    const response = await fetch(index)
    const content = await response.text()
    internalDescDrawerRef.value?.open(content, tool)
  } else {
    internalDescDrawerRef.value?.open(tool.readMe, tool)
  }
}

const addInternalToolDialogRef = ref<InstanceType<typeof AddInternalToolDialog>>()
function handleOpenAdd(data?: any, isEdit?: boolean) {
  addInternalToolDialogRef.value?.open(data, isEdit)
}

const addLoading = ref(false)
async function handleAdd(tool: any) {
  if (toolType.value === 'INTERNAL') {
    await handleInternalAdd(tool)
  } else {
    await handleStoreAdd(tool)
  }
}

async function handleInternalAdd(tool: any) {
  try {
    await loadSharedApi({ type: 'tool', systemType: props.apiType })
      .addInternalTool(tool.id, { name: tool.name, folder_id: folderId.value }, addLoading)
      .then(() => {
        return user.profile()
      })
    emit('refresh')
    MsgSuccess(t('common.addSuccess'))
    dialogVisible.value = false
  } catch (error) {
    console.error(error)
  }
}

async function handleStoreAdd(tool: any) {
  try {
    const obj = {
      name: tool.name,
      folder_id: folderId.value,
      download_url: tool.downloadUrl,
      download_callback_url: tool.downloadCallbackUrl,
      icon: tool.icon,
      versions: tool.versions,
      label: tool.label,
    }
    await loadSharedApi({ type: 'tool', systemType: props.apiType })
      .addStoreTool(tool.id, obj, addLoading)
      .then(() => {
        return user.profile()
      })
    emit('refresh')
    MsgSuccess(t('common.addSuccess'))
    dialogVisible.value = false
  } catch (error) {
    console.error(error)
  }
}

function radioChange() {
  searchValue.value = ''
  getList()
}

defineExpose({ open })
</script>
<style lang="scss">
.tool-store-dialog {
  padding: 0;
  .el-dialog__headerbtn {
    top: 7px;
  }

  .el-dialog__header {
    padding: 12px 20px 4px 24px;
    border-bottom: 1px solid var(--el-border-color-light);

    .dialog-header {
      position: relative;

      .store-type {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
    }
  }

  .layout-container__left {
    background-color: var(--app-layout-bg-color);
    border-radius: 0 0 0 8px;
  }
  .layout-container__right {
    background-color: var(--app-layout-bg-color);
    border-radius: 0 0 8px 0;
  }

  .el-anchor {
    background-color: var(--app-layout-bg-color);

    .el-anchor__marker {
      display: none;
    }

    .el-anchor__list {
      padding: 8px;
    }

    .el-anchor__item {
      .el-anchor__link {
        padding: 8px 16px;
        font-weight: 500;
        font-size: 14px;
        color: var(--el-text-color-primary);
        border-radius: 6px;

        &.is-active {
          color: var(--el-color-primary);
          background-color: #3370ff1a;
        }
      }
    }
  }

  .category-scrollbar {
    height: calc(100vh - 200px);
    // min-height: 500px;
  }
}
</style>
