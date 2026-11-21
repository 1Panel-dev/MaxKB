<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationAccessToken } from '@/api/types'
import AccessRestrictionDrawer from './AccessRestrictionDrawer.vue'

defineProps<{ accessTokenConfig?: ApplicationAccessToken }>()

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'ButtonAccessRestriction' })

const drawerVisible = ref(false)

const emit = defineEmits<{ updated: [config: ApplicationAccessToken] }>()

function handleOpenAccessRestriction() {
  drawerVisible.value = true
}
</script>

<template>
  <!-- 设置访问限制 -->
  <el-button plain @click="handleOpenAccessRestriction">
    <MkIcon name="icon-lock" />
    <span>{{ t('application.overview.accessRestriction.title') }}</span>
  </el-button>
  <AccessRestrictionDrawer
    v-if="drawerVisible"
    :initial-config="accessTokenConfig"
    @closed="drawerVisible = false"
    @updated="(config) => emit('updated', config)"
  />
</template>
