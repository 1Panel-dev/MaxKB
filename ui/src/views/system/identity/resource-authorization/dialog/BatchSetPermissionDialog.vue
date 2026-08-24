<script setup lang="ts">
import { ref } from 'vue'
import type { ResourcePermission } from '@/api/types'
import { getPermissionOptions } from '../constants'

defineOptions({ name: 'BatchSetPermissionDialog' })

const emit = defineEmits<{
  submit: [permission: ResourcePermission]
}>()

const visible = ref(false)
const permission = ref<ResourcePermission>()

function open() {
  visible.value = true
}

function resetData() {
  permission.value = undefined
}

function handleSubmit() {
  if (!permission.value) return

  emit('submit', permission.value)
  visible.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="配置权限" @closed="resetData">
    <el-radio-group v-model="permission" class="vertical-radio-group">
      <el-radio
        v-for="permissionOption in getPermissionOptions()"
        :key="permissionOption.value"
        :value="permissionOption.value"
      >
        <p>{{ permissionOption.label }}</p>
        <p v-if="permissionOption.description" class="text-N500 mt-1">
          {{ permissionOption.description }}
        </p>
      </el-radio>
    </el-radio-group>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!permission" @click="handleSubmit">确认</el-button>
    </template>
  </MkDialog>
</template>

<style scoped lang="scss"></style>
