<template>
  <p class="bold title p-24" style="padding-bottom: 0">
    <span class="flex align-center">
      <span>关联问题</span>
      <el-divider direction="vertical" class="mr-4" />
      <el-button text @click="addProblem">
        <el-icon><Plus /></el-icon>
      </el-button>
    </span>
  </p>
  <div v-loading="loading">
    <el-scrollbar height="345px">
      <div class="p-24" style="padding-top: 16px">
        <!-- <el-input
          ref="inputRef"
          v-if="isAddProblem"
          v-model="problemValue"
          @change="addProblemHandle"
          placeholder="请输入问题，回车保存"
          class="mb-8"
          autofocus
        /> -->
        <el-select
          v-if="isAddProblem"
          v-model="problemValue"
          filterable
          allow-create
          default-first-option
          :reserve-keyword="false"
          placeholder="请选择问题"
          remote
          :remote-method="remoteMethod"
          :loading="optionLoading"
          @change="addProblemHandle"
        >
          <el-option
            v-for="item in problemOptions"
            :key="item.id"
            :label="item.content"
            :value="item.id"
          />
        </el-select>
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
import useStore from '@/stores'

const props = defineProps({
  problemId: String,
  docId: String,
  datasetId: String
})

const route = useRoute()
const {
  params: { id, documentId } // id为datasetId
} = route as any

const { problem } = useStore()
const inputRef = ref()
const loading = ref(false)
const isAddProblem = ref(false)

const problemValue = ref('')
const problemList = ref<any[]>([])

const problemOptions = ref<any[]>([])
const optionLoading = ref(false)

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
  console.log(val)
  // if (val) {
  //   const obj = {
  //     content: val
  //   }
  //   loading.value = true
  //   if (props.problemId) {
  //     paragraphApi
  //       .postProblem(props.datasetId || id, documentId || props.docId, props.problemId, obj)
  //       .then((res) => {
  //         getProblemList()
  //         problemValue.value = ''
  //         isAddProblem.value = false
  //       })
  //       .catch(() => {
  //         loading.value = false
  //       })
  //   } else {
  //     problemList.value.unshift(obj)
  //     problemValue.value = ''
  //     isAddProblem.value = false
  //     loading.value = false
  //   }
  // }
}

const remoteMethod = (query: string) => {
  if (query) {
    getProblemOption(query)
  } else {
    problemOptions.value = []
  }
}

function getProblemOption(filterText?: string) {
  return problem
    .asyncGetProblem(
      id as string,
      { current_page: 1, page_size: 100 },
      filterText && { content: filterText },
      optionLoading
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
  problemList
})
</script>
<style scoped lang="scss">
.question-tag {
  width: 217px;
}
</style>
