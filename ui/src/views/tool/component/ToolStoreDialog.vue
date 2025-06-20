<template>
  <el-dialog v-model="dialogVisible" width="1000" append-to-body class="tool-store-dialog" align-center
    :close-on-click-modal="false" :close-on-press-escape="false">
    <template #header="{ titleId }">
      <div class="flex-between mb-8">
        <h4 :id="titleId" class="medium">
          {{ $t('views.tool.toolStore.title') }}
        </h4>

        <div class="flex align-center" style="margin-right: 28px;">
          <el-input v-model="searchValue" :placeholder="$t('common.search')" prefix-icon="Search" class="w-240 mr-8"
            clearable @change="getList" />
          <el-divider direction="vertical" />
        </div>
      </div>
    </template>

    <LayoutContainer v-loading="loading">
      <template #left>
        <el-anchor direction="vertical" :offset="130" type="default" container=".category-scrollbar"
          @click="handleClick">
          <el-anchor-link v-for="category in categories" :key="category.id" :href="`#category-${category.id}`"
            :title="category.title" />
        </el-anchor>
      </template>

      <el-scrollbar class="layout-bg" wrap-class="p-16-24 category-scrollbar">
        <template v-if="filterList === null">
          <div v-for="category in categories" :key="category.id">
            <h4 class="title-decoration-1 mb-16 mt-8 color-text-primary" :id="`category-${category.id}`">
              {{ category.title }}
            </h4>
            <el-row :gutter="16">
              <el-col v-for="tool in category.tools" :key="tool.id" :span="8" class="mb-16">
                <ToolCard :tool="tool" :addLoading="addLoading" :get-sub-title="getSubTitle"
                  @handleAdd="handleAdd(tool)" />
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
            <el-col v-for="tool in filterList" :key="tool.id" :span="8" class="mb-16">
              <ToolCard :tool="tool" :addLoading="addLoading" :get-sub-title="getSubTitle"
                @handleAdd="handleAdd(tool)" />
            </el-col>
          </el-row>
          <el-empty v-else :description="$t('common.noData')" />
        </div>
      </el-scrollbar>
    </LayoutContainer>
  </el-dialog>
</template>

<script setup lang="ts">
import { onBeforeMount, ref } from 'vue'
import ToolApi from '@/api/tool/tool'
import { t } from '@/locales'
import ToolCard from './ToolCard.vue'

interface ToolCategory {
  id: string
  title: string
  tools: any[]
}

const emit = defineEmits(['refresh'])

const dialogVisible = ref(false)
const loading = ref(false)
const searchValue = ref('')

const categories = ref<ToolCategory[]>([
  {
    id: 'recommend',
    title: t('views.tool.toolStore.recommend'),
    tools: []
  },
  {
    id: 'web_search',
    title: t('views.tool.toolStore.webSearch'),
    tools: []
  },
  {
    id: 'database_search',
    title: t('views.tool.toolStore.databaseQuery'),
    tools: []
  },
  {
    id: 'image',
    title: t('views.tool.toolStore.image'),
    tools: []
  },
  {
    id: 'developer',
    title: t('views.tool.toolStore.developer'),
    tools: []
  },
  {
    id: 'communication',
    title: t('views.tool.toolStore.communication'),
    tools: []
  }
])
const filterList = ref<any>(null)

function getSubTitle(tool: any) {
  return categories.value.find(i => i.id === tool.label)?.title ?? ''
}

function open() {
  filterList.value = null
  dialogVisible.value = true
}

onBeforeMount(() => {
  getList()
})

async function getList() {
  try {
    const res = await ToolApi.getInternalToolList({ name: searchValue.value }, loading)
    if (searchValue.value.length) {
      filterList.value = res.data
    } else {
      filterList.value = null
      categories.value.forEach(category => {
        if (category.id === 'recommend') {
          category.tools = res.data
        } else {
          category.tools = res.data.filter((tool: any) => tool.label === category.id)
        }
      })
    }
  } catch (error) {
    console.error(error)
  }
}

const handleClick = (e: MouseEvent) => {
  e.preventDefault()
}

const addLoading = ref(false)
async function handleAdd(tool: any) {
  try {
    await ToolApi.addInternalTool(tool.id, { name: tool.name, folder_id: tool.folder_id }, addLoading)
    dialogVisible.value = false
    emit('refresh')
  } catch (error) {
    console.error(error)
  }
}

defineExpose({ open })
</script>
<style lang="scss">
.tool-store-dialog {
  padding: 0;

  .el-dialog__header {
    padding: 12px 20px 4px 24px;
    border-bottom: 1px solid var(--el-border-color-light);
  }

  .layout-container__left {
    background-color: var(--app-layout-bg-color);
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
    max-height: calc(100vh - 260px);
    min-height: 500px;
  }
}
</style>
