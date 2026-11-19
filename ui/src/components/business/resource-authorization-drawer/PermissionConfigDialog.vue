<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ResourcePermissionOption } from './types'
import type { ResourcePermission } from '@/api/types'

const props = defineProps<{
  options: ResourcePermissionOption[]
  isFolder: boolean
  canIncludeChildren: boolean
  loading: boolean
}>()
const emit = defineEmits<{ submit: [permission: ResourcePermission, includeChildren: boolean] }>()
const { t } = useI18n({ useScope: 'global' })

/* 权限和生效范围 */
const visible = ref(false)
const permission = ref<ResourcePermission>()
const includeChildren = ref(false)
const scopeOnly = ref(false)

function open(currentPermission?: ResourcePermission) {
  permission.value = currentPermission
  scopeOnly.value = Boolean(currentPermission)
  visible.value = true
}

function handleSubmit() {
  if (!permission.value || props.loading) return
  emit('submit', permission.value, props.isFolder && includeChildren.value)
}

function close() {
  visible.value = false
}

function resetData() {
  permission.value = undefined
  includeChildren.value = false
  scopeOnly.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog
    v-model="visible"
    :title="scopeOnly ? t('authorization.resource.scope.label') : t('authorization.permission.configure')"
    @closed="resetData"
  >
    <el-radio-group v-if="!scopeOnly" v-model="permission" class="mk-radio-group-vertical" :disabled="loading">
      <el-radio v-for="option in options" :key="option.value" :value="option.value">
        <p>{{ option.label }}</p>
        <p v-if="option.description" class="mt-1 text-N500">{{ option.description }}</p>
      </el-radio>
    </el-radio-group>
    <div v-if="isFolder">
      <div v-if="!scopeOnly">
        <el-divider class="my-4!" />
        <h6 class="mb-2">{{ t('authorization.resource.scope.label') }}</h6>
      </div>
      <el-radio-group v-model="includeChildren" class="mk-radio-group-vertical" :disabled="loading">
        <el-radio :value="false">{{ t('authorization.resource.scope.current') }}</el-radio>
        <el-radio :value="true" :disabled="!canIncludeChildren">{{ t('authorization.resource.scope.includeChildren') }}</el-radio>
      </el-radio-group>
    </div>
    <template #footer>
      <!-- 取消权限配置 -->
      <el-button plain :disabled="loading" @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确认权限配置 -->
      <el-button type="primary" :loading="loading" :disabled="!permission" @click="handleSubmit">{{ t('common.actions.confirm') }}</el-button>
    </template>
  </MkDialog>
</template>
