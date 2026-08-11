<template>
  <el-dialog
    :title="isEdit ? '重命名文件夹' : '新建文件夹'"
    v-model="visible"
    width="480"
    append-to-body
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :rules="rules" :model="form" label-position="top" @submit.prevent>
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入文件夹名称"
          maxlength="64"
          show-word-limit
          @keyup.enter="submit"
        />
      </el-form-item>
      <el-form-item v-if="!isEdit" label="父文件夹" prop="parent_id">
        <el-tree-select
          v-model="form.parent_id"
          :data="folderOptions"
          :props="{ label: 'name', children: 'children', value: 'id' }"
          placeholder="请选择父文件夹"
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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import folderApi from '@/api/workspace/folder'

const emit = defineEmits<{ (e: 'refresh'): void }>()

const visible = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const editId = ref('')
const source = ref('')
const formRef = ref()
const form = reactive({ name: '', parent_id: '' })
const folderOptions = ref<any[]>([])

const rules = {
  name: [
    { required: true, message: '请输入文件夹名称', trigger: 'blur' },
    { max: 64, message: '名称不能超过64个字符', trigger: 'blur' },
  ],
}

function flattenTree(nodes: any[]): any[] {
  const result: any[] = []
  for (const node of nodes) {
    result.push(node)
    if (node.children && node.children.length > 0) {
      result.push(...flattenTree(node.children))
    }
  }
  return result
}

function open(src: string, pid: string, data?: any) {
  source.value = src
  isEdit.value = !!data
  if (data) {
    editId.value = data.id
    form.name = data.name
  } else {
    editId.value = ''
    form.name = ''
    form.parent_id = pid || ''
    // 加载文件夹树作为选项
    folderApi.getFolder(src).then((res) => {
      folderOptions.value = res.data || []
      // 如果 pid 存在且在树中找得到，默认选中
      if (pid) {
        const all = flattenTree(folderOptions.value)
        if (all.some(n => n.id === pid)) {
          form.parent_id = pid
        }
      }
    }).catch(() => {
      folderOptions.value = []
    })
  }
  visible.value = true
}

function handleClosed() {
  form.name = ''
  form.parent_id = ''
  editId.value = ''
  isEdit.value = false
  folderOptions.value = []
  formRef.value?.resetFields()
}

async function submit() {
  await formRef.value?.validate()
  if (!form.name.trim()) return
  saving.value = true
  try {
    if (isEdit.value) {
      await folderApi.putFolder(editId.value, source.value, { name: form.name.trim() })
      ElMessage.success('重命名成功')
    } else {
      await folderApi.postFolder(source.value, {
        name: form.name.trim(),
        parent_id: form.parent_id || undefined,
      })
      ElMessage.success('创建成功')
    }
    visible.value = false
    emit('refresh')
  } catch (e: any) {
    ElMessage.error(e?.message || (isEdit.value ? '重命名失败' : '创建失败'))
  } finally {
    saving.value = false
  }
}

defineExpose({ open })
</script>
