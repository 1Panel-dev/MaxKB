<template>
  <el-dialog
    v-model="dialogVisible"
    width="1000"
    append-to-body
    class="tool-store-dialog"
    align-center
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId }">
      <div class="dialog-header flex-between mb-8">
        <h4 :id="titleId" class="medium w-240 mr-8">
          {{ $t('workflow.setting.templateCenter') }}
        </h4>

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

    <!-- <LayoutContainer v-loading="loading" :minLeftWidth="204">
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
      </template> -->

    <el-scrollbar class="layout-bg" wrap-class="p-16-24 category-scrollbar">
      <template v-if="filterList === null">
        <div v-for="category in categories" :key="category.id">
          <!-- <h4
              class="title-decoration-1 mb-16 mt-8 color-text-primary"
              :id="`category-${category.id}`"
            >
              {{ category.title }}
            </h4> -->
          <el-row :gutter="16">
            <el-col v-for="tool in category.tools" :key="tool.id" :span="8" class="mb-16">
              <TemplateCard
                :tool="tool"
                :addLoading="addLoading"
                :get-sub-title="getSubTitle"
                @handleAdd="handleOpenAdd(tool)"
                @handleDetail="handleDetail(tool)"
              >
              </TemplateCard>
            </el-col>
          </el-row>
        </div>
      </template>
      <div v-else>
        <!-- <h4 class="color-text-primary medium mb-16">
            <span class="color-primary">{{ searchValue }}</span>
            {{ t('views.tool.toolStore.searchResult', { count: filterList.length }) }}
          </h4> -->
        <el-row :gutter="16" v-if="filterList.length">
          <el-col v-for="tool in filterList" :key="tool.id" :span="8" class="mb-16">
            <TemplateCard
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
    <!-- </LayoutContainer> -->
  </el-dialog>
  <InternalDescDrawer ref="internalDescDrawerRef" @addTool="handleOpenAdd" />
  <CreateApplicationDialog ref="CreateKnowledgeDialogRef" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ToolStoreApi from '@/api/tool/store'
import { t } from '@/locales'
import TemplateCard from './TemplateCard.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import InternalDescDrawer from './InternalDescDrawer.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
import CreateApplicationDialog from '@/views/application/component/CreateApplicationDialog.vue'

const { user } = useStore()
const route = useRoute()
const {
  params: { id },
  /*
  folderId 可以区分 resource-management shared还是 workspace
  */
} = route as any

interface ToolCategory {
  id: string
  title: string
  tools: any[]
}

const props = defineProps({
  apiType: {
    type: String as () => 'workspace' | 'systemShare' | 'systemManage' | 'workspaceShare',
    default: 'workspace',
  },
  source: {
    type: String,
    default: 'application',
  },
})
const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const loading = ref(false)
const searchValue = ref('')
const folderId = ref('')
const categories = ref<ToolCategory[]>([])

const filterList = ref<any>(null)

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
  filterList.value = null
  const [v1] = await Promise.all([getStoreToolList()])

  const merged = [...v1].reduce((acc, category) => {
    const existing = acc.find((item: any) => item.id === category.id)
    if (existing) {
      existing.tools = [...existing.tools, ...category.tools]
    } else {
      acc.push({ ...category })
    }
    return acc
  }, [] as ToolCategory[])

  categories.value = merged.filter((item: any) => item.tools.length > 0)
}

async function getStoreToolList() {
  try {
    const res = await ToolStoreApi.getStoreAppList({ name: searchValue.value }, loading)
    const tags = res.data.additionalProperties.tags
    const storeTools = res.data.apps
    let categories = []
    //
    storeTools.forEach((tool: any) => {
      tool.desc = tool.description
    })
    if (searchValue.value.length) {
      filterList.value = [...res.data.apps, ...(filterList.value || [])]
    } else {
      filterList.value = null
      categories = tags.map((tag: any) => ({
        id: tag.key,
        title: tag.name, // 国际化
        tools: storeTools.filter((tool: any) => tool.label === tag.key),
      }))
    }
    return categories
  } catch (error) {
    console.error(error)
    return []
  }
}

const handleClick = (e: MouseEvent) => {
  e.preventDefault()
}

const internalDescDrawerRef = ref<InstanceType<typeof InternalDescDrawer>>()

async function handleDetail(tool: any) {
  internalDescDrawerRef.value?.open(tool.readMe, tool)
}

const CreateKnowledgeDialogRef = ref()

function handleOpenAdd(data?: any, isEdit?: boolean) {
  if (props.source === 'work_flow') {
    MsgConfirm(
      t('common.tip'),
      `${t('views.application.tip.confirmUse')} ${data.name} ${t('views.application.tip.overwrite')}?`,
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
      },
    )
      .then(() => {
        handleStoreAdd(data)
      })
      .catch(() => {})
  } else {
    CreateKnowledgeDialogRef.value.open(folderId.value, 'WORK_FLOW', data)
  }
}

const addLoading = ref(false)

function handleStoreAdd(tool: any) {
  try {
    loadSharedApi({ type: 'application', systemType: props.apiType })
      .putApplication(id, { work_flow_template: tool }, addLoading)
      .then(() => {
        emit('refresh')
        MsgSuccess(t('common.addSuccess'))
      })
    dialogVisible.value = false
  } catch (error) {
    console.error(error)
  }
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
