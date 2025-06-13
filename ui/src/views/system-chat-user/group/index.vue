<template>
  <div class="group-manage p-16-24">
    <h4 class="mb-16">{{ $t('views.system.group.title') }}</h4>

    <div class="flex main-calc-height">
      <div class="group-member p-8 border-r">
        <div class="flex-between p-16">
          <h4>{{ $t('views.system.group.member') }}</h4>
          <el-button type="primary" link @click="addMember">
            <AppIcon iconName="app-add-users" class="add-user-icon" />
          </el-button>
        </div>
        <div class="group-member-input">
          <el-input
            v-model="filterText"
            :placeholder="$t('views.system.group.searchBar.placeholder')"
            prefix-icon="Search"
            clearable
          />
        </div>
        <div class="list-height-left">
          <el-scrollbar>
            <common-list
              :data="filterGroup"
              class="mt-8"
              v-loading="loading"
              @click="clickMemberHandle"
              :default-active="currentUser"
            >
              <template #default="{ row }">
                <div class="flex-between">
                  <div>
                    <span class="mr-8">{{ row.username }}</span>
                  </div>
                  <div @click.stop style="margin-top: 5px">
                    <el-dropdown trigger="click" v-if="!isManage(row.type)">
                      <span class="cursor">
                        <el-icon class="rotate-90"><MoreFilled /></el-icon>
                      </span>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- <el-dropdown-item @click.prevent="deleteMember(row)">{{
                            $t('views.system.group.delete.button')
                          }}</el-dropdown-item> -->
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </template>
            </common-list>
          </el-scrollbar>
        </div>
      </div>
      <div class="permission-setting flex" v-loading="rLoading">
        <div class="group-manage__table">
          <h4 class="p-24 pb-0 mb-4">{{ $t('views.system.group.permissionSetting') }}</h4>
        </div>
      </div>
    </div>
    <CreateGroupDialog ref="CreateGroupRef" @refresh="refresh" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import GroupApi from '@/api/system/user-group'
import CreateGroupDialog from './component/CreateGroupDialog.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
const CreateGroupRef = ref<InstanceType<typeof CreateGroupDialog>>()
const loading = ref(false)
const rLoading = ref(false)
const groupList = ref([]) // 全部成员
const filterGroup = ref([]) // 搜索过滤后列表
const currentUser = ref<String>('')
const currentType = ref<String>('')

const filterText = ref('')

const tableHeight = ref(0)

watch(filterText, (val) => {
  if (val) {
    // filterGroup.value = groupList.value.filter((v) =>
    //   v.name.toLowerCase().includes(val.toLowerCase()),
    // )
  } else {
    filterGroup.value = groupList.value
  }
})

function isManage(type: String) {
  return type === 'manage'
}

function clickMemberHandle(item: any) {
  currentUser.value = item.id
  currentType.value = item.type
}
function addMember() {
  CreateGroupRef.value?.open()
}

function getMember(id?: string) {
  loading.value = true
}

function refresh(data?: string[]) {}

onMounted(() => {})
</script>

<style lang="scss" scoped>
.group-manage {
}
</style>
