<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type HomepageApi from '@/api/admin/workspace/homepage'
import type { HomeApplicationAggregation, HomeKnowledgeAggregation, HomeToolAggregation, HomeModelAggregation } from '@/api/types'
import { toThousands } from '@/utils/number'
import perm from '@/permission'
interface HomeResourceCard {
  label: string
  route: string
  icon: string
  color: string
  disabled?: boolean
  total?: number
  details: [string, number | undefined][]
}

const ZERO_APPLICATION: HomeApplicationAggregation = { total: 0, publish_count: 0, un_publish_count: 0 }
const ZERO_KNOWLEDGE: HomeKnowledgeAggregation = { total: 0, document_count: 0, failure_count: 0 }
const ZERO_TOOL: HomeToolAggregation = {
  total: 0,
  custom_count: 0,
  workflow_count: 0,
  skill_count: 0,
  mcp_count: 0,
  data_source_count: 0,
}
const ZERO_MODEL: HomeModelAggregation = { total: 0, llm_count: 0, embedding_count: 0 }

/* 资源概况与列表导航 */
const props = defineProps<{ workspaceId: string; api: typeof HomepageApi }>()
const router = useRouter()
const route = useRoute()
const isSystemScope = computed(() => route.meta.scope === 'system')
const canReadApplication = computed(() => !isSystemScope.value || perm.application.system.read())
const canReadKnowledge = computed(() => !isSystemScope.value || perm.knowledge.system.read())
const canReadTool = computed(() => !isSystemScope.value || perm.tool.system.read())
const canReadModel = computed(() => !isSystemScope.value || perm.model.system.read())
const loading = ref(false)
const application = ref<HomeApplicationAggregation>()
const knowledge = ref<HomeKnowledgeAggregation>()
const tool = ref<HomeToolAggregation>()
const model = ref<HomeModelAggregation>()
const resourceGroups = computed<HomeResourceCard[]>(() => [
  {
    label: '智能体',
    disabled: isSystemScope.value || !perm.application.workspace.isShare(),
    route: 'workspace-application-list',
    icon: 'icon_robot_filled',
    color: '#3370FF',
    total: application.value?.total,
    details: [
      ['已发布', application.value?.publish_count],
      ['未发布', application.value?.un_publish_count],
    ],
  },
  {
    label: '知识库',
    disabled: isSystemScope.value || !perm.knowledge.workspace.isShare(),
    route: 'workspace-knowledge-list',
    icon: 'icon_book_filled',
    color: '#7F3BF5',
    total: knowledge.value?.total,
    details: [
      ['文档', knowledge.value?.document_count],
      ['失败', knowledge.value?.failure_count],
    ],
  },
  {
    label: '工具',
    disabled: isSystemScope.value || !perm.tool.workspace.isShare(),
    route: 'workspace-tools',
    icon: 'icon_busy_filled',
    color: '#2CA91F',
    total: tool.value?.total,
    details: [
      ['工具', tool.value?.custom_count],
      ['工作流', tool.value?.workflow_count],
      ['其他', tool.value ? Math.max(0, tool.value.total - tool.value.custom_count - tool.value.workflow_count) : undefined],
    ],
  },
  {
    label: '模型',
    disabled: isSystemScope.value || !perm.model.workspace.isShare(),
    route: 'workspace-model',
    icon: 'icon_dataset_filled',
    color: '#FF8800',
    total: model.value?.total,
    details: [
      ['大语言', model.value?.llm_count],
      ['向量', model.value?.embedding_count],
      ['其他', model.value ? Math.max(0, model.value.total - model.value.llm_count - model.value.embedding_count) : undefined],
    ],
  },
])
function loadResources() {
  if (loading.value) return
  loading.value = true
  return Promise.allSettled([
    canReadApplication.value
      ? props.api
          .getApplicationAggregation(props.workspaceId)
          .then((value) => {
            application.value = value
          })
          .catch(() => {
            application.value = undefined
          })
      : Promise.resolve().then(() => {
          application.value = { ...ZERO_APPLICATION }
        }),
    canReadKnowledge.value
      ? props.api
          .getKnowledgeAggregation(props.workspaceId)
          .then((value) => {
            knowledge.value = value
          })
          .catch(() => {
            knowledge.value = undefined
          })
      : Promise.resolve().then(() => {
          knowledge.value = { ...ZERO_KNOWLEDGE }
        }),
    canReadTool.value
      ? props.api
          .getToolAggregation(props.workspaceId)
          .then((value) => {
            tool.value = value
          })
          .catch(() => {
            tool.value = undefined
          })
      : Promise.resolve().then(() => {
          tool.value = { ...ZERO_TOOL }
        }),
    canReadModel.value
      ? props.api
          .getModelAggregation(props.workspaceId)
          .then((value) => {
            model.value = value
          })
          .catch(() => {
            model.value = undefined
          })
      : Promise.resolve().then(() => {
          model.value = { ...ZERO_MODEL }
        }),
  ]).finally(() => {
    loading.value = false
  })
}
function handleNavigate(card: HomeResourceCard) {
  if (card.disabled) return
  router.push({ name: card.route, params: { workspaceId: props.workspaceId } })
}
onMounted(loadResources)
defineExpose({ refresh: loadResources })
</script>
<template>
  <section>
    <div v-loading="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <template v-for="card in resourceGroups" :key="card.route">
        <!-- 进入未禁用资源的列表 -->
        <el-card
          :shadow="card.disabled ? 'never' : 'hover'"
          :class="{ 'cursor-pointer hover:border-current!': !card.disabled }"
          :style="{ color: card.color, backgroundImage: `linear-gradient(to bottom, ${card.color}0A 0%, #FFFFFF 40%, #FFFFFF 100%)` }"
          @click="handleNavigate(card)"
        >
          <div class="flex-between text-N900">
            <div>
              <p class="text-N600 mb-1">{{ card.label }}</p>
              <p class="text-3xl leading-9.5 font-semibold tabular-nums">{{ toThousands(card.total) }}</p>
            </div>

            <el-avatar
              shape="square"
              :size="44"
              :style="{ color: card.color, backgroundColor: `${card.color}14`, '--el-avatar-border-radius': '12px' }"
            >
              <MkIcon :name="card.icon" :size="26" />
            </el-avatar>
          </div>

          <div class="flex mt-4 gap-4">
            <template v-for="[label, value] in card.details" :key="String(label)">
              <div class="min-w-0 flex-1">
                <p class="text-N600">{{ label }}</p>
                <h2 class="mt-1 text-N900">{{ toThousands(value) }}</h2>
              </div>
            </template>
          </div>
        </el-card>
      </template>
    </div>
  </section>
</template>
