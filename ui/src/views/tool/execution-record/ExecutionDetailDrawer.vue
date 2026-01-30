<template>
  <el-drawer
    v-model="visible"
    size="800px"
    :modal="false"
    destroy-on-close
    :before-close="closeHandle"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="visible = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>{{ $t('chat.executionDetails.title') }}</h4>
      </div>
    </template>
    <div>
      <el-scrollbar>
        <h4 class="title-decoration-1 mb-16 mt-4">
          {{ $t('common.ExecutionRecord.title') }}
        </h4>
        <el-card class="mb-24" shadow="never" style="--el-card-padding: 12px 16px">
          <el-row :gutter="16" class="lighter">
            <el-col :span="6">
              <p class="color-secondary mb-4">{{ $t('views.trigger.triggerSource') }}</p>
              <p class="flex align-center">
                <el-avatar shape="square" :size="22" style="background: none" class="mr-8">
                  <img
                    v-if="props.currentContent?.source_type === 'TOOL'"
                    :src="resetUrl(props.currentContent?.source_icon, resetUrl('./favicon.ico'))"
                    alt=""
                  />
                  <img
                    v-if="props.currentContent?.source_type === 'APPLICATION'"
                    :src="resetUrl(props.currentContent?.source_icon, resetUrl('./favicon.ico'))"
                    alt=""
                  />
                </el-avatar>

                <span class="ellipsis-1" :title="props.currentContent?.source_name">{{
                  props.currentContent?.source_name || '-'
                }}</span>
              </p>
            </el-col>
            <el-col :span="6">
              <p class="color-secondary mb-4">{{ $t('common.status.label') }}</p>
              <p>
                <el-text
                  class="color-text-primary"
                  v-if="props.currentContent?.state === 'SUCCESS'"
                >
                  <el-icon class="color-success"><SuccessFilled /></el-icon>
                  {{ $t('common.status.success') }}
                </el-text>
                <el-text
                  class="color-text-primary"
                  v-else-if="props.currentContent?.state === 'FAILURE'"
                >
                  <el-icon class="color-danger"><CircleCloseFilled /></el-icon>
                  {{ $t('common.status.fail') }}
                </el-text>
                <el-text
                  class="color-text-primary"
                  v-else-if="props.currentContent?.state === 'REVOKED'"
                >
                  <el-icon class="color-danger"><CircleCloseFilled /></el-icon>
                  {{ $t('common.status.REVOKED') }}
                </el-text>
                <el-text
                  class="color-text-primary"
                  v-else-if="props.currentContent?.state === 'REVOKE'"
                >
                  <el-icon class="is-loading color-primary"><Loading /></el-icon>
                  {{ $t('common.status.REVOKE') }}
                </el-text>
                <el-text class="color-text-primary" v-else>
                  <el-icon class="is-loading color-primary"><Loading /></el-icon>
                  {{ $t('common.status.STARTED') }}
                </el-text>
              </p>
            </el-col>
            <el-col :span="6">
              <p class="color-secondary mb-4">{{ $t('chat.KnowledgeSource.consumeTime') }}</p>
              <p>
                {{
                  props.currentContent?.run_time != undefined
                    ? props.currentContent?.run_time?.toFixed(2) + 's'
                    : '-'
                }}
              </p>
            </el-col>
            <el-col :span="6">
              <p class="color-secondary mb-4">{{ $t('chat.executionDetails.createTime') }}</p>
              <p>{{ datetimeFormat(props.currentContent?.create_time) }}</p>
            </el-col>
          </el-row>
        </el-card>
        <h4 class="title-decoration-1 mb-16 mt-4">
          {{ $t('chat.executionDetails.title') }}
        </h4>
        <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
          <div class="flex-between cursor" @click="showDetail = !showDetail">
            <div class="flex align-center">
              <el-icon class="mr-8 arrow-icon" :class="showDetail ? 'rotate-90' : ''">
                <CaretRight />
              </el-icon>
              <el-avatar
                v-if="detail?.tool_icon"
                shape="square"
                :size="24"
                style="background: none"
                class="mr-8"
              >
                <img :src="resetUrl(detail?.tool_icon)" alt="" />
              </el-avatar>
              <ToolIcon v-else :size="24" :type="detail?.tool_type" />
              <h4>{{ detail?.tool_name }}</h4>
            </div>
            <div class="flex align-center">
              <span class="mr-16 color-secondary" v-if="detail?.state !== 'STARTED'"
                >{{ detail?.run_time?.toFixed(2) || 0.0 }} s</span
              >
              <el-icon class="color-success" :size="16" v-if="detail?.state === 'SUCCESS'">
                <CircleCheck />
              </el-icon>
              <el-icon class="is-loading" :size="16" v-else-if="detail?.state === 'STARTED'">
                <Loading />
              </el-icon>
              <el-icon class="color-danger" :size="16" v-else>
                <CircleClose />
              </el-icon>
            </div>
          </div>
          <el-collapse-transition>
            <div class="mt-12" v-if="showDetail">
              <!-- 工具库 -->
              <div class="card-never border-r-6 mt-8">
                <h5 class="p-8-12">{{ $t('chat.executionDetails.input') }}</h5>
                <div class="p-8-12 border-t-dashed lighter break-all">
                  {{ detail?.meta.input || '-' }}
                </div>
              </div>
              <div class="card-never border-r-6 mt-8">
                <h5 class="p-8-12">{{ $t('chat.executionDetails.output') }}</h5>
                <div class="p-8-12 border-t-dashed lighter break-all">
                  {{ detail?.meta.output || '-' }}
                </div>
              </div>
            </div>
          </el-collapse-transition>
        </el-card>
      </el-scrollbar>
    </div>
    <template #footer>
      <div>
        <el-button @click="pre" :disabled="pre_disable || loading">{{
          $t('common.pages.prev')
        }}</el-button>
        <el-button @click="next" :disabled="next_disable || loading">{{
          $t('common.pages.next')
        }}</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { isAppIcon, resetUrl } from '@/utils/common'
import { datetimeFormat } from '@/utils/time'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
const props = withDefaults(
  defineProps<{
    /**
     * 当前的action_id
     */
    currentId: string
    currentContent: any
    /**
     * 下一条
     */
    next: () => void
    /**
     * 上一条
     */
    pre: () => void

    pre_disable: boolean

    next_disable: boolean
  }>(),
  {},
)

const emit = defineEmits(['update:currentId', 'update:currentContent'])

const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const detail = ref<any>(null)
const showDetail = ref<boolean>(true)

const loading = ref(false)
const visible = ref(false)

function closeHandle() {}

watch(
  () => props.currentId,
  () => {
    if (props.currentId) {
      getDetail()
    }
  },
)

watch(visible, (bool) => {
  if (!bool) {
    emit('update:currentId', '')
    emit('update:currentContent', null)
  }
})

function getDetail() {
  if (!props.currentContent) {
    return
  }
  loadSharedApi({ type: 'tool', systemType: apiType.value })
    .getToolRecordDetail(props.currentContent?.tool_id, props.currentContent?.id, loading)
    .then((ok: any) => {
      detail.value = ok.data
    })
}

const open = (row: any) => {
  visible.value = true
}

defineExpose({
  open,
})
</script>
<style lang="scss"></style>
