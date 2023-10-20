<template>
  <LayoutContent header="团队管理">
    <div class="team-manage flex main-calc-height">
      <div class="team-member p-15 border-r">
        <h3>团队成员</h3>
        <div class="align-right">
          <el-button type="primary" link
            ><AppIcon iconName="app-add-users" class="add-user-icon" />添加成员</el-button
          >
        </div>
        <div class="mt-10">
          <el-input v-model="filterText" placeholder="请输入用户名搜索" suffix-icon="Search" />
        </div>
        <div class="member-list mt-10">
          <el-scrollbar>
            <ul>
              <template v-for="(item, index) in memberList" :key="index">
                <li class="active border-b-light flex-between p-15">
                  <div>
                    <span>{{ item.username }}</span>
                    <el-tag class="ml-10" effect="dark">所有者</el-tag>
                  </div>
                  <el-dropdown trigger="click">
                    <span class="cursor">
                      <el-icon><MoreFilled /></el-icon>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item>移除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </li>
              </template>
            </ul>
          </el-scrollbar>
        </div>
      </div>
      <div class="permission-setting flex">
        <div class="team-manage__table p-15">
          <h3>权限设置</h3>
          <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
            <el-tab-pane label="数据集" name="dataset">
              <el-table :data="tableData" :max-height="tableHeight">
                <el-table-column prop="date" label="数据集名称" />
                <el-table-column label="管理" align="center">
                  <template #header>
                    <el-checkbox v-model="allChecked" label="管理" />
                  </template>
                  <template #default="scope">
                    <el-checkbox v-model="scope.row.checked" />
                  </template>
                </el-table-column>
                <el-table-column label="使用" align="center">
                  <template #header>
                    <el-checkbox v-model="allChecked" label="使用" />
                  </template>
                  <template #default="scope">
                    <el-checkbox v-model="scope.row.checked" />
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="应用" name="application">应用</el-tab-pane>
          </el-tabs>
        </div>

        <div class="team-manage__footer border-t p-15 flex">
          <el-button type="primary">保存</el-button>
        </div>
      </div>
    </div>
  </LayoutContent>
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, nextTick } from 'vue'
import TeamApi from '@/api/team'
import type { TeamMember } from '@/api/type/team'

const loading = ref(false)
const memberList = ref<TeamMember[]>([])

const filterText = ref('')
const activeName = ref('dataset')
const allChecked = ref(false)
const tableHeight = ref(0)
function handleClick() {}

const tableData = [
  {
    date: '2016-05-03',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  },
  {
    date: '2016-05-02',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  },
  {
    date: '2016-05-04',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  },
  {
    date: '2016-05-01',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  },
  {
    date: '2016-05-08',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  },
  {
    date: '2016-05-06',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  },
  {
    date: '2016-05-07',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles'
  }
]

function getMember() {
  loading.value = true
  TeamApi.getTeamMember().then((res) => {
    memberList.value = res.data
    loading.value = false
  })
}

onMounted(() => {
  tableHeight.value = window.innerHeight - 300
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 300
    })()
  }
  getMember()
})
</script>

<style lang="scss" scoped>
.team-manage {
  .add-user-icon {
    margin-right: 5px;
    font-size: 20px;
  }
  .team-member {
    box-sizing: border-box;
    width: var(--team-manage-left-width);
    min-width: var(--team-manage-left-width);
    .member-list {
      li {
        &.active {
          background: var(--el-color-primary-light-9);
        }
      }
    }
  }
  .permission-setting {
    box-sizing: border-box;
    width: calc(100% - var(--team-manage-left-width) - 5px);
    flex-direction: column;
  }
  .team-manage__table {
    flex: 1;
  }
  .team-manage__footer {
    flex: 0 0 auto;
    justify-content: right;
  }
}
</style>
