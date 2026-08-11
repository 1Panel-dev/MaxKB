<template>
  <div class="detail-page">
    <div class="detail-page-inner">
      <!-- 顶部导航 -->
      <div class="page-header flex items-center gap-3 mb-6">
        <el-button text @click="goBack">
          <MkIcon name="icon_left_outlined" :size="16" />
        </el-button>
        <el-divider direction="vertical" />
        <h3 class="m-0">工具概览</h3>
      </div>

      <el-skeleton :loading="loading" animated>
        <template #default>
          <!-- 基本信息 -->
          <section class="mb-6">
            <el-card shadow="never" class="detail-card" :body-style="{ padding: 0 }">
              <div class="detail-card-section">
                <h4 class="detail-card-title">基本信息</h4>
                <div class="info-panel">
                  <div class="info-main">
                    <div class="info-avatar">
                      <el-avatar :size="56" shape="square" style="background: #ebf9e9">
                        <span class="text-xl font-bold" style="color: #2ca91f">{{ typeIcon }}</span>
                      </el-avatar>
                    </div>
                    <div class="info-detail">
                      <div class="info-name-row">
                        <h2 class="info-name">{{ detail?.name || '-' }}</h2>
                        <el-tag size="small" effect="plain">{{ typeLabel }}</el-tag>
                        <el-tag
                          :type="detail?.is_active ? 'success' : 'info'"
                          size="small"
                          effect="plain"
                        >
                          {{ detail?.is_active ? '已启用' : '未启用' }}
                        </el-tag>
                      </div>
                      <p class="info-desc">{{ detail?.desc || '暂无描述' }}</p>
                      <div class="info-meta">
                        <span>{{ detail?.nick_name || '--' }}</span>
                        <el-divider direction="vertical" />
                        <span>创建于 {{ detail?.create_time ? formatDate(detail.create_time) : '--' }}</span>
                        <el-divider direction="vertical" />
                        <span>更新于 {{ detail?.update_time ? formatDate(detail.update_time) : '--' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </section>

          <!-- 参数信息 -->
          <section class="mb-6">
            <el-card shadow="never" class="detail-card" :body-style="{ padding: 0 }">
              <div class="detail-card-section">
                <h4 class="detail-card-title">参数信息</h4>
                <el-row :gutter="24">
                  <el-col :span="12">
                    <div class="param-section">
                      <h5 class="param-section-title">初始化参数</h5>
                      <template v-if="detail?.init_field_list?.length">
                        <div
                          v-for="field in detail.init_field_list"
                          :key="field.field"
                          class="param-item"
                        >
                          <span class="param-name">{{ field.name || field.field }}</span>
                          <span class="param-type">{{ field.type || '--' }}</span>
                        </div>
                      </template>
                      <span v-else class="param-empty">无初始化参数</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="param-section">
                      <h5 class="param-section-title">输入参数</h5>
                      <template v-if="detail?.input_field_list?.length">
                        <div
                          v-for="field in detail.input_field_list"
                          :key="field.field"
                          class="param-item"
                        >
                          <span class="param-name">{{ field.name || field.field }}</span>
                          <span class="param-type">{{ field.type || '--' }}</span>
                          <el-tag v-if="field.required" size="small" type="danger" effect="plain">必填</el-tag>
                        </div>
                      </template>
                      <span v-else class="param-empty">无输入参数</span>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </section>

          <!-- 使用统计 -->
          <section>
            <el-card shadow="never" class="detail-card" :body-style="{ padding: 0 }">
              <div class="detail-card-section">
                <h4 class="detail-card-title">使用统计</h4>
                <el-row :gutter="16">
                  <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" class="mb-4">
                    <el-card shadow="never" class="stat-mini-card" :body-style="{ padding: '16px' }">
                      <div class="flex flex-col gap-1.5">
                        <span class="stat-mini-label">调用次数</span>
                        <span class="stat-mini-value">{{ detail?.call_count || 0 }}</span>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" class="mb-4">
                    <el-card shadow="never" class="stat-mini-card" :body-style="{ padding: '16px' }">
                      <div class="flex flex-col gap-1.5">
                        <span class="stat-mini-label">关联智能体</span>
                        <span class="stat-mini-value">{{ detail?.application_count || 0 }}</span>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" class="mb-4">
                    <el-card shadow="never" class="stat-mini-card" :body-style="{ padding: '16px' }">
                      <div class="flex flex-col gap-1.5">
                        <span class="stat-mini-label">版本</span>
                        <span class="stat-mini-value">{{ detail?.version || '--' }}</span>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" class="mb-4">
                    <el-card shadow="never" class="stat-mini-card" :body-style="{ padding: '16px' }">
                      <div class="flex flex-col gap-1.5">
                        <span class="stat-mini-label">状态</span>
                        <span class="stat-mini-value">{{ detail?.is_active ? '启用' : '停用' }}</span>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </section>
        </template>
      </el-skeleton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import toolApi from '@/api/tool/tool'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const detail = ref<any>(null)

const typeLabels: Record<string, string> = {
  CUSTOM: '工具',
  WORKFLOW: '工作流',
  SKILL: 'Skills',
  MCP: 'MCP',
  DATA_SOURCE: '数据源',
}

const typeIcons: Record<string, string> = {
  CUSTOM: 'T',
  WORKFLOW: 'W',
  SKILL: 'S',
  MCP: 'M',
  DATA_SOURCE: 'D',
}

const typeLabel = computed(() => {
  const t = detail.value?.tool_type
  return t ? typeLabels[t] || t : '--'
})

const typeIcon = computed(() => {
  const t = detail.value?.tool_type
  return t ? typeIcons[t] || 'T' : 'T'
})

function goBack() {
  router.push({ name: 'workspace-tool-list' })
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadData() {
  const toolId = route.params.toolId as string
  if (!toolId) return
  loading.value = true
  try {
    const res = await toolApi.getToolById(toolId)
    detail.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.detail-page {
  padding: 24px;
  max-width: 1280px;
  margin: 0 auto;
}

.page-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--mk-N900);
}

.detail-card {
  border-radius: 12px;
  border: 1px solid var(--mk-N300);
}

.detail-card-section {
  padding: 24px;
}

.detail-card-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--mk-N900);
  padding-left: 12px;
  border-left: 3px solid var(--mk-primary);
}

/* ---- 基本信息 ---- */
.info-panel {
  padding: 8px 0 0;
}

.info-main {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.info-avatar {
  flex-shrink: 0;
}

.info-detail {
  flex: 1;
  min-width: 0;
}

.info-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.info-name {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--mk-N900);
  line-height: 1.3;
}

.info-desc {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: var(--mk-N600);
  line-height: 1.4;
}

.info-meta {
  display: flex;
  align-items: center;
  gap: 0;
  font-size: 12px;
  color: var(--mk-N600);
}

/* ---- 参数信息 ---- */
.param-section {
  padding: 4px 0;
}

.param-section-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: var(--mk-N900);
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--mk-N300);

  &:last-child {
    border-bottom: none;
  }
}

.param-name {
  font-size: 13px;
  color: var(--mk-N900);
  font-weight: 500;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.param-type {
  font-size: 12px;
  color: var(--mk-N600);
}

.param-empty {
  font-size: 12px;
  color: var(--mk-N600);
}

/* ---- 迷你统计卡片 ---- */
.stat-mini-card {
  border-radius: 10px;
  border: 1px solid var(--mk-N300);
  transition: all 0.2s;

  &:hover {
    border-color: var(--mk-primary) !important;
    box-shadow: 0 2px 8px rgba(51, 112, 255, 0.08);
  }
}

.stat-mini-label {
  font-size: 12px;
  color: var(--mk-N600);
}

.stat-mini-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--mk-N900);
  line-height: 1.1;
}
</style>
