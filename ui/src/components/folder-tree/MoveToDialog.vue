<template>
  <el-dialog
    title="转移到"
    v-model="visible"
    width="440"
    append-to-body
    :close-on-click-modal="false"
  >
    <el-form label-position="top" @submit.prevent>
      <el-form-item label="目标文件夹">
        <el-tree-select
          v-model="targetFolderId"
          :data="folderOptions"
          :props="{ label: 'name', children: 'children', value: 'id' }"
          placeholder="请选择目标文件夹"
          filterable
          clearable
          check-strictly
          default-expand-all
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false" :disabled="saving">取消</el-button>
      <el-button type="primary" @click="submit" :loading="saving">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import folderApi from '@/api/workspace/folder'
import { put } from '@/request/index'

const emit = defineEmits<{ (e: 'success', id: string): void }>()

const visible = ref(false)
const saving = ref(false)
const source = ref('')
const resourceId = ref('')
const targetFolderId = ref('')
const folderOptions = ref<any[]>([])

function getWsId(): string {
  return localStorage.getItem('workspace_id') || 'default'
}

function open(src: string, id: string, currentFolderId?: string) {
  source.value = src
  resourceId.value = id
  targetFolderId.value = ''
  visible.value = true
  // Load folder tree options
  folderApi.getFolder(src).then((res) => {
    folderOptions.value = res.data || []
  }).catch(() => {
    folderOptions.value = []
  })
}

async function submit() {
  if (!targetFolderId.value) {
    ElMessage.warning('请选择目标文件夹')
    return
  }
  saving.value = true
  try {
    const src = source.value.toLowerCase()
    const wsId = getWsId()
    if (src === 'application') {
      await put(`/workspace/${wsId}/application/${resourceId.value}/move/${targetFolderId.value}`)
    } else if (src === 'knowledge') {
      await put(`/workspace/${wsId}/knowledge/${resourceId.value}/move/${targetFolderId.value}`)
    } else if (src === 'tool') {
      await put(`/workspace/${wsId}/tool/${resourceId.value}/move/${targetFolderId.value}`)
    }
    ElMessage.success('转移成功')
    visible.value = false
    emit('success', resourceId.value)
  } catch (e: any) {
    ElMessage.error(e?.message || '转移失败')
  } finally {
    saving.value = false
  }
}

defineExpose({ open })
</script>
