<template>
  <el-popover
    v-model:visible="visible"
    placement="top"
    trigger="hover"
    :popper-style="{ width: 'auto' }"
  >
    <template #default
      ><StatusTable
        v-if="visible"
        :status="status"
        :statusMeta="statusMeta"
        :taskTypeMap="taskTypeMap"
        :stateMap="stateMap"
      ></StatusTable>
    </template>
    <template #reference>
      <el-text v-if="aggStatus?.value === State.SUCCESS || aggStatus?.value === State.REVOKED">
        <el-icon class="success"><SuccessFilled /></el-icon>
        {{ stateMap[aggStatus.value](aggStatus.key) }}
      </el-text>
      <el-text v-else-if="aggStatus?.value === State.FAILURE">
        <el-icon class="danger"><CircleCloseFilled /></el-icon>
        {{ stateMap[aggStatus.value](aggStatus.key) }}
      </el-text>
      <el-text v-else-if="aggStatus?.value === State.STARTED">
        <el-icon class="is-loading primary"><Loading /></el-icon>
        {{ stateMap[aggStatus.value](aggStatus.key) }}
      </el-text>
      <el-text v-else-if="aggStatus?.value === State.PENDING">
        <el-icon class="is-loading primary"><Loading /></el-icon>
        {{ stateMap[aggStatus.value](aggStatus.key) }}
      </el-text>
      <el-text v-else-if="aggStatus?.value === State.REVOKE">
        <el-icon class="is-loading primary"><Loading /></el-icon>
        {{ stateMap[aggStatus.value](aggStatus.key) }}
      </el-text>
    </template>
  </el-popover>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { TaskType, State } from '@/utils/status'
import StatusTable from '@/views/document/component/StatusTable.vue'
import { t } from '@/locales'
const props = defineProps<{ status: string; statusMeta: any }>()
const visible = ref<boolean>(false)
const checkList: Array<string> = [
  State.REVOKE,
  State.STARTED,
  State.PENDING,
  State.FAILURE,
  State.REVOKED,
  State.SUCCESS
]
const aggStatus = computed(() => {
  let obj = { key: 0, value: '' }
  for (const i in checkList) {
    const state = checkList[i]
    const index = props.status.indexOf(state)
    if (index > -1) {
      obj = { key: props.status.length - index, value: state }
      break
    }
  }
  return obj
})
const startedMap = {
  [TaskType.EMBEDDING]: t('views.document.fileStatus.EMBEDDING'),
  [TaskType.GENERATE_PROBLEM]: t('views.document.fileStatus.GENERATE'),
  [TaskType.SYNC]: t('views.document.fileStatus.SYNC')
}
const taskTypeMap = {
  [TaskType.EMBEDDING]: t('views.dataset.setting.vectorization'),
  [TaskType.GENERATE_PROBLEM]: t('views.document.generateQuestion.title'),
  [TaskType.SYNC]: t('views.dataset.setting.sync')
}
const stateMap: any = {
  [State.PENDING]: (type: number) => t('views.document.fileStatus.PENDING'),
  [State.STARTED]: (type: number) => startedMap[type],
  [State.REVOKE]: (type: number) => t('views.document.fileStatus.REVOKE'),
  [State.REVOKED]: (type: number) => t('views.document.fileStatus.SUCCESS'),
  [State.FAILURE]: (type: number) => t('views.document.fileStatus.FAILURE'),
  [State.SUCCESS]: (type: number) => t('views.document.fileStatus.SUCCESS'),
}
</script>
<style lang="scss" scoped></style>
