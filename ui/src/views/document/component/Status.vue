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
  [TaskType.EMBEDDING]: '索引中',
  [TaskType.GENERATE_PROBLEM]: '生成中',
  [TaskType.SYNC]: '同步中'
}
const taskTypeMap = {
  [TaskType.EMBEDDING]: '向量化',
  [TaskType.GENERATE_PROBLEM]: '生成问题',
  [TaskType.SYNC]: '同步'
}
const stateMap: any = {
  [State.PENDING]: (type: number) => '排队中',
  [State.STARTED]: (type: number) => startedMap[type],
  [State.REVOKE]: (type: number) => '取消中',
  [State.REVOKED]: (type: number) => '成功',
  [State.FAILURE]: (type: number) => '失败',
  [State.SUCCESS]: (type: number) => '成功'
}
</script>
<style lang="scss" scoped></style>
