<template>
  <el-dialog
    :title="$t('views.application.applicationForm.dialogues.addDataset')"
    v-model="dialogVisible"
    width="600"
    append-to-body
    class="addDataset-dialog"
    align-center
  >
    <template #header="{ titleId, titleClass }">
      <div class="flex-between mb-8">
        <h4 :id="titleId" :class="titleClass">
          {{ $t('views.application.applicationForm.dialogues.addDataset') }}
        </h4>
        <div class="flex align-center">
          <el-button link class="ml-16" @click="refresh">
            <el-icon class="mr-4"><Refresh /></el-icon
            >{{ $t('views.application.applicationForm.dialogues.refresh') }}
          </el-button>
          <el-divider direction="vertical" />
        </div>
      </div>
      <el-text type="info" class="color-secondary">
        所选知识库必须使用相同的 Embedding 模型
      </el-text>
    </template>
    <el-scrollbar>
      <div class="max-height">
        <el-row :gutter="12" v-loading="loading">
          <el-col :span="12" v-for="(item, index) in filterData" :key="index" class="mb-16">
            <CardCheckbox value-field="id" :data="item" v-model="checkList" @change="changeHandle">
              <span class="ellipsis">
                {{ item.name }}
              </span>
            </CardCheckbox>
          </el-col>
        </el-row>
      </div>
    </el-scrollbar>
    <template #footer>
      <div class="flex-between">
        <div class="flex">
          <el-text type="info" class="color-secondary mr-8" v-if="checkList.length > 0">
            已选 {{ checkList.length }} 个知识库
          </el-text>
          <el-button link type="primary" v-if="checkList.length > 0" @click="clearCheck">
            清空
          </el-button>
        </div>
        <span>
          <el-button @click.prevent="dialogVisible = false">
            {{ $t('views.application.applicationForm.buttons.cancel') }}
          </el-button>
          <el-button type="primary" @click="submitHandle">
            {{ $t('views.application.applicationForm.buttons.confirm') }}
          </el-button>
        </span>
      </div>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  },
  loading: Boolean
})

const emit = defineEmits(['addData', 'refresh'])

const dialogVisible = ref<boolean>(false)
const checkList = ref([])
const currentEmbedding = ref('')

const filterData = computed(() => {
  return currentEmbedding.value
    ? props.data.filter((v) => v.embedding_mode_id === currentEmbedding.value)
    : props.data
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    checkList.value = []
    currentEmbedding.value = ''
  }
})

function changeHandle() {
  if (checkList.value.length > 0) {
    currentEmbedding.value = props.data.filter(
      (v) => v.id === checkList.value[0]
    )[0].embedding_mode_id
  } else if (checkList.value.length === 0) {
    currentEmbedding.value = ''
  }
}
function clearCheck() {
  checkList.value = []
  currentEmbedding.value = ''
}

const open = (checked: any) => {
  checkList.value = checked
  if (checkList.value.length > 0) {
    currentEmbedding.value = props.data.filter(
      (v) => v.id === checkList.value[0]
    )[0].embedding_mode_id
  }

  dialogVisible.value = true
}
const submitHandle = () => {
  emit('addData', checkList.value)
  dialogVisible.value = false
}

const refresh = () => {
  emit('refresh')
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.addDataset-dialog {
  padding: 0;
  .el-dialog__header {
    padding: 24px 24px 8px 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .el-dialog__footer {
    padding: 8px 24px 24px 24px;
  }
  .el-dialog__header.show-close {
    padding-right: 34px;
  }
  .el-dialog__headerbtn {
    top: 13px;
  }
  .max-height {
    max-height: calc(100vh - 260px);
    padding: 0 16px;
  }
}
</style>
