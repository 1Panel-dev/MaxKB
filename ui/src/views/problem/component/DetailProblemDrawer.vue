<template>
  <el-drawer v-model="visible" size="60%" @close="closeHandle">
    <template #header>
      <h4>{{ $t('views.problem.detailProblem') }}</h4>
    </template>
    <div>
      <el-scrollbar>
        <div class="p-8">
          <el-form label-position="top" v-loading="loading" @submit.prevent>
            <el-form-item :label="$t('views.problem.title')">
              <ReadWrite
                @change="editName"
                :data="currentContent"
                :showEditIcon="permissionPrecise.problem_edit(id as string)"
                :maxlength="256"
              />
            </el-form-item>
            <el-form-item :label="$t('views.problem.relateParagraph.title')">
              <template v-for="(item, index) in paragraphList" :key="index">
                <CardBox
                  :title="item.title || '-'"
                  class="cursor mb-8 w-full"
                  :showIcon="false"
                  @click.stop="permissionPrecise.doc_edit(id as string) && editParagraph(item)"
                  style="height: 210px"
                >
                  <template #tag>
                    <el-tooltip
                      effect="dark"
                      :content="$t('views.problem.setting.cancelRelated')"
                      placement="top"
                    >
                      <el-button
                        type="primary"
                        text
                        @click.stop="disassociation(item)"
                        v-if="permissionPrecise.problem_relate(id as string)"
                      >
                        <AppIcon iconName="app-quxiaoguanlian"></AppIcon>
                      </el-button>
                    </el-tooltip>
                  </template>
                  <el-scrollbar height="110">
                    {{ item.content }}
                  </el-scrollbar>

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
      <ParagraphDialog
        ref="ParagraphDialogRef"
        :title="$t('views.paragraph.editParagraph')"
        :apiType="apiType"
        @refresh="refresh"
      />
      <RelateProblemDialog ref="RelateProblemDialogRef" @refresh="refresh" />
    </div>
    <template #footer>
      <div>
        <el-button @click="relateProblem" v-if="permissionPrecise.doc_edit(id as string)">{{
          $t('views.problem.relateParagraph.title')
        }}</el-button>
        <el-button @click="pre" :disabled="pre_disable || loading">{{
          $t('views.chatLog.buttons.prev')
        }}</el-button>
        <el-button @click="next" :disabled="next_disable || loading">{{
          $t('views.chatLog.buttons.next')
        }}</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import ParagraphDialog from '@/views/paragraph/component/ParagraphDialog.vue'
import RelateProblemDialog from './RelateProblemDialog.vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
import { t } from '@/locales'
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
  {},
)

const emit = defineEmits(['update:currentId', 'update:currentContent', 'refresh'])

const route = useRoute()
const {
  params: { id },
} = route

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const RelateProblemDialogRef = ref()
const ParagraphDialogRef = ref()
const loading = ref(false)
const visible = ref(false)
const paragraphList = ref<any[]>([])

function disassociation(item: any) {
  const obj = {
    paragraph_id: item.id,
    problem_id: props.currentId,
  }
  loadSharedApi({ type: 'paragraph', systemType: apiType.value })
    .putDisassociationProblem(item.knowledge_id, item.document_id, obj, loading)
    .then(() => {
      getRecord()
    })
}

function relateProblem() {
  RelateProblemDialogRef.value.open([props.currentId])
}

function editParagraph(row: any) {
  ParagraphDialogRef.value.open(row, 'edit')
}

function editName(val: string) {
  if (val) {
    const obj = {
      content: val,
    }
    loadSharedApi({ type: 'problem', systemType: apiType.value })
      .putProblems(id as string, props.currentId, obj, loading)
      .then(() => {
        emit('update:currentContent', val)
        MsgSuccess(t('common.modifySuccess'))
      })
  } else {
    MsgError(t('views.problem.tip.errorMessage'))
  }
}

function closeHandle() {
  paragraphList.value = []
}

function getRecord() {
  if (props.currentId && visible.value) {
    loadSharedApi({ type: 'problem', systemType: apiType.value })
      .getDetailProblems(id as string, props.currentId, loading)
      .then((res: any) => {
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
  },
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
  open,
})
</script>
<style lang="scss"></style>
