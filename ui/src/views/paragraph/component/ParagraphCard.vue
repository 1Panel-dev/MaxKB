<template>
  <el-card
    shadow="hover"
    class="paragraph-box cursor"
    :class="data.is_active ? '' : 'disabled'"
    @mouseenter="cardEnter()"
    @mouseleave="cardLeave()"
    @click.stop="handleClickCard(data)"
    v-loading="loading"
  >
    <div v-show="show" class="mk-sticky" v-if="!disabled">
      <el-card
        class="paragraph-box-operation mt-8 mr-8"
        shadow="always"
        style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px"
        @click.stop
        v-if="MoreFieldPermission(id)"
      >
        <el-switch
          :loading="changeStateloading"
          v-model="data.is_active"
          :before-change="() => changeState(data)"
          size="small"
          v-if="permissionPrecise.doc_edit(id)"
        />

        <el-divider direction="vertical" />
        <span class="mr-8">
          <el-tooltip
            effect="dark"
            :content="$t('views.paragraph.editParagraph')"
            placement="top"
            v-if="permissionPrecise.doc_edit(id)"
          >
            <el-button text @click.stop="editParagraph(data)">
              <AppIcon iconName="app-edit" :size="16" class="color-secondary"></AppIcon>
            </el-button>
          </el-tooltip>
        </span>
        <span class="mr-8">
          <el-tooltip
            effect="dark"
            :content="$t('views.paragraph.prevAddParagraph')"
            placement="top"
            v-if="permissionPrecise.doc_edit(id)"
          >
            <el-button text @click.stop="addParagraph(data)" v-if="permissionPrecise.doc_edit(id)">
              <AppIcon
                iconName="app-add-circle-outlined"
                class="color-secondary"
                :size="16"
              ></AppIcon>
            </el-button>
          </el-tooltip>
        </span>
        <el-dropdown trigger="click" :teleported="false" v-if="MoreFieldPermission(id)">
          <el-button text>
            <AppIcon iconName="app-more" class="color-secondary"></AppIcon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu style="min-width: 140px">
              <el-dropdown-item
                @click.stop="openGenerateDialog(data)"
                v-if="permissionPrecise.doc_generate(id)"
              >
                <AppIcon iconName="app-generate-question" class="color-secondary"></AppIcon>
                {{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
              >
              <el-dropdown-item
                @click.stop="openSelectDocumentDialog(data)"
                v-if="permissionPrecise.doc_edit(id)"
              >
                <AppIcon iconName="app-migrate" class="color-secondary"></AppIcon>
                {{ $t('views.document.setting.migration') }}</el-dropdown-item
              >
              <el-dropdown-item v-if="permissionPrecise.doc_edit(id)">
                <el-dropdown
                  class="w-full"
                  trigger="hover"
                  :show-arrow="false"
                  placement="right-start"
                  popper-class="move-position-popper"
                >
                  <div class="w-full flex-between" style="line-height: 22px">
                    <div class="flex align-center">
                      <AppIcon iconName="app-drag-outlined" class="color-secondary"></AppIcon>
                      {{ $t('views.document.movePosition.title') }}
                    </div>
                    <el-icon class="color-input-placeholder" :size="16" style="margin-right: 0"
                      ><ArrowRight
                    /></el-icon>
                  </div>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        :disabled="!props.showMoveUp"
                        @click.stop="emit('move', 'up')"
                      >
                        {{ $t('views.document.movePosition.moveUp') }}
                      </el-dropdown-item>
                      <el-dropdown-item
                        :disabled="!props.showMoveDown"
                        @click.stop="emit('move', 'down')"
                      >
                        {{ $t('views.document.movePosition.moveDown') }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </el-dropdown-item>
              <el-dropdown-item
                @click.stop="deleteParagraph(data)"
                v-if="permissionPrecise.doc_edit(id)"
              >
                <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                {{ $t('common.delete') }}</el-dropdown-item
              >
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
      style="background: none"
      @clickPreview="handleClickCard(data)"
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import ParagraphDialog from '@/views/paragraph/component/ParagraphDialog.vue'
import SelectDocumentDialog from '@/views/paragraph/component/SelectDocumentDialog.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'
import { t } from '@/locales'
const props = defineProps<{
  data: any
  disabled?: boolean
  showMoveUp?: boolean
  showMoveDown?: boolean
}>()

const route = useRoute()
const {
  params: { id, documentId },
  query: { from, isShared },
} = route as any

const shareDisabled = computed(() => {
  return isShared === 'true'
})

const apiType = computed(() => {
  return from as 'systemShare' | 'workspace' | 'systemManage'
})

const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][apiType.value]
})

const MoreFieldPermission = (id: any) => {
  return permissionPrecise.value.doc_generate(id) || permissionPrecise.value.doc_edit(id)
}

const emit = defineEmits([
  'dialogVisibleChange',
  'clickCard',
  'changeState',
  'deleteParagraph',
  'refresh',
  'refreshMigrateParagraph',
  'move',
])
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

async function changeState(row: any) {
  const obj = {
    is_active: !row.is_active,
  }
  await loadSharedApi({ type: 'paragraph', systemType: apiType.value })
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
    title.value = t('views.paragraph.editParagraph')
    ParagraphDialogRef.value.open(row, 'edit')
  }
}

const cardClick = permissionPrecise.value.doc_edit(id)

function handleClickCard(row: any) {
  if (!cardClick || dialogVisible.value) {
    return
  }
  if (!props.disabled) {
    title.value = t('views.paragraph.paragraphDetail')
    ParagraphDialogRef.value.open(row)
  } else {
    emit('clickCard')
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

const dialogVisible = computed(
  () =>
    ParagraphDialogRef.value?.dialogVisible ||
    SelectDocumentDialogRef.value?.dialogVisible ||
    GenerateRelatedDialogRef.value?.dialogVisible,
)

watch(dialogVisible, (val: boolean) => {
  emit('dialogVisibleChange', val)
})
</script>
<style lang="scss" scoped>
.paragraph-box {
  background: var(--app-layout-bg-color);
  border: 1px solid #ffffff;
  box-shadow: none !important;
  position: relative;
  overflow: inherit;
  &:hover {
    background: var(--app-text-color-light-1);
    border: 1px solid #dee0e3;
  }
  &.disabled {
    color: var(--app-text-color-disable) !important;
    :deep(.md-editor-preview) {
      color: var(--app-text-color-disable) !important;
    }
    &:hover {
      background: var(--app-layout-bg-color);
      border: 1px solid #ffffff;
    }
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

<style lang="scss">
.move-position-popper {
  .el-popper__arrow {
    display: none;
  }
}
</style>
