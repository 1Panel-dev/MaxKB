<template>
  <el-popover placement="top" :width="450" trigger="hover">
    <template #default>
      <el-row :gutter="3" v-for="status in statusTable" :key="status.type">
        <el-col :span="4">{{ taskTypeMap[status.type] }} </el-col>
        <el-col :span="4">
          <el-text v-if="status.state === State.SUCCESS || status.state === State.REVOKED">
            <el-icon class="success"><SuccessFilled /></el-icon>
            {{ stateMap[status.state](status.type) }}
          </el-text>
          <el-text v-else-if="status.state === State.FAILURE">
            <el-icon class="danger"><CircleCloseFilled /></el-icon>
            {{ stateMap[status.state](status.type) }}
          </el-text>
          <el-text v-else-if="status.state === State.STARTED">
            <el-icon class="is-loading primary"><Loading /></el-icon>
            {{ stateMap[status.state](status.type) }}
          </el-text>
          <el-text v-else-if="status.state === State.PENDING">
            <el-icon class="is-loading primary"><Loading /></el-icon>
            {{ stateMap[status.state](status.type) }}
          </el-text>
          <el-text v-else-if="aggStatus?.value === State.REVOKE">
            <el-icon class="is-loading primary"><Loading /></el-icon>
            {{ stateMap[aggStatus.value](aggStatus.key) }}
          </el-text>
        </el-col>
        <el-col :span="5">
          完成
          {{
            Object.keys(status.aggs ? status.aggs : {})
              .filter((k) => k == State.SUCCESS)
              .map((k) => status.aggs[k])
              .reduce((x: any, y: any) => x + y, 0)
          }}/{{
            Object.values(status.aggs ? status.aggs : {}).reduce((x: any, y: any) => x + y, 0)
          }}
        </el-col>
        <el-col :span="9">
          {{
            status.time
              ? status.time[
                  status.state == State.REVOKED ? State.REVOKED : State.PENDING
                ]?.substring(0, 19)
              : undefined
          }}
        </el-col>
      </el-row>
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
import { computed } from 'vue'
import { Status, TaskType, State, type TaskTypeInterface } from '@/utils/status'
import { mergeWith } from 'lodash'
const props = defineProps<{ status: string; statusMeta: any }>()

const checkList: Array<string> = [
  State.REVOKE,
  State.STARTED,
  State.PENDING,
  State.REVOKED,
  State.FAILURE,
  State.SUCCESS
]
const aggStatus = computed(() => {
  for (const i in checkList) {
    const state = checkList[i]
    const index = props.status.indexOf(state)
    if (index > -1) {
      return { key: props.status.length - index, value: state }
    }
  }
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

const parseAgg = (agg: { count: number; status: string }) => {
  const status = new Status(agg.status)
  return Object.keys(TaskType)
    .map((key) => {
      const value = TaskType[key as keyof TaskTypeInterface]
      return { [value]: { [status.task_status[value]]: agg.count } }
    })
    .reduce((x, y) => ({ ...x, ...y }), {})
}

const customizer: (x: any, y: any) => any = (objValue: any, srcValue: any) => {
  if (objValue == undefined && srcValue) {
    return srcValue
  }
  if (srcValue == undefined && objValue) {
    return objValue
  }
  // 如果是数组，我们将元素进行聚合
  if (typeof objValue === 'object' && typeof srcValue === 'object') {
    // 若是object类型的对象，我们进行递归
    return mergeWith(objValue, srcValue, customizer)
  } else {
    // 否则，单纯的将值进行累加
    return objValue + srcValue
  }
}
const aggs = computed(() => {
  return (props.statusMeta.aggs ? props.statusMeta.aggs : [])
    .map((agg: any) => {
      return parseAgg(agg)
    })
    .reduce((x: any, y: any) => {
      return mergeWith(x, y, customizer)
    }, {})
})

const statusTable = computed(() => {
  return Object.keys(TaskType)
    .map((key) => {
      const value = TaskType[key as keyof TaskTypeInterface]
      const parseStatus = new Status(props.status)
      return {
        type: value,
        state: parseStatus.task_status[value],
        aggs: aggs.value[value],
        time: props.statusMeta.state_time[value]
      }
    })
    .filter((item) => item.state !== State.IGNORED)
})
</script>
<style lang="scss" scoped></style>
