<template>
  <el-dialog
    title="编辑分段"
    v-model="dialogVisible"
    width="80%"
    destroy-on-close
    class="paragraph-dialog"
  >
    <el-row v-if="isConnect">
      <el-col :span="18" class="p-24">
        <ParagraphForm ref="paragraphFormRef" :data="detail" :isEdit="true" />
      </el-col>
      <el-col :span="6" class="border-l" style="width: 300px">
        <p class="bold title p-24" style="padding-bottom: 0">
          <span class="flex align-center">
            <span>关联问题</span>
            <el-divider direction="vertical" class="mr-4" />
            <el-button text @click="addProblem">
              <el-icon><Plus /></el-icon>
            </el-button>
          </span>
        </p>
        <el-scrollbar height="500px">
          <div class="p-24" style="padding-top: 16px">
            <el-input
              v-if="isAddProblem"
              v-model="problemValue"
              placeholder="请选择问题"
              @change="addProblemHandle"
              @blur="isAddProblem = false"
              ref="inputRef"
            />

            <template v-for="(item, index) in detail.problem_list" :key="index">
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
      </el-col>
    </el-row>
    <div v-else class="p-24">
      <ParagraphForm ref="paragraphFormRef" :data="detail" :isEdit="true" />
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submitHandle"> 保存 </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { cloneDeep } from 'lodash'
import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'

const props = defineProps({
  isConnect: Boolean
})

const emit = defineEmits(['updateContent'])

const dialogVisible = ref<boolean>(false)

const detail = ref<any>({})

const paragraphFormRef = ref()
const inputRef = ref()

const isAddProblem = ref(false)

const problemValue = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
  }
})

const open = (data: any) => {
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}

function delProblemHandle(item: any, index: number) {
  detail.value.problem_list.splice(index, 1)
}
function addProblemHandle() {
  if (problemValue.value.trim()) {
    detail.value?.problem_list?.push({
      content: problemValue.value.trim()
    })
    problemValue.value = ''
    isAddProblem.value = false
  }
}
function addProblem() {
  isAddProblem.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    emit('updateContent', {
      problem_list: detail.value.problem_list,
      ...paragraphFormRef.value?.form
    })
    dialogVisible.value = false
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope></style>
