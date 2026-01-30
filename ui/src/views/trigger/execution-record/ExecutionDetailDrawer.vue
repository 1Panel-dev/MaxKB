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
              <p class="color-secondary mb-4">{{ $t('views.trigger.triggerTask') }}</p>
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
        <template v-if="taskRecordDetails && taskRecordDetails.state === 'TRIGGER_ERROR'">
          <div class="card-never border-r-6 mb-12">
            <h5 class="p-8-12">触发器入参</h5>
            <div class="p-8-12 border-t-dashed lighter">
              {{ taskRecordDetails.meta.input }}
            </div>
          </div>
          <div class="card-never border-r-6 mb-12">
            <h5 class="p-8-12">错误信息</h5>
            <div class="p-8-12 border-t-dashed lighter">
              {{ taskRecordDetails.meta.err_message }}
            </div>
          </div>
        </template>
        <template v-else v-for="(item, index) in arraySort(detail ?? [], 'index')" :key="index">
          <ExecutionDetailCard :data="item"> </ExecutionDetailCard>
        </template>
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
import { arraySort } from '@/utils/array'
import { isAppIcon, resetUrl } from '@/utils/common'
import ExecutionDetailCard from '@/components/execution-detail-card/index.vue'
import { datetimeFormat } from '@/utils/time'
import triggerAPI from '@/api/trigger/trigger'
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
const taskRecordDetails = ref<any>()
const detail = ref<any>(null)

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
  triggerAPI
    .getTriggerTaskRecordDetails(
      props.currentContent?.trigger_id,
      props.currentContent?.trigger_task_id,
      props.currentContent?.id,
    )
    .then((ok) => {
      if (ok.data.details) {
        detail.value = Object.values(ok.data.details)
      }
      taskRecordDetails.value = ok.data
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
