<template>
  <LayoutContainer header="团队管理">
    <div class="team-manage flex main-calc-height">
      <div class="team-member p-8 border-r">
        <div class="flex-between p-16">
          <h4>成员</h4>
          <el-button type="primary" link @click="addMember">
            <AppIcon iconName="app-add-users" class="add-user-icon" />
          </el-button>
        </div>
        <div class="team-member-input">
          <el-input v-model="filterText" placeholder="请输入用户名搜索" prefix-icon="Search" />
        </div>
        <div class="member-list mt-8" v-loading="loading">
          <el-scrollbar>
            <ul v-if="filterMember.length > 0">
              <template v-for="(item, index) in filterMember" :key="index">
                <li
                  @click.prevent="clickMemberHandle(item.id)"
                  :class="currentUser === item.id ? 'active' : ''"
                  class="flex-between cursor"
                >
                  <div>
                    <span class="mr-8">{{ item.username }}</span>
                    <el-tag v-if="isManage(item.type)" class="default-tag">所有者</el-tag>
                    <el-tag type="warning" v-else>用户</el-tag>
                  </div>
                  <span @click.stop>
                    <el-dropdown trigger="click" v-if="!isManage(item.type)">
                      <span class="cursor">
                        <el-icon><MoreFilled /></el-icon>
                      </span>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click.prevent="deleteMember(item)"
                            >移除</el-dropdown-item
                          >
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </span>
                </li>
              </template>
            </ul>
            <el-empty description="暂无数据" v-else />
          </el-scrollbar>
        </div>
      </div>
      <div class="permission-setting flex" v-loading="rLoading">
        <div class="team-manage__table p-24">
          <h4>权限设置</h4>
          <el-tabs v-model="activeName" class="team-manage__tabs">
            <el-tab-pane
              v-for="item in settingTags"
              :key="item.value"
              :label="item.label"
              :name="item.value"
            >
              <PermissionSetting :data="item.data"></PermissionSetting>
            </el-tab-pane>
          </el-tabs>
        </div>

        <div class="team-manage__footer border-t p-16 flex">
          <el-button type="primary" @click="submitPermissions">保存</el-button>
        </div>
      </div>
    </div>
    <CreateMemberDialog ref="CreateMemberRef" @refresh="refresh" />
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import TeamApi from '@/api/team'
import type { TeamMember } from '@/api/type/team'
import CreateMemberDialog from './component/CreateMemberDialog.vue'
import PermissionSetting from './component/PermissionSetting.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'

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
  },
  {
    label: '应用',
    value: 'application',
    data: [] as any
  }
])

watch(filterText, (val) => {
  if (val) {
    filterMember.value = memberList.value.filter((v) => v.username.includes(val))
  } else {
    filterMember.value = memberList.value
  }
})

function submitPermissions() {
  rLoading.value = true
  const obj: any = {
    team_member_permission_list: []
  }
  settingTags.map((item) => {
    item.data.map((v: any) => {
      obj['team_member_permission_list'].push({
        target_id: v.id,
        type: v.type,
        operate: v.operate
      })
    })
  })
  TeamApi.putMemberPermissions(currentUser.value, obj)
    .then(() => {
      MsgSuccess('提交成功')
      MemberPermissions(currentUser.value)
    })
    .catch(() => {
      rLoading.value = false
    })
}

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
      rLoading.value = false
    })
    .catch(() => {
      rLoading.value = false
    })
}

function deleteMember(row: TeamMember) {
  MsgConfirm(
    {
      title: `是否移除成员：${row.username}`,
      decription: '移除后将会取消成员拥有的数据集和应用权限。',
      confirmButtonText: '移除'
    },
    {
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      TeamApi.delTeamMember(row.id)
        .then(() => {
          MsgSuccess('删除成功')
          getMember()
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
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
    font-size: 17px;
  }
  .team-member-input {
    padding: 0 16px;
  }
  .team-member {
    box-sizing: border-box;
    width: var(--team-manage-left-width);
    min-width: var(--team-manage-left-width);
    .member-list {
      li {
        padding: 11px 16px;
        &.active {
          background: var(--el-color-primary-light-9);
          border-radius: 4px;
          color: var(--el-color-primary);
        }
      }
    }
  }

  .permission-setting {
    box-sizing: border-box;
    width: calc(100% - var(--team-manage-left-width) - 5px);
    flex-direction: column;
  }

  &__tabs {
    margin-top: 10px;
  }
  &__table {
    flex: 1;
  }
  &__footer {
    flex: 0 0 auto;
    justify-content: right;
  }
}
</style>
