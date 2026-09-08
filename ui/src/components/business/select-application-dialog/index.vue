<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import ApplicationApi from '@/api/admin/workspace/application/application'
import type { FolderItem, ApplicationDetail } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRIES } from '@/constants/folder'
import FolderTree from '@/components/business/folder-tree/index.vue'
import MkCardCheckbox from '@/components/mk-card-checkbox/index.vue'
import MkSourceCard from '@/components/mk-source-card/index.vue'

defineOptions({ name: 'SelectApplicationDialog' })

const props = withDefaults(defineProps<{ excludedIds?: string[] }>(), { excludedIds: () => [] })

const emit = defineEmits<{ submit: [application: (Partial<ApplicationDetail> & { id: string })[]] }>()
const visible = ref(false)
const loading = ref(false)
const searchKeyword = ref('')
const appliedSearchKeyword = ref('')
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.APPLICATION].all })
const applicationOptions = ref<ApplicationDetail[]>([])
const selectedApplication = ref<(Partial<ApplicationDetail> & { id: string })[]>([])
const applicationLayoutRef = useTemplateRef<{ setScrollTop: (scrollTop: number) => void }>('applicationLayoutRef')
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
let dialogVersion = 0

const selectedApplicationIds = computed(() => selectedApplication.value.map(({ id }) => id))

function toggleApplication(application: ApplicationDetail) {
  selectedApplication.value = selectedApplicationIds.value.includes(application.id)
    ? selectedApplication.value.filter(({ id }) => id !== application.id)
    : [...selectedApplication.value, cloneDeep(application)]
}

// 每次查询一次加载全部结果，忽略切换目录或关闭弹窗前发出的旧请求。
function refreshApplication() {
  const version = ++dialogVersion
  loading.value = true
  applicationOptions.value = []
  appliedSearchKeyword.value = searchKeyword.value.trim()
  return ApplicationApi.getAllApplication({
    folder_id: currentFolder.value.id,
    publish_status: 'published',
    ...(appliedSearchKeyword.value ? { name: appliedSearchKeyword.value } : {}),
  })
    .then((application) => {
      if (version !== dialogVersion) return
      applicationOptions.value = application.filter((resource) => resource.is_publish && !props.excludedIds.includes(resource.id))
      // 仅补全已选快照，不因查询结果缺少某个 ID 而删除关联。
      const applicationById = new Map(application.map((application) => [application.id, application]))
      selectedApplication.value = selectedApplication.value.map((application) => applicationById.get(application.id) ?? application)
      return nextTick(() => {
        if (version === dialogVersion) applicationLayoutRef.value?.setScrollTop(0)
      })
    })
    .finally(() => {
      if (version === dialogVersion) loading.value = false
    })
}

function refreshResources() {
  folderTreeRef.value?.refresh()
  void refreshApplication()
}

function selectFolder(folder?: FolderItem) {
  if (!folder || folder.id === currentFolder.value.id) return
  currentFolder.value = folder
  void refreshApplication()
}

function open(application: (Partial<ApplicationDetail> & { id: string })[]) {
  resetData()
  selectedApplication.value = cloneDeep(application)
  visible.value = true
  void refreshApplication()
}

function submit() {
  emit('submit', cloneDeep(selectedApplication.value))
  visible.value = false
}
function resetData() {
  dialogVersion++
  loading.value = false
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
  currentFolder.value = { ...FOLDER_ENTRIES[RESOURCE_TYPE.APPLICATION].all }
  applicationOptions.value = []
  selectedApplication.value = []
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" title="智能体" width="1200" @closed="resetData">
    <template #header="{ titleId }">
      <div class="flex-between pr-8">
        <div class="flex items-center gap-2">
          <h4 :id="titleId">智能体</h4>
        </div>

        <el-button text class="h-7! w-7! min-w-0! p-1!" title="刷新" aria-label="刷新智能体" @click="refreshResources">
          <MkIcon name="icon_refresh_outlined" :size="20" />
        </el-button>
      </div>
    </template>

    <MkViewLayout ref="applicationLayoutRef" :loading="loading" title="">
      <template #aside>
        <FolderTree
          ref="folderTreeRef"
          class="pt-4"
          :can-edit="false"
          :show-shared="false"
          :source="RESOURCE_TYPE.APPLICATION"
          @loaded="selectFolder"
          @select="selectFolder"
        />
      </template>
      <template #default="{ Header }">
        <component :is="Header">
          <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
          <MkSearchInput v-model="searchKeyword" class="w-60! shrink-0" @change="refreshApplication" />
        </component>

        <template v-if="!loading">
          <div v-if="applicationOptions.length" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            <template v-for="application in applicationOptions" :key="application.id">
              <el-popover placement="bottom-start" :width="360" :show-after="500" :persistent="false" popper-class="border-none! rounded-xl!">
                <template #reference>
                  <MkCardCheckbox
                    :model-value="selectedApplicationIds.includes(application.id)"
                    :label="application.name"
                    @update:model-value="toggleApplication(application)"
                  >
                    <div class="flex min-w-0 flex-1 items-center gap-2">
                      <ApplicationIcon :icon="application.icon" class="shrink-0" />
                      <span class="min-w-0 flex-1 truncate" :title="application.name">{{ application.name }}</span>
                    </div>
                  </MkCardCheckbox>
                </template>
                <template #default>
                  <MkSourceCard :title="application.name" :nick_name="application.nick_name || '-'" :create_time="application.create_time">
                    <template #icon><ApplicationIcon :icon="application.icon" /></template>
                    <p class="line-clamp-2" :title="application.desc || '-'">{{ application.desc || '-' }}</p>
                  </MkSourceCard>
                </template>
              </el-popover>
            </template>
          </div>
          <MkEmpty v-else class="mt-24" :type="appliedSearchKeyword ? 'search' : 'default'" />
        </template>
      </template>
    </MkViewLayout>
    <template #footer>
      <div class="flex-between -mx-6 border-t px-6 pt-4">
        <div class="flex items-center gap-2">
          <span class="text-N600">已选 {{ selectedApplication.length }}</span>
          <el-button v-if="selectedApplication.length" link type="primary" @click="selectedApplication = []">清空</el-button>
        </div>
        <div>
          <el-button plain @click="visible = false">取消</el-button>
          <el-button type="primary" @click="submit">确定</el-button>
        </div>
      </div>
    </template>
  </MkDialog>
</template>
