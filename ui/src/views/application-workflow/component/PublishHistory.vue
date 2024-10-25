<template>
  <div class="workflow-publish-history border-l">
    <h4 class="border-b p-16-24">发布历史</h4>
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
                  <h5 :class="index === 0 ? 'primary' : ''" class="flex">
                    <ReadWrite
                      @change="editName($event, row)"
                      :data="row.name || datetimeFormat(row.update_time)"
                      trigger="manual"
                      :write="row.writeStatus"
                      @close="closeWrite(row)"
                    />
                    <el-tag v-if="index === 0" class="default-tag ml-4">最近发布</el-tag>
                  </h5>
                  <el-text type="info" class="color-secondary flex mt-8">
                    <AppAvatar :size="20" class="avatar-grey mr-4">
                      <el-icon><UserFilled /></el-icon>
                    </AppAvatar>
                    {{ row.publish_user_name }}
                  </el-text>
                </div>

                <div @click.stop v-show="mouseId === row.id">
                  <el-dropdown trigger="click" :teleported="false">
                    <el-button text>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click.stop="openEditVersion(row)">
                          <el-icon><EditPen /></el-icon>
                          编辑
                        </el-dropdown-item>
                        <el-dropdown-item @click="refreshVersion(row)">
                          <el-icon><RefreshLeft /></el-icon>
                          恢复此版本
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </template>

            <template #empty>
              <div class="text-center">
                <el-text type="info">暂无历史记录</el-text>
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
import applicationApi from '@/api/application'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgError } from '@/utils/message'
const route = useRoute()
const {
  params: { id }
} = route as any

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
      name: val
    }
    applicationApi.putWorkFlowVersion(id as string, item.id, obj, loading).then(() => {
      MsgSuccess('修改成功')
      item['writeStatus'] = false
      getList()
    })
  } else {
    MsgError('名字不能为空！')
  }
}

function getList() {
  applicationApi.getWorkFlowVersion(id, loading).then((res: any) => {
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
  background: #ffffff;
  height: calc(100vh - 57px);
  z-index: 9;
  .list-height {
    height: calc(100vh - 120px);
  }
}
</style>
