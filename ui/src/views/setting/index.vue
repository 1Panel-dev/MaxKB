<template>
  <div>团队管理</div>

  <!-- <div class="sales-department__tree">
        <support-tree
          ref="salesDepartmentTree"
          v-model:data="dataSource"
          :title="`飞致云 ${regionName}`"
          buttonName="新建部门"
          :beforeAppend="appendDepartment"
          :beforeRemove="removedDepartment"
          :beforeEdit="editDepartment"
          :filterable="true"
          :highlight-current="true"
          node-key="id"
          :props="defaultProps"
          @node-click="treeClick"
        />
      </div>
      <div class="sales-department__table">
        <complex-table v-if="currentDepartment" :data="memberTable" border>
          <template #toolbar>
            <div class="table-header">
              <h3>{{ currentDepartment?.name }}</h3>
              <div>
                <el-button type="primary" @click="addMember">设置人员</el-button>
              </div>
            </div>
          </template>
          <el-table-column label="账户ID" prop="username" show-overflow-tooltip />
          <el-table-column label="姓名">
            <template #default="{ row }">
              <icon
                icon="iconfont icon-vip"
                v-if="currentDepartment?.leaderId === row.userId"
                style="color: #f8bc2e"
              ></icon>
              {{ row.name }}
            </template>
          </el-table-column>
          <el-table-column label="手机号" prop="phone" />
          <el-table-column label="邮箱" prop="email" show-overflow-tooltip />
          <el-table-column label="角色">
            <template #default="{ row }">
              {{ currentDepartment?.leaderId === row.userId ? '销售主管' : '销售' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                v-if="currentDepartment?.leaderId !== row.userId"
                @click="setLeader(row)"
                >升级</el-button
              >
            </template>
          </el-table-column>
        </complex-table>
        <el-empty :image-size="200" v-else />
      </div> -->
  <!-- 设置部门
      <department-dialog ref="departmentDialogRef" :title="dialogTitle" @refresh="refresh" />
      <member-dialog ref="memberDialogRef" @refresh="refresh" /> -->
</template>

<script lang="ts" setup>
import { onMounted, ref, watch, nextTick } from 'vue'
// import DepartmentDialog from './components/DepartmentDialog.vue'
// import MemberDialog from './components/MemberDialog.vue'
// import { getSalesTeams, deleteSalesTeams, putSetLeader } from '@/api/sales-team-controller'
// import { searchiInTree } from '@/utils/utils'
// import { $error, $confirm, $success } from '@/utils/message'

// import useStore from '@/store'
// const { user } = useStore()

// const defaultProps = {
//   children: 'subTeams'
// }

// const salesDepartmentTree = ref()
// const memberDialogRef = ref()
// const departmentDialogRef = ref()
// const loading = ref(false)

// const regionName = ref('')
// const dialogTitle = ref('')
// const dataSource = ref([])
// const salesOptions = ref([])
// const currentDepartment = ref(null)
// const memberTable = ref([])

// watch([salesOptions, currentDepartment], (val) => {
//   if (val[0]?.length && val[1]) {
//     const leader = val[0].filter((item) => item.userId === val[1]?.leaderId)
//     const member = val[1]?.teamMember
//       ? val[0].filter((item) => val[1]?.teamMember.includes(item.userId))
//       : []
//     memberTable.value = [...leader, ...member]
//   }
// })

// function addMember() {
//   memberDialogRef.value.open(currentDepartment.value)
// }

// const appendDepartment = (data) => {
//   dialogTitle.value = '新建部门'
//   departmentDialogRef.value.open('create', data)
//   return false
// }

// const removedDepartment = (node, data) => {
//   $confirm('确定要删除这个部门吗?', {
//     confirmButtonText: '确定',
//     cancelButtonText: '取消',
//     type: 'warning'
//   })
//     .then(() => {
//       loading.value = true
//       deleteSalesTeams(data.id)
//         .then(() => {
//           $success('删除成功')
//           getTeams()
//         })
//         .catch(() => {
//           loading.value = false
//         })
//     })
//     .catch(() => {})

//   return false
// }

// const editDepartment = (node) => {
//   dialogTitle.value = '编辑部门'
//   const parent = node.isLeaf ? node.parent.data : null
//   departmentDialogRef.value.open('edit', node.data, parent)
//   return false
// }

// function setLeader(row) {
//   loading.value = true
//   putSetLeader(currentDepartment.value.id, row.userId)
//     .then((data) => {
//       getTeams()
//     })
//     .catch(() => {
//       loading.value = false
//     })
// }

// function treeClick(node) {
//   currentDepartment.value = node
// }

// function getTeams() {
//   loading.value = true
//   getSalesTeams({ includeUsers: true })
//     .then((data) => {
//       dataSource.value = data
//       currentDepartment.value = currentDepartment.value
//         ? searchiInTree(dataSource.value, currentDepartment.value, 'subTeams')
//         : dataSource.value?.length && dataSource.value[0]
//       nextTick(() => {
//         salesDepartmentTree.value.setCurrentKey(currentDepartment.value?.id)
//       })

//       loading.value = false
//     })
//     .catch(() => {
//       loading.value = false
//     })
// }

// function getSalesList() {
//   loading.value = true
//   user
//     .asyncGetInternalUsers({ group: ['sales', 'sales_leader', 'region_sales_admin'] })
//     .then((res) => {
//       salesOptions.value = res
//       loading.value = false
//     })
//     .catch(() => {
//       loading.value = false
//     })
// }

// function getInfo() {
//   loading.value = true
//   user
//     .asyncGetUserInfo()
//     .then((data) => {
//       regionName.value = data?.region?.name ? `- ${data?.region?.name}` : ''
//       loading.value = false
//     })
//     .catch(() => {
//       loading.value = false
//     })
// }

// function refresh() {
//   getTeams()
// }

onMounted(() => {
  // getSalesList()
  // getInfo()
  // getTeams()
})
</script>

<style lang="scss" scoped>
$department-left-width: 300px;

.sales-department {
  &__tree {
    width: $department-left-width;
    min-width: $department-left-width;
    padding-right: 20px;
    box-sizing: content-box;
  }
  &__table {
    border-left: 1px solid var(--el-border-color);
    width: calc(100% - $department-left-width - 40px);
    padding-left: 20px;
    .table-header {
      h3 {
        font-size: 18px;
      }
    }
  }
}
</style>
