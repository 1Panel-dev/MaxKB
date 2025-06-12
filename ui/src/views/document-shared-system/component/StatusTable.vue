<template>
  <div v-for="status in statusTable" :key="status.type" >
    <span> {{ taskTypeMap[status.type] }}：</span>
    <span>
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
      <el-text v-else-if="status.state === State.REVOKE">
        <el-icon class="is-loading primary"><Loading /></el-icon>
        {{ stateMap[status.state](status.type) }}
      </el-text>
    </span>
    <span
      class="ml-8 lighter"
      :style="{ color: [State.FAILURE, State.REVOKED].includes(status.state) ? '#F54A45' : '' }"
    >
    {{ $t('views.document.fileStatus.finish') }}
      {{
        Object.keys(status.aggs ? status.aggs : {})
          .filter((k) => k == State.SUCCESS)
          .map((k) => status.aggs[k])
          .reduce((x: any, y: any) => x + y, 0)
      }}/{{
        Object.values(status.aggs ? status.aggs : {}).reduce((x: any, y: any) => x + y, 0)
      }}</span
    >
    <el-text type="info" class="ml-12">
      {{
        status.time
          ? status.time[status.state == State.REVOKED ? State.REVOKED : State.PENDING]?.substring(
              0,
              19
            )
          : undefined
      }}
    </el-text>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { Status, TaskType, State, type TaskTypeInterface } from '@/utils/status'
import { mergeWith } from 'lodash'
const props = defineProps<{ status: string; statusMeta: any; stateMap: any; taskTypeMap: any }>()

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
<style lang="scss"></style>
