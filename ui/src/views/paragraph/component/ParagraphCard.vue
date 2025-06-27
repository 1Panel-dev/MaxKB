<template>
  <el-card
    shadow="hover"
    class="paragraph-box cursor"
    @mouseenter="cardEnter()"
    @mouseleave="cardLeave()"
    @click.stop="editParagraph(data)"
    v-loading="loading"
  >
    <div v-show="show" class="mk-sticky" v-if="!disabled">
      <el-card
        class="paragraph-box-operation mt-8 mr-8"
        shadow="always"
        style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px"
        @click.stop
      >
        <el-switch
          :loading="changeStateloading"
          v-model="data.is_active"
          :before-change="() => changeState(data)"
          size="small"
        />

        <el-divider direction="vertical" />
        <span class="mr-8">
          <el-button link @click.stop="editParagraph(data)">
            <el-icon :size="16" :title="$t('views.applicationWorkflow.control.zoomOut')">
              <EditPen />
            </el-icon>
          </el-button>
        </span>
        <span class="mr-8">
          <el-button link @click.stop="addParagraph(data)">
            <el-icon :size="16" :title="$t('views.applicationWorkflow.control.zoomOut')">
              <el-icon><CirclePlus /></el-icon>
            </el-icon>
          </el-button>
        </span>
        <el-dropdown trigger="click" :teleported="false">
          <el-button text>
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click.stop="openGenerateDialog(data)">
                <el-icon><Connection /></el-icon>
                {{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
              >
              <el-dropdown-item @click.stop="openSelectDocumentDialog(data)">
                <AppIcon iconName="app-migrate"></AppIcon>
                {{ $t('views.document.setting.migration') }}</el-dropdown-item
              >
              <el-dropdown-item icon="Delete" @click.stop="deleteParagraph(data)">{{
                $t('common.delete')
              }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-card>
    </div>
    <h2 class="mb-16">{{ data.title || '-' }}</h2>
    <MdPreview
      ref="editorRef"
      editorId="preview-only"
      :modelValue="data.content"
      class="maxkb-md"
    />

    <ParagraphDialog
      ref="ParagraphDialogRef"
      :title="title"
      @refresh="refresh"
      :apiType="apiType"
    />
    <SelectDocumentDialog
      ref="SelectDocumentDialogRef"
      @refresh="refreshMigrateParagraph"
      :apiType="apiType"
    />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" @refresh="refresh" :apiType="apiType" />
  </el-card>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import ParagraphDialog from '@/views/paragraph/component/ParagraphDialog.vue'
import SelectDocumentDialog from '@/views/paragraph/component/SelectDocumentDialog.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { t } from '@/locales'
const props = defineProps<{
  data: any
  disabled?: boolean
}>()

const route = useRoute()
const {
  params: { id, documentId },
  query: { type },
} = route as any

const apiType = computed(() => {
  return type as 'systemShare' | 'workspace' | 'systemManage'
})

const emit = defineEmits(['changeState', 'deleteParagraph', 'refresh', 'refreshMigrateParagraph'])
const loading = ref(false)
const changeStateloading = ref(false)
const show = ref(false)
// card上面存在dropdown菜单
const subHovered = ref(false)
function cardEnter() {
  show.value = true
  subHovered.value = false
}

function cardLeave() {
  show.value = subHovered.value
}

function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  loadSharedApi({ type: 'paragraph', systemType: apiType.value })
    .putParagraph(id, documentId, row.id, obj, changeStateloading)
    .then(() => {
      emit('changeState', row.id)
      return true
    })
    .catch(() => {
      return false
    })
}

const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()
function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([row.id], 'paragraph', row.id)
  }
}
function deleteParagraph(row: any) {
  MsgConfirm(
    `${t('views.paragraph.delete.confirmTitle')} ${row.title || '-'} ?`,
    t('views.paragraph.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      loadSharedApi({ type: 'paragraph', systemType: apiType.value })
        .delParagraph(id, documentId, row.id, loading)
        .then(() => {
          emit('deleteParagraph', row.id)
          MsgSuccess(t('common.deleteSuccess'))
        })
    })
    .catch(() => {})
}

const ParagraphDialogRef = ref()
const title = ref('')
function editParagraph(row: any) {
  if (!props.disabled) {
    title.value = t('views.paragraph.paragraphDetail')
    ParagraphDialogRef.value.open(row)
  }
}

function addParagraph(row: any) {
  title.value = t('views.paragraph.addParagraph')
  ParagraphDialogRef.value.open(row, 'add')
}

const SelectDocumentDialogRef = ref()
function openSelectDocumentDialog(row?: any) {
  SelectDocumentDialogRef.value.open([row.id])
}

function refresh(data?: any) {
  emit('refresh', data)
}

function refreshMigrateParagraph() {
  emit('refreshMigrateParagraph', props.data)
}
</script>
<style lang="scss" scoped>
.paragraph-box {
  background: var(--app-layout-bg-color);
  border: 1px solid #ffffff;
  box-shadow: none !important;
  position: relative;
  overflow: inherit;
  &:hover {
    background: rgba(31, 35, 41, 0.1);
    border: 1px solid #dee0e3;
  }
  .paragraph-box-operation {
    position: absolute;
    right: -10px;
    top: -10px;
    overflow: inherit;
    border: 1px solid #dee0e3;
    z-index: 10;
  }

  .mk-sticky {
    height: 0;
    position: sticky;
    right: 0;
    top: 0;
    overflow: inherit;
    z-index: 10;
  }
}
</style>
