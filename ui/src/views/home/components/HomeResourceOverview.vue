<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type HomepageApi from '@/api/admin/workspace/homepage'
import type { HomeApplicationAggregation, HomeKnowledgeAggregation, HomeModelAggregation, HomeToolAggregation } from '@/api/types'
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

const { t } = useI18n({ useScope: 'global' })

/* 资源概况与列表导航 */
const props = defineProps<{ workspaceId: string; api: typeof HomepageApi }>()
const router = useRouter()
const route = useRoute()
const isSystemScope = computed(() => route.meta.scope === 'system')
const loading = ref(false)
const application = ref<HomeApplicationAggregation>()
const knowledge = ref<HomeKnowledgeAggregation>()
const tool = ref<HomeToolAggregation>()
const model = ref<HomeModelAggregation>()
const resourceGroups = computed<HomeResourceCard[]>(() => [
  {
    label: t('application.title'),
    disabled: isSystemScope.value || !perm.application.workspace.isShare(),
    route: 'workspace-application-list',
    icon: 'icon_robot_filled',
    color: '#3370FF',
    total: application.value?.total,
    details: [
      [t('application.status.published'), application.value?.publish_count],
      [t('application.status.unpublished'), application.value?.un_publish_count],
    ],
  },
  {
    label: t('knowledge.title'),
    disabled: isSystemScope.value || !perm.knowledge.workspace.isShare(),
    route: 'workspace-knowledge-list',
    icon: 'icon_book_filled',
    color: '#7F3BF5',
    total: knowledge.value?.total,
    details: [
      [t('knowledge.document.title'), knowledge.value?.document_count],
      [t('common.status.failure'), knowledge.value?.failure_count],
    ],
  },
  {
    label: t('tool.title'),
    disabled: isSystemScope.value || !perm.tool.workspace.isShare(),
    route: 'workspace-tools',
    icon: 'icon_busy_filled',
    color: '#2CA91F',
    total: tool.value?.total,
    details: [
      [t('tool.title'), tool.value?.custom_count],
      [t('workflow.title'), tool.value?.workflow_count],
      [t('common.labels.other'), tool.value ? Math.max(0, tool.value.total - tool.value.custom_count - tool.value.workflow_count) : undefined],
    ],
  },
  {
    label: t('model.title'),
    disabled: isSystemScope.value || !perm.model.workspace.isShare(),
    route: 'workspace-model',
    icon: 'icon_dataset_filled',
    color: '#FF8800',
    total: model.value?.total,
    details: [
      [t('overview.resources.llm'), model.value?.llm_count],
      [t('overview.resources.embedding'), model.value?.embedding_count],
      [t('common.labels.other'), model.value ? Math.max(0, model.value.total - model.value.llm_count - model.value.embedding_count) : undefined],
    ],
  },
])
function loadResources() {
  if (loading.value) return
  loading.value = true
  return Promise.allSettled([
    props.api
      .getApplicationAggregation(props.workspaceId)
      .then((value) => {
        application.value = value
      })
      .catch(() => {
        application.value = undefined
      }),
    props.api
      .getKnowledgeAggregation(props.workspaceId)
      .then((value) => {
        knowledge.value = value
      })
      .catch(() => {
        knowledge.value = undefined
      }),
    props.api
      .getToolAggregation(props.workspaceId)
      .then((value) => {
        tool.value = value
      })
      .catch(() => {
        tool.value = undefined
      }),
    props.api
      .getModelAggregation(props.workspaceId)
      .then((value) => {
        model.value = value
      })
      .catch(() => {
        model.value = undefined
      }),
  ]).finally(() => {
    loading.value = false
  })
}
function handleNavigate(card: HomeResourceCard) {
  if (loading.value || card.disabled) return
  router.push({ name: card.route, params: { workspaceId: props.workspaceId } })
}
onMounted(loadResources)
defineExpose({ refresh: loadResources })
</script>
<template>
  <section>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <template v-for="card in resourceGroups" :key="card.route">
        <!-- 进入未禁用资源的列表 -->
        <el-card
          :shadow="card.disabled ? 'never' : 'hover'"
          :class="{ 'cursor-pointer hover:border-current!': !card.disabled }"
          :style="{ color: card.color, backgroundImage: `linear-gradient(to bottom, ${card.color}0A 0%, #FFFFFF 40%, #FFFFFF 100%)` }"
          @click="handleNavigate(card)"
        >
          <el-skeleton :loading="loading" animated>
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
          </el-skeleton>
        </el-card>
      </template>
    </div>
  </section>
</template>
