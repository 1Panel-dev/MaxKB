<script setup lang="ts">
import { ref } from 'vue'
import type { ResourcePermission } from '@/api/types'

import type { ResourcePermissionOption } from './types'

const props = defineProps<{
  options: ResourcePermissionOption[]
  isFolder: boolean
  canIncludeChildren: boolean
  loading: boolean
}>()
const emit = defineEmits<{ submit: [permission: ResourcePermission, includeChildren: boolean] }>()

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
  <MkDialog v-model="visible" :title="scopeOnly ? '生效资源' : '配置权限'" :show-close="!loading" @closed="resetData">
    <el-radio-group v-if="!scopeOnly" v-model="permission" class="vertical-radio-group" :disabled="loading">
      <el-radio v-for="option in options" :key="option.value" :value="option.value">
        <p>{{ option.label }}</p>
        <p v-if="option.description" class="mt-1 text-N500">{{ option.description }}</p>
      </el-radio>
    </el-radio-group>
    <template v-if="isFolder">
      <template v-if="!scopeOnly">
        <el-divider class="my-4!" />
        <h6 class="mb-2">生效资源</h6>
      </template>
      <el-radio-group v-model="includeChildren" class="vertical-radio-group" :disabled="loading">
        <el-radio :value="false">仅当前资源</el-radio>
        <el-radio :value="true" :disabled="!canIncludeChildren">包含所有子文件夹</el-radio>
      </el-radio-group>
    </template>
    <template #footer>
      <el-button plain :disabled="loading" @click="close">取消</el-button>
      <el-button type="primary" :loading="loading" :disabled="!permission" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>
