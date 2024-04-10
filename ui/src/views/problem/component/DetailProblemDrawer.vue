<template>
  <el-drawer v-model="visible" size="60%" @close="closeHandel">
    <template #header>
      <h4>问题详情</h4>
    </template>
    <div>
      <el-scrollbar>
        <div class="p-8">
          <el-form label-position="top" v-loading="loading" @submit.prevent>
            <el-form-item label="问题">
              <ReadWrite
                @change="editName"
                :data="currentContent"
                :showEditIcon="true"
                :maxlength="256"
              />
            </el-form-item>
            <el-form-item label="关联分段">
              <template v-for="(item, index) in paragraphList" :key="index">
                <CardBox
                  :title="item.title || '-'"
                  class="paragraph-source-card cursor mb-8"
                  :showIcon="false"
                  @click.stop="editParagraph(item)"
                >
                  <div class="active-button">
                    <span class="mr-4">
                      <el-tooltip effect="dark" content="取消关联" placement="top">
                        <el-button type="primary" text @click.stop="disassociation(item)">
                          <AppIcon iconName="app-quxiaoguanlian"></AppIcon>
                        </el-button>
                      </el-tooltip>
                    </span>
                  </div>
                  <template #description>
                    <el-scrollbar height="80">
                      {{ item.content }}
                    </el-scrollbar>
                  </template>
                  <template #footer>
                    <div class="footer-content flex-between">
                      <el-text>
                        <el-icon>
                          <Document />
                        </el-icon>
                        {{ item?.document_name }}
                      </el-text>
                    </div>
                  </template>
                </CardBox>
              </template>
            </el-form-item>
          </el-form>
        </div>
      </el-scrollbar>
      <ParagraphDialog ref="ParagraphDialogRef" title="编辑分段" @refresh="refresh" />
      <RelateProblemDialog ref="RelateProblemDialogRef" @refresh="refresh" />
    </div>
    <template #footer>
      <div>
        <el-button @click="relateProblem">关联分段</el-button>
        <el-button @click="pre" :disabled="pre_disable || loading">上一条</el-button>
        <el-button @click="next" :disabled="next_disable || loading">下一条</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import problemApi from '@/api/problem'
import ParagraphDialog from '@/views/paragraph/component/ParagraphDialog.vue'
import RelateProblemDialog from './RelateProblemDialog.vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'

const props = withDefaults(
  defineProps<{
    /**
     * 当前的id
     */
    currentId: string
    currentContent: string
    /**
     * 下一条
     */
    next: () => void
    /**
     * 上一条
     */
    pre: () => void

    pre_disable: boolean

    next_disable: boolean
  }>(),
  {}
)

const emit = defineEmits(['update:currentId', 'update:currentContent', 'refresh'])

const route = useRoute()
const {
  params: { id }
} = route

const { problem } = useStore()
const RelateProblemDialogRef = ref()
const ParagraphDialogRef = ref()
const loading = ref(false)
const visible = ref(false)
const paragraphList = ref<any[]>([])

function disassociation(item: any) {
  problem
    .asyncDisassociationProblem(
      item.dataset_id,
      item.document_id,
      item.id,
      props.currentId,
      loading
    )
    .then(() => {
      getRecord()
    })
}

function relateProblem() {
  RelateProblemDialogRef.value.open(props.currentId)
}

function editParagraph(row: any) {
  ParagraphDialogRef.value.open(row)
}

function editName(val: string) {
  if (val) {
    const obj = {
      content: val
    }
    problemApi.putProblems(id as string, props.currentId, obj, loading).then(() => {
      emit('update:currentContent', val)
      MsgSuccess('修改成功')
    })
  } else {
    MsgError('问题不能为空！')
  }
}

function closeHandel() {
  paragraphList.value = []
}

function getRecord() {
  if (props.currentId && visible.value) {
    problemApi.getDetailProblems(id as string, props.currentId, loading).then((res) => {
      paragraphList.value = res.data
    })
  }
}

function refresh() {
  getRecord()
}

watch(
  () => props.currentId,
  () => {
    paragraphList.value = []
    getRecord()
  }
)

watch(visible, (bool) => {
  if (!bool) {
    emit('update:currentId', '')
    emit('update:currentContent', '')
    emit('refresh')
  }
})

const open = () => {
  getRecord()
  visible.value = true
}

defineExpose({
  open
})
</script>
<style lang="scss"></style>
