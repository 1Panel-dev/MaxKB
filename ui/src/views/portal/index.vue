<template>
  <div class="portal-page h-full flex">
    <aside class="portal-sidebar border-r shrink-0 flex flex-col bg-white">
      <div class="p-4">
        <el-button class="w-full portal-all-btn" type="primary">
          <MkIcon name="icon_magic_stick_outlined" :size="16" />
          所有智能体
        </el-button>
      </div>
      <div class="portal-history flex-1 overflow-auto px-4 pb-4">
        <div class="text-sm text-gray-400 mb-3 font-medium">对话历史</div>
        <el-empty description="暂无对话历史" :image-size="50" />
      </div>
    </aside>
    <div class="flex-1 p-5 overflow-auto bg-gray-50 portal-content">
      <div class="page-header flex items-center justify-between mb-5">
        <h3>智能体门户</h3>
      </div>
      <el-row :gutter="16" v-loading="loading">
        <el-col
          v-for="item in list"
          :key="item.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          :xl="6"
          class="mb-4"
        >
          <el-card
            shadow="hover"
            class="portal-card"
            @click="goToChat(item)"
          >
            <div class="portal-card-inner">
              <el-avatar :size="40" shape="square" style="background:#ebf1ff">
                <span class="text-lg font-semibold" style="color:#3370ff">AI</span>
              </el-avatar>
              <div class="portal-card-body">
                <div class="portal-card-top">
                  <div class="portal-card-info">
                    <span class="portal-card-name">{{ item.name }}</span>
                  </div>
                  <el-tag :type="item.is_publish ? 'success' : 'info'" size="small" effect="plain">
                    {{ item.is_publish ? '已发布' : '未发布' }}
                  </el-tag>
                </div>
                <div class="portal-card-desc">{{ item.desc || '暂无描述' }}</div>
                <div class="portal-card-meta">
                  <span class="portal-card-creator">{{ item.nick_name || '--' }}</span>
                  <span class="portal-card-workspace">{{ item.workspace_name }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-if="!loading && list.length === 0" description="暂无智能体" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import portalApi from '@/api/application/portal'

const router = useRouter()
const loading = ref(false)
const list = ref<any[]>([])

function goToChat(item: any) {
  router.push({
    name: 'portal-chat',
    params: { workspaceId: item.workspace_id, agentId: item.id },
  })
}

function loadData() {
  loading.value = true
  portalApi
    .getPortalApplicationList()
    .then((res) => {
      list.value = res.data || []
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.portal-page { height: 100%; }
.portal-sidebar { width: 200px; height: 100%; }
.portal-all-btn { border-radius: 8px; }
.portal-history {
  .el-empty { padding: 20px 0; }
}
.page-header h3 { font-size: 18px; font-weight: 600; margin: 0; color: var(--mk-N900); }
.portal-card {
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
  &:hover {
    border-color: var(--mk-primary) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
}
.portal-card-inner { display: flex; gap: 12px; align-items: flex-start; }
.portal-card-body { flex: 1; min-width: 0; }
.portal-card-top { display: flex; align-items: center; gap: 8px; }
.portal-card-info { flex: 1; min-width: 0; }
.portal-card-name {
  font-weight: 600; font-size: 14px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%;
  display: block;
}
.portal-card-desc {
  font-size: 13px; color: var(--mk-N600); margin-top: 4px;
  line-height: 1.4;
  display: -webkit-box; -webkit-box-orient: vertical;
  -webkit-line-clamp: 1; overflow: hidden;
}
.portal-card-meta {
  display: flex; align-items: center; gap: 8px; margin-top: 4px;
}
.portal-card-creator {
  font-size: 12px; color: var(--mk-N500); white-space: nowrap;
}
.portal-card-workspace {
  font-size: 11px;
  background: #f0f5ff;
  color: #3370ff;
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
}
</style>
