<template>
  <el-drawer v-model="drawer" title="执行记录" direction="rtl" size="800px" :before-close="close">
    <el-table v-if="active == 'list'" :data="data" style="width: 100%">
      <el-table-column prop="meta" label="发起人" width="180">
        <template #default="{ row }">
          {{ row.meta.user_name }}
        </template>
      </el-table-column>
      <el-table-column prop="sate" label="状态" width="180">
        <template #default="{ row }">
          {{ row.state }}
        </template>
      </el-table-column>
      <el-table-column prop="run_time" label="运行时间">
        <template #default="{ row }">
          {{ row.run_time }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <span @click="details(row)">执行详情</span>
        </template>
      </el-table-column>
    </el-table>
    <Result
      v-if="active == 'details'"
      :id="active_action_id"
      :knowledge_id="active_knowledge_id"
    ></Result>
  </el-drawer>
</template>
<script setup lang="ts">
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { computed, ref, reactive } from 'vue'
import Result from '../action/Result.vue'
import { useRoute, useRouter } from 'vue-router'
const drawer = ref<boolean>(false)
const active_knowledge_id = ref<string>()
const active_action_id = ref<string>()
const active = ref<'list' | 'details'>('list')
const route = useRoute()
const details = (row: any) => {
  active_action_id.value = row.id
  active.value = 'details'
}

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0,
})
const query = ref<any>({
  user_name: '',
})
const data = ref<Array<any>>([])
const page = () => {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .pageWorkflowAction(active_knowledge_id.value, paginationConfig, query)
    .then((ok: any) => {
      paginationConfig.total = ok.data?.total
      data.value = ok.data.records
    })
}
const open = (knowledge_id: string) => {
  drawer.value = true
  active_knowledge_id.value = knowledge_id
  page()
}
const close = () => {
  drawer.value = false
}
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
