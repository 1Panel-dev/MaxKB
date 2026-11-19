<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ResourcePermission } from '@/api/types'
import { getPermissionOptions } from '../constants'

defineOptions({ name: 'BatchSetPermissionDialog' })

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ submit: [permission: ResourcePermission] }>()
const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const permission = ref<ResourcePermission>()

function open() {
  if (props.disabled) return

  visible.value = true
}

function close() {
  visible.value = false
}

function resetData() {
  permission.value = undefined
}

function handleSubmit() {
  if (props.disabled || !permission.value) return

  emit('submit', permission.value)
  visible.value = false
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="t('authorization.permission.configure')" @closed="resetData">
    <el-radio-group v-model="permission" class="mk-radio-group-vertical" :disabled="disabled">
      <el-radio v-for="permissionOption in getPermissionOptions()" :key="permissionOption.value" :value="permissionOption.value">
        <p>{{ t(permissionOption.labelKey) }}</p>
        <p v-if="permissionOption.descriptionKey" class="text-N500 mt-1">
          {{ t(permissionOption.descriptionKey) }}
        </p>
      </el-radio>
    </el-radio-group>
    <template #footer>
      <!-- 取消批量配置 -->
      <el-button plain @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确认批量配置 -->
      <el-button type="primary" :disabled="disabled || !permission" @click="handleSubmit">{{ t('common.actions.confirm') }}</el-button>
    </template>
  </MkDialog>
</template>

<style scoped lang="scss"></style>
