<template>
  <el-dialog
    :title="$t('views.knowledge.syncWeb.title')"
    v-model="dialogVisible"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
  >
    <p class="mb-8">{{ $t('views.knowledge.syncWeb.syncMethod') }}</p>
    <el-radio-group v-model="method" class="card__radio">
      <el-card shadow="never" class="mb-16" :class="method === 'replace' ? 'border-active' : ''">
        <el-radio value="replace" size="large">
          <p class="mb-4">{{ $t('views.knowledge.syncWeb.replace') }}</p>
          <el-text type="info">{{ $t('views.knowledge.syncWeb.replaceText') }}</el-text>
        </el-radio>
      </el-card>

      <el-card shadow="never" class="mb-16" :class="method === 'complete' ? 'border-active' : ''">
        <el-radio value="complete" size="large">
          <p class="mb-4">{{ $t('views.knowledge.syncWeb.complete') }}</p>
          <el-text type="info">{{ $t('views.knowledge.syncWeb.completeText') }}</el-text>
        </el-radio>
      </el-card>
    </el-radio-group>
    <p class="color-danger">{{ $t('views.knowledge.syncWeb.tip') }}</p>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { MsgSuccess } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { t } from '@/locales'

const route = useRoute()
const {
  query: { from },
} = route
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management') || from === 'systemManage') {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const emit = defineEmits(['refresh'])
const loading = ref<boolean>(false)
const method = ref('replace')
const knowledgeId = ref('')

const dialogVisible = ref<boolean>(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    method.value = 'replace'
  }
})

const open = (id: string) => {
  knowledgeId.value = id
  dialogVisible.value = true
}

const submit = () => {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .putSyncWebKnowledge(knowledgeId.value, method.value, loading)
    .then((res: any) => {
      emit('refresh', res.data)
      MsgSuccess(t('views.knowledge.tip.syncSuccess'))
      dialogVisible.value = false
    })
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.select-provider {
  font-size: 16px;
  color: rgba(100, 106, 115, 1);
  font-weight: 400;
  line-height: 24px;
  cursor: pointer;
  &:hover {
    color: var(--el-color-primary);
  }
}
.active-breadcrumb {
  font-size: 16px;
  color: var(--el-text-color-primary);
  font-weight: 500;
  line-height: 24px;
}
</style>
