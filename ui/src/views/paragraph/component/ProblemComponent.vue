<template>
  <p class="bold title p-24" style="padding-bottom: 0">
    <span class="flex align-center">
      <span>{{ $t('views.paragraph.relatedProblem.title') }}</span>
      <el-divider direction="vertical" class="mr-4" />
      <el-button text @click="addProblem"
        v-if="permissionPrecise.problem_relate(id)"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </span>
  </p>
  <div v-loading="loading">
    <el-scrollbar height="500px">
      <div class="p-24" style="padding-top: 16px">
        <el-select
          v-if="isAddProblem"
          v-model="problemValue"
          filterable
          allow-create
          default-first-option
          :reserve-keyword="false"
          :placeholder="$t('views.paragraph.relatedProblem.placeholder')"
          remote
          :remote-method="remoteMethod"
          :loading="optionLoading"
          @change="addProblemHandle"
          @blur="isAddProblem = false"
          class="mb-16"
          popper-class="select-popper"
          :popper-append-to-body="false"
        >
          <el-option
            v-for="item in problemOptions"
            :key="item.id"
            :label="item.content"
            :value="item.id"
          >
            {{ item.content }}
          </el-option>
        </el-select>
        <template v-for="(item, index) in problemList" :key="index">
          <TagEllipsis
            @close="delProblemHandle(item, index)"
            class="question-tag"
            type="info"
            effect="plain"
            v-bind="permissionPrecise.problem_relate(id) ? {closable:true} : {} "
          >
            <auto-tooltip :content="item.content">
              {{ item.content }}
            </auto-tooltip>
          </TagEllipsis>
        </template>
      </div>
    </el-scrollbar>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'


const props = defineProps<{
  paragraphId: String
  docId: String
  knowledgeId: String
  apiType: 'systemShare' | 'workspace' | 'systemManage'
}>()

const route = useRoute()
const {
  params: { id, documentId }, // id为knowledgeId
} = route as any

const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][props.apiType]
})

const inputRef = ref()
const loading = ref(false)
const isAddProblem = ref(false)

const problemValue = ref('')
const problemList = ref<any[]>([])

const problemOptions = ref<any[]>([])
const optionLoading = ref(false)

watch(
  () => props.paragraphId,
  (value) => {
    if (value) {
      getProblemList()
    }
  },
  {
    immediate: true,
  },
)

function delProblemHandle(item: any, index: number) {
  if (item.id) {
    const obj = {
      paragraph_id: props.paragraphId || '',
      problem_id: item.id,
    }
    loadSharedApi({ type: 'paragraph', systemType: props.apiType })
      .putDisassociationProblem(props.knowledgeId || id, documentId || props.docId, obj, loading)
      .then((res: any) => {
        getProblemList()
      })
  } else {
    problemList.value.splice(index, 1)
  }
}

function getProblemList() {
  loading.value = true
  loadSharedApi({ type: 'paragraph', systemType: props.apiType })
    .getParagraphProblem(
      props.knowledgeId || id,
      documentId || props.docId,
      props.paragraphId || '',
    )
    .then((res: any) => {
      problemList.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function addProblem() {
  isAddProblem.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}
function addProblemHandle(val: string) {
  if (props.paragraphId) {
    const obj = {
      paragraph_id: props.paragraphId,
      problem_id: val,
    }
    const api = problemOptions.value.some((option) => option.id === val)
      ? loadSharedApi({ type: 'paragraph', systemType: props.apiType }).putAssociationProblem(
          props.knowledgeId || id,
          documentId || props.docId,
          obj,
          loading,
        )
      : loadSharedApi({ type: 'paragraph', systemType: props.apiType }).postParagraphProblem(
          props.knowledgeId || id,
          documentId || props.docId,
          props.paragraphId,
          {
            content: val,
          },
          loading,
        )
    api.then(() => {
      getProblemList()
      problemValue.value = ''
      isAddProblem.value = false
    })
  } else {
    const problem = problemOptions.value.find((option) => option.id === val)
    const content = problem ? problem.content : val
    if (!problemList.value.some((item) => item.content === content)) {
      problemList.value.push({ content: content })
    }

    problemValue.value = ''
    isAddProblem.value = false
  }
}

const remoteMethod = (query: string) => {
  getProblemOption(query)
}

function getProblemOption(filterText?: string) {
  return loadSharedApi({ type: 'problem', systemType: props.apiType })
    .getProblemsPage(
      props.knowledgeId || (id as string),
      { current_page: 1, page_size: 100 },
      filterText && { content: filterText },
      optionLoading,
    )
    .then((res: any) => {
      problemOptions.value = res.data.records
    })
}

onMounted(() => {
  getProblemOption()
})
onUnmounted(() => {
  problemList.value = []
  problemValue.value = ''
  isAddProblem.value = false
})

defineExpose({
  problemList,
})
</script>
<style scoped lang="scss"></style>
