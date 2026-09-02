<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, reactive, ref } from 'vue'
import { CaretBottom } from '@element-plus/icons-vue'
import Knowledge from '../../items/knowledge/Knowledge.vue'
import type { FormField } from '../../type'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { FOLDER_ENTRY_ID } from '@/constants'

const props = defineProps<{ modelValue: DynamicFormValue }>()

const emit = defineEmits(['update:modelValue'])

const collapseData = reactive({ optional_knowledge: true })
const formValue = computed({
  set: (item: DynamicFormValue) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue || { knowledge_list: [], default_value: [] }
  },
})

const formField = computed<FormField>(() => {
  return { attrs: { knowledge_list: formValue.value.knowledge_list } } as DynamicFormValue
})

const getData = () => {
  const knowledgeItemList = (formValue.value.knowledge_list || []).map((k: DynamicFormValue) => {
    return { id: k.id, name: k.name, type: k.type, embedding_model_id: k.embedding_model_id }
  })

  return { input_type: 'Knowledge', default_value: formValue.value.default_value || [], attrs: { knowledge_list: knowledgeItemList } }
}

const render = (formData: DynamicFormValue) => {
  formValue.value.default_value = formData.default_value || []
  formValue.value.knowledge_list = formData.attrs?.knowledge_list || []
}

defineExpose({ getData, render })

// ── 添加知识库 ─────────────────────────────────────────
const knowledgeDialogVisible = ref(false)
const knowledgeLoading = ref(false)
const knowledgeSearch = ref('')
const knowledgeList = ref<KnowledgeItem[]>([])
const selectedKnowledgeIds = ref<Array<string>>([])

const filteredKnowledgeList = computed(() => {
  const keyword = knowledgeSearch.value.trim().toLocaleLowerCase()
  if (!keyword) return knowledgeList.value
  return knowledgeList.value.filter((item) => item.name.toLocaleLowerCase().includes(keyword))
})

const openAddKnowledgeDialog = async () => {
  knowledgeDialogVisible.value = true
  selectedKnowledgeIds.value = (formValue.value.knowledge_list || []).map((k: DynamicFormValue) => k.id)
  knowledgeLoading.value = true
  try {
    const res = await KnowledgeApi.getKnowledgePage({ currentPage: 1, pageSize: 100 }, { folder_id: FOLDER_ENTRY_ID.ALL })
    knowledgeList.value = res.records || []
  } finally {
    knowledgeLoading.value = false
  }
}

const handleKnowledgeSelect = () => {
  const selectIds = new Set(selectedKnowledgeIds.value)
  const currentList = (formValue.value.knowledge_list || []).filter((k: DynamicFormValue) => selectIds.has(k.id))
  knowledgeList.value.forEach((item) => {
    if (selectIds.has(item.id) && !currentList.some((k: DynamicFormValue) => k.id === item.id)) {
      currentList.push({ id: item.id, name: item.name, type: item.type, embedding_model_id: item.embedding_model_id })
    }
  })
  formValue.value.knowledge_list = currentList
  if (formValue.value.default_value) {
    formValue.value.default_value = formValue.value.default_value.filter((id: string) => selectIds.has(id))
  }
  knowledgeDialogVisible.value = false
}

function removeKnowledge(id: string) {
  formValue.value.knowledge_list = formValue.value.knowledge_list.filter((k: DynamicFormValue) => k.id !== id)
  if (formValue.value.default_value) {
    formValue.value.default_value = formValue.value.default_value.filter((k_id: string) => k_id !== id)
  }
}
</script>

<template>
  <el-form-item prop="knowledge_list" :rules="[{ message: '请选择可选知识库', type: 'array', min: 1 }]">
    <template #label>
      <div class="flex-between mb-2 cursor" @click="collapseData.optional_knowledge = !collapseData.optional_knowledge">
        <div class="flex align-center">
          <MkIcon
            :icon="CaretBottom"
            :size="14"
            class="mr-1 text-N600! transition-transform"
            :class="{ '-rotate-90': !collapseData.optional_knowledge }"
          />
          <span class="lighter"
            >可选知识库
            <span class="text-danger">*</span>
          </span>
          <span class="ml-1" v-if="formValue.knowledge_list?.length">({{ formValue.knowledge_list.length }})</span>
        </div>
        <el-button type="primary" link @click.stop="openAddKnowledgeDialog">
          <MkIcon name="icon_add_outlined" class="mr-1" />
          添加
        </el-button>
      </div>
    </template>
    <div class="w-full" v-if="collapseData.optional_knowledge">
      <div v-if="formValue.knowledge_list?.length > 0">
        <template v-for="(item, index) in formValue.knowledge_list" :key="index">
          <div class="flex-between border border-r-6 white-bg mb-8" style="padding: 3px 12px">
            <div class="flex align-center" style="width: 80%">
              <KnowledgeIcon :type="item.type" class="mr-8" :size="20" style="--el-avatar-border-radius: 6px" />

              <span class="ellipsis cursor" :title="item.name"> {{ item.name }}</span>
            </div>
            <el-button text @click="removeKnowledge(item.id)">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </template>
      </div>
      <el-text type="info" v-else> 请选择可选知识库 </el-text>
    </div>
  </el-form-item>
  <el-form-item
    label="默认知识库"
    prop="default_value"
    :required="formValue.required"
    :rules="formValue.required ? [{ message: '请选择知识库', type: 'array', min: 1 }] : []"
    v-if="formValue.knowledge_list && formValue.knowledge_list.length > 0"
  >
    <div class="w-full" v-if="formValue.knowledge_list?.length > 0">
      <Knowledge v-model="formValue.default_value" :form-field="formField" />
    </div>
  </el-form-item>

  <MkDialog v-model="knowledgeDialogVisible" title="添加知识库" width="600px" append-to-body>
    <el-input v-model="knowledgeSearch" placeholder="按名称搜索" clearable class="mb-3">
      <template #prefix>
        <MkIcon name="icon_magnify_outlined" />
      </template>
    </el-input>
    <div v-loading="knowledgeLoading" class="max-h-[360px] overflow-auto">
      <el-checkbox-group v-model="selectedKnowledgeIds">
        <el-checkbox :value="item.id" class="-mr-2 w-full mb-2 rounded-md border border-N300 p-2" v-for="item in filteredKnowledgeList" :key="item.id">
          <span class="flex items-center gap-2">
            <KnowledgeIcon :type="item.type" :size="20" style="--el-avatar-border-radius: 6px" />
            <span class="truncate">{{ item.name }}</span>
          </span>
        </el-checkbox>
      </el-checkbox-group>
      <el-empty v-if="!knowledgeLoading && filteredKnowledgeList.length === 0" description="暂无知识库" :image-size="60" />
    </div>
    <template #footer>
      <el-button @click="knowledgeDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleKnowledgeSelect">确定</el-button>
    </template>
  </MkDialog>
</template>
