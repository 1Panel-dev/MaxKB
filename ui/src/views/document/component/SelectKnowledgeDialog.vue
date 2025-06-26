<template>
  <el-dialog
    :title="`${$t('views.document.migrateDocument')}`"
    v-model="dialogVisible"
    width="600"
    class="select-knowledge-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form ref="FormRef" :model="form" label-position="top" require-asterisk-position="right">
      <el-form-item :label="$t('views.chatLog.selectKnowledge')" required>
        <el-tree-select
          v-model="form.selectKnowledge"
          :props="defaultProps"
          node-key="id"
          lazy
          :load="loadTree"
          :placeholder="$t('views.chatLog.selectKnowledgePlaceholder')"
          :loading="loading"
        >
          <template #default="{ data }">
            <div class="flex align-center">
              <KnowledgeIcon
                class="mr-12"
                :size="20"
                v-if="data.resource_type !== 'folder'"
                :type="data.type"
              />
              <el-avatar v-else class="mr-12" shape="square" :size="20" style="background: none">
                <img
                  src="@/assets/knowledge/icon_file-folder_colorful.svg"
                  style="width: 100%"
                  alt=""
                />
              </el-avatar>

              {{ data.name }}
            </div>
          </template>
        </el-tree-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button
          type="primary"
          @click="submitHandle"
          :disabled="!form.selectKnowledge || loading"
        >
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import useStore from "@/stores";
const route = useRoute()
const {
  params: { id }, // id为knowledgeID
} = route as any

const { user } = useStore()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const emit = defineEmits(['refresh'])

const loading = ref<boolean>(false)

const dialogVisible = ref<boolean>(false)
const knowledgeList = ref<any>([])
const documentList = ref<any>([])
const form = ref<any>({
  selectKnowledge: '',
})

const defaultProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: any) => data.resource_type && data.resource_type !== 'folder',
  disabled: (data: any, node: any) => {
    return data.id === id
  },
}

const loadTree = (node: any, resolve: any) => {
  console.log(node)
  if (node.isLeaf) return resolve([])
  const folder_id = node.level === 0 ? user.getWorkspaceId() : node.data.id
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getKnowledgeList({folder_id: folder_id}, loading)
    .then((res: any) => {
      resolve(res.data)
    })
}

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value.selectKnowledge = ''
    knowledgeList.value = []
    documentList.value = []
  }
})

const open = (list: any) => {
  documentList.value = list
  dialogVisible.value = true
}

const submitHandle = () => {
  loadSharedApi({ type: 'document', systemType: apiType.value })
    .putMigrateMulDocument(id, form.value.selectKnowledge, documentList.value, loading)
    .then(() => {
      emit('refresh')
      dialogVisible.value = false
    })
}

defineExpose({ open })
</script>
<style lang="scss"></style>
