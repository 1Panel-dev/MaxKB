<template>
  <div class="workflow-publish-history border-l white-bg">
    <h4 class="border-b p-16-24">{{ $t('views.applicationWorkflow.setting.releaseHistory') }}</h4>
    <div class="list-height pt-0">
      <el-scrollbar>
        <div class="p-8 pt-0">
          <common-list
            :data="LogData"
            class="mt-8"
            v-loading="loading"
            @click="clickListHandle"
            @mouseenter="mouseenter"
            @mouseleave="mouseId = ''"
          >
            <template #default="{ row, index }">
              <div class="flex-between">
                <div style="max-width: 80%">
                  <h5 :class="index === 0 ? 'primary' : ''" class="flex align-center">
                    <ReadWrite
                      @change="editName($event, row)"
                      :data="row.name || datetimeFormat(row.update_time)"
                      trigger="manual"
                      :write="row.writeStatus"
                      @close="closeWrite(row)"
                    />
                    <el-tag v-if="index === 0" class="default-tag ml-4">{{
                      $t('views.applicationWorkflow.setting.latestRelease')
                    }}</el-tag>
                  </h5>
                  <el-text type="info" class="color-secondary flex align-center mt-8">
                    <el-avatar :size="20" class="avatar-grey mr-4">
                      <el-icon><UserFilled /></el-icon>
                    </el-avatar>
                    {{ row.publish_user_name }}
                  </el-text>
                </div>

                <div @click.stop v-show="mouseId === row.id">
                  <el-dropdown trigger="click" :teleported="false">
                    <el-button text>
                      <AppIcon iconName="app-more"></AppIcon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click.stop="openEditVersion(row)">
                          <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
                          {{ $t('common.edit') }}
                        </el-dropdown-item>
                        <el-dropdown-item @click="refreshVersion(row)">
                          <el-icon class="color-secondary"><RefreshLeft /></el-icon>
                          {{ $t('views.applicationWorkflow.setting.restoreCurrentVersion') }}
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </template>

            <template #empty>
              <div class="text-center">
                <el-text type="info"> {{ $t('chat.noHistory') }}</el-text>
              </div>
            </template>
          </common-list>
        </div>
      </el-scrollbar>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgError } from '@/utils/message'
import { t } from '@/locales'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
const route = useRoute()
const {
  params: { id },
} = route as any
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const emit = defineEmits(['click', 'refreshVersion'])
const loading = ref(false)
const LogData = ref<any[]>([])

const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}

function clickListHandle(item: any) {
  emit('click', item)
}

function refreshVersion(item: any) {
  emit('refreshVersion', item)
}

function openEditVersion(item: any) {
  item['writeStatus'] = true
}

function closeWrite(item: any) {
  item['writeStatus'] = false
}

function editName(val: string, item: any) {
  if (val) {
    const obj = {
      name: val,
    }
    loadSharedApi({ type: 'workflowVersion', systemType: apiType.value })
      .putWorkFlowVersion(id as string, item.id, obj, loading)
      .then(() => {
        MsgSuccess(t('common.modifySuccess'))
        item['writeStatus'] = false
        getList()
      })
  } else {
    MsgError(t('views.applicationWorkflow.tip.nameMessage'))
  }
}

function getList() {
  loadSharedApi({ type: 'workflowVersion', systemType: apiType.value })
    .getWorkFlowVersion(id, loading)
    .then((res: any) => {
      LogData.value = res.data
    })
}

onMounted(() => {
  getList()
})
</script>
<style lang="scss" scoped>
.workflow-publish-history {
  width: 320px;
  position: absolute;
  right: 0;
  top: 57px;
  height: calc(100vh - 57px);
  z-index: 9;
  .list-height {
    height: calc(100vh - 120px);
  }
}
</style>
