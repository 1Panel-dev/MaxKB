<template>
  <LayoutContent header="团队管理">
    <div class="team-manage flex main-calc-height">
      <div class="team-member p-15 border-r">
        <h3>团队成员</h3>
        <div class="align-right">
          <el-button type="primary" link @click="addMember">
            <AppIcon iconName="app-add-users" class="add-user-icon" />添加成员
          </el-button>
        </div>
        <div class="mt-10">
          <el-input v-model="filterText" placeholder="请输入用户名搜索" suffix-icon="Search" />
        </div>
        <div class="member-list mt-10" v-loading="loading">
          <el-scrollbar>
            <ul v-if="filterMember.length > 0">
              <template v-for="(item, index) in filterMember" :key="index">
                <li
                  @click.prevent="clickMemberHandle(item.id)"
                  :class="currentUser === item.id ? 'active' : ''"
                  class="border-b-light flex-between p-15 cursor"
                >
                  <div>
                    <span class="mr-10">{{ item.username }}</span>
                    <el-tag effect="dark" v-if="isManage(item.type)">所有者</el-tag>
                    <el-tag effect="dark" type="warning" v-else>用户</el-tag>
                  </div>
                  <el-dropdown trigger="click" v-if="!isManage(item.type)">
                    <span class="cursor">
                      <el-icon><MoreFilled /></el-icon>
                    </span>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item @click.prevent="deleteMember(item.id)"
                          >移除</el-dropdown-item
                        >
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </li>
              </template>
            </ul>
            <el-empty description="暂无数据" v-else />
          </el-scrollbar>
        </div>
      </div>
      <div class="permission-setting flex" v-loading="rLoading">
        <div class="team-manage__table p-15">
          <h3>权限设置</h3>
          <el-tabs v-model="activeName" class="demo-tabs">
            <el-tab-pane
              v-for="item in settingTags"
              :key="item.value"
              :label="item.label"
              :name="item.value"
            >
              <PermissionSetting :data="item.data"></PermissionSetting>
            </el-tab-pane>
            <!-- <el-tab-pane label="应用" name="application">应用</el-tab-pane> -->
          </el-tabs>
        </div>

        <div class="team-manage__footer border-t p-15 flex">
          <el-button type="primary">保存</el-button>
        </div>
      </div>
    </div>
    <CreateMemberDialog ref="CreateMemberRef" @refresh="refresh" />
  </LayoutContent>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import TeamApi from '@/api/team'
import type { TeamMember } from '@/api/type/team'
import CreateMemberDialog from './component/CreateMemberDialog.vue'
import PermissionSetting from './component/PermissionSetting.vue'
import { MsgSuccess } from '@/utils/message'
import { timePanelSharedProps } from 'element-plus/es/components/time-picker/src/props/shared'

const DATASET = 'DATASET'

const CreateMemberRef = ref<InstanceType<typeof CreateMemberDialog>>()
const loading = ref(false)
const rLoading = ref(false)
const memberList = ref<TeamMember[]>([]) // 全部成员
const filterMember = ref<TeamMember[]>([]) // 搜索过滤后列表
const currentUser = ref<String>('')
const filterText = ref('')

const activeName = ref(DATASET)

const settingTags = reactive([
  {
    label: '数据集',
    value: DATASET,
    data: [] as any
  }
  // {
  //   label: '应用',
  //   value: 'application',
  //   data: []
  // }
])

watch(filterText, (val) => {
  if (val) {
    filterMember.value = memberList.value.filter((v) => v.username.includes(val))
  } else {
    filterMember.value = memberList.value
  }
})

function MemberPermissions(id: String) {
  rLoading.value = true
  TeamApi.getMemberPermissions(id)
    .then((res) => {
      if (!res.data || Object.keys(res.data).length > 0) {
        settingTags.map((item) => {
          if (Object.keys(res.data).indexOf(item.value) !== -1) {
            item.data = res.data[item.value]
          }
        })
      }
      // if (!res.data || Object.keys(res.data).length == 0) {
      //   permissionsData.value = []
      // } else {
      //   permissionsData.value = res.data
      // }

      rLoading.value = false
    })
    .catch(() => {
      rLoading.value = false
    })
}

function deleteMember(id: String) {
  loading.value = true
  TeamApi.delTeamMember(id)
    .then(() => {
      MsgSuccess('删除成功')
      getMember()
    })
    .catch(() => {
      loading.value = false
    })
}

function isManage(type: String) {
  return type === 'manage'
}

function clickMemberHandle(id: String) {
  currentUser.value = id
  MemberPermissions(id)
}
function addMember() {
  CreateMemberRef.value?.open()
}

function getMember() {
  loading.value = true
  TeamApi.getTeamMember()
    .then((res) => {
      memberList.value = res.data
      filterMember.value = res.data
      currentUser.value = memberList.value[0].id
      MemberPermissions(currentUser.value)
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function refresh() {
  getMember()
}

onMounted(() => {
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
