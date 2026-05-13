<template>
  <div class="chat-entry p-16-24" v-loading="loading">
    <!-- 头部：标题 + 搜索 -->
    <div class="chat-entry__header flex-between mb-16">
      <div>
        <h4>{{ $t('views.chatEntry.title') }}</h4>
        <el-text type="info" size="small">{{ $t('views.chatEntry.subTitle') }}</el-text>
      </div>
      <el-input
        v-model="search"
        :placeholder="$t('views.chatEntry.search.placeholder')"
        clearable
        style="width: 280px"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <el-alert
      v-if="filteredList.length > 0"
      class="mb-16"
      :title="$t('views.chatEntry.hint.onlyPublished')"
      type="info"
      :closable="false"
      show-icon
    />

    <!-- 卡片网格 -->
    <el-row :gutter="16" v-if="filteredList.length > 0">
      <el-col
        v-for="item in filteredList"
        :key="item.id"
        :xs="24" :sm="12" :md="12" :lg="8" :xl="6"
        class="mb-16"
      >
        <div
          class="chat-card"
          @click="toChat(item)"
          @keydown.enter="toChat(item)"
          tabindex="0"
          role="button"
        >
          <div class="chat-card__head flex align-center">
            <el-avatar shape="square" :size="40" class="mr-8">
              <img v-if="item.icon" :src="resolveIcon(item.icon)" />
              <AppIcon v-else iconName="app-agent" />
            </el-avatar>
            <div class="chat-card__title-block flex-1">
              <div class="chat-card__title">{{ item.name }}</div>
              <el-text class="color-secondary" size="small">
                {{ item.nick_name || '' }}
              </el-text>
            </div>
            <el-tag size="small" v-if="isWorkflow(item.type)">
              {{ $t('views.chatEntry.card.workflow') }}
            </el-tag>
            <el-tag size="small" type="info" v-else>
              {{ $t('views.chatEntry.card.simple') }}
            </el-tag>
          </div>

          <div class="chat-card__desc" :title="item.desc || ''">
            {{ item.desc || ' ' }}
          </div>

          <div class="chat-card__footer flex-between">
            <el-text size="small" class="color-secondary">
              {{ updatedLabel(item) }}
            </el-text>
            <el-button type="primary" plain size="small" @click.stop="toChat(item)">
              <AppIcon iconName="app-create-chat" class="mr-4" />
              {{ $t('views.chatEntry.card.chat') }}
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 空态 -->
    <el-empty v-if="!loading && filteredList.length === 0" :description="emptyDescription">
      <template #image>
        <AppIcon iconName="app-user-chat" style="font-size: 60px; color: var(--el-color-info);" />
      </template>
      <div class="mt-8">
        <el-text type="info" size="small">{{ $t('views.chatEntry.empty.hint') }}</el-text>
      </div>
      <el-button type="primary" class="mt-12" @click="goCreateAgent">
        {{ $t('views.chatEntry.empty.goCreate') }}
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import ApplicationApi from '@/api/application/application'
import useStore from '@/stores'
import { t } from '@/locales'

const router = useRouter()
const { application } = useStore()

const loading = ref(false)
const search = ref('')
const list = ref<any[]>([])

function isWorkflow(type: string) {
  return type === 'WORK_FLOW'
}

function resolveIcon(icon: string) {
  if (!icon) return ''
  // 后端返回的图标可能是相对路径 './oss/file/<uuid>' 或绝对 URL
  return icon
}

function updatedLabel(item: any) {
  const d = item.update_time || item.create_time
  if (!d) return ''
  try {
    return new Date(d).toLocaleString()
  } catch (e) {
    return d
  }
}

const filteredList = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return list.value
  return list.value.filter((x) => (x.name || '').toLowerCase().includes(q))
})

const emptyDescription = computed(() => t('views.chatEntry.empty.noPublished'))

async function loadList() {
  loading.value = true
  try {
    const res: any = await ApplicationApi.getAllApplication({} as any, loading)
    const all: any[] = Array.isArray(res?.data) ? res.data : []
    // 仅展示已发布的智能体（is_publish === true）。
    // 后端 API 暂无 publish_status 过滤参数（实际上 search_form 走的是 list 路径），
    // 这里前端过滤已经够用，覆盖所有应用列表场景。
    list.value = all.filter((x) => x.is_publish === true)
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function toChat(row: any) {
  // 复用 application/index.vue 的 toChat 行为：拿到 access_token → 新页签打开
  const api =
    row.type === 'WORK_FLOW'
      ? (id: string) => ApplicationApi.getApplicationDetail(id)
      : (id: string) => Promise.resolve({ data: row })

  api(row.id).then((ok: any) => {
    // 工作流应用可能有 API 输入字段，拼成 query string；简单应用无此需求
    let aips: Array<{ name: string; value: any }> = []
    try {
      const baseNodes = (ok?.data?.work_flow?.nodes || []).filter(
        (v: any) => v.id === 'base-node',
      )
      const lists = baseNodes.map((v: any) => {
        if (v?.properties?.api_input_field_list) {
          return v.properties.api_input_field_list.map((x: any) => ({
            name: x.variable,
            value: x.default_value,
          }))
        }
        if (v?.properties?.input_field_list) {
          return v.properties.input_field_list
            .filter((x: any) => x.assignment_method === 'api_input')
            .map((x: any) => ({ name: x.variable, value: x.default_value }))
        }
        return []
      })
      aips = lists.reduce((acc: any[], cur: any[]) => [...acc, ...cur], [])
    } catch (e) {
      aips = []
    }

    const params = new URLSearchParams()
    aips.forEach((p: any) => {
      if (p.name) params.append(p.name, p.value ?? '')
    })
    const qs = params.toString() ? '?' + params.toString() : ''

    ApplicationApi.getAccessToken(row.id, loading).then((res: any) => {
      const accessToken = res?.data?.access_token
      if (!accessToken) return
      const url = application.location + accessToken + qs
      window.open(url)
    })
  })
}

function goCreateAgent() {
  router.push({ name: 'application' })
}

onMounted(() => {
  loadList()
})
</script>

<style lang="scss" scoped>
.chat-entry {
  min-height: 100%;

  &__header {
    h4 {
      margin: 0 0 4px 0;
    }
  }
}

.chat-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.18s, transform 0.18s, border-color 0.18s;
  height: 100%;
  display: flex;
  flex-direction: column;
  outline: none;

  &:hover,
  &:focus {
    border-color: var(--el-color-primary);
    box-shadow: 0 4px 16px 0 rgba(var(--el-text-color-primary-rgb), 0.08);
    transform: translateY(-1px);
  }

  &__head {
    margin-bottom: 10px;
  }

  &__title {
    font-weight: 500;
    color: var(--el-text-color-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
  }

  &__title-block {
    overflow: hidden;
  }

  &__desc {
    color: var(--el-text-color-regular);
    font-size: 13px;
    line-height: 1.5;
    height: 42px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    margin-bottom: 12px;
  }

  &__footer {
    margin-top: auto;
  }
}
</style>
