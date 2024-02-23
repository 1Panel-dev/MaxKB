<template>
  <p class="bold title p-24" style="padding-bottom: 0">
    <span class="flex align-center">
      <span>关联问题</span>
      <el-divider direction="vertical" class="mr-4"/>
      <el-button text @click="addProblem">
        <el-icon><Plus /></el-icon>
      </el-button>
    </span>
  </p>
  <div v-loading="loading">
    <el-scrollbar height="345px">
      <div class="p-24" style="padding-top: 16px">
        <el-input
          ref="inputRef"
          v-if="isAddProblem"
          v-model="problemValue"
          @change="addProblemHandle"
          placeholder="请输入问题，回车保存"
          class="mb-8"
          autofocus
        />

        <template v-for="(item, index) in problemList" :key="index">
          <TagEllipsis
            @close="delProblemHandle(item, index)"
            class="question-tag"
            type="info"
            effect="plain"
            closable
          >
            {{ item.content }}
          </TagEllipsis>
        </template>
      </div>
    </el-scrollbar>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import paragraphApi from '@/api/paragraph'

const props = defineProps({
  problemId: String,
  docId: String,
  datasetId: String
})

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const inputRef = ref()
const loading = ref(false)
const isAddProblem = ref(false)

const problemValue = ref('')
const problemList = ref<any[]>([])

watch(
  () => props.problemId,
  (value) => {
    if (value) {
      getProblemList()
    }
  },
  {
    immediate: true
  }
)

function delProblemHandle(item: any, index: number) {
  loading.value = true
  if (item.id) {
    paragraphApi
      .delProblem(props.datasetId || id, documentId || props.docId, props.problemId || '', item.id)
      .then((res) => {
        getProblemList()
      })
      .catch(() => {
        loading.value = false
      })
  } else {
    problemList.value.splice(index, 1)
    loading.value = false
  }
}

function getProblemList() {
  loading.value = true
  paragraphApi
    .getProblem(props.datasetId || id, documentId || props.docId, props.problemId || '')
    .then((res) => {
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
  if (val) {
    const obj = {
      content: val
    }
    loading.value = true
    if (props.problemId) {
      paragraphApi
        .postProblem(props.datasetId || id, documentId || props.docId, props.problemId, obj)
        .then((res) => {
          getProblemList()
          problemValue.value = ''
          isAddProblem.value = false
        })
        .catch(() => {
          loading.value = false
        })
    } else {
      problemList.value.unshift(obj)
      problemValue.value = ''
      isAddProblem.value = false
      loading.value = false
    }
  }
}

onMounted(() => {})
onUnmounted(() => {
  problemList.value = []
  problemValue.value = ''
  isAddProblem.value = false
})

defineExpose({
  problemList
})
</script>
<style scoped lang="scss">
.question-tag {
  width: 217px;
}
</style>
