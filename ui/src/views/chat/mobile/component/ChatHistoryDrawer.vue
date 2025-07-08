<template>
  <div>
    <el-drawer v-model="show" :with-header="false" class="left-drawer" direction="ltr" :size="280">
      <div>
        <div class="flex align-center mb-16">
          <div class="flex mr-8">
            <el-avatar
              v-if="isAppIcon(applicationDetail?.icon)"
              shape="square"
              :size="32"
              style="background: none"
            >
              <img :src="applicationDetail?.icon" alt="" />
            </el-avatar>
            <LogoIcon v-else height="32px" />
          </div>
          <h4>{{ applicationDetail?.name }}</h4>
        </div>
        <el-button size="large" class="add-button w-full primary" @click="emit('newChat')">
          <AppIcon iconName="app-create-chat"></AppIcon>
          <span class="ml-4">{{ $t('chat.createChat') }}</span>
        </el-button>
        <p class="mt-20 mb-8 color-secondary">{{ $t('chat.history') }}</p>
      </div>

      <div class="left-height pt-0">
        <el-scrollbar>
          <div>
            <common-list
              :style="{ '--el-color-primary': applicationDetail?.custom_theme?.theme_color }"
              :data="chatLogData"
              v-loading="leftLoading"
              :defaultActive="currentChatId"
              @click="handleClickList"
              @mouseenter="mouseenter"
              @mouseleave="mouseId = ''"
            >
              <template #default="{ row }">
                <div class="flex-between">
                  <ReadWrite
                    @change="(val: string) => updateChatName(val, row)"
                    :data="row.abstract"
                    trigger="manual"
                    :write="row.writeStatus"
                    @close="() => (row.writeStatus = false)"
                    :maxlength="1024"
                  />
                  <div
                    @click.stop
                    v-if="mouseId === row.id && row.id !== 'new' && !row.writeStatus"
                    class="flex"
                  >
                    <el-button style="padding: 0" link @click.stop="() => (row.writeStatus = true)">
                      <el-icon>
                        <EditPen />
                      </el-icon>
                    </el-button>
                    <el-button style="padding: 0" link @click.stop="() => deleteChatLog(row)">
                      <el-icon>
                        <Delete />
                      </el-icon>
                    </el-button>
                  </div>
                </div>
              </template>
              <template #empty>
                <div class="text-center mt-24">
                  <el-text type="info">{{ $t('chat.noHistory') }}</el-text>
                </div>
              </template>
            </common-list>
          </div>
          <div v-if="chatLogData.length" class="gradient-divider lighter mt-8">
            <span>{{ $t('chat.only20history') }}</span>
          </div>
        </el-scrollbar>
      </div>
      <div class="flex align-center user-info" @click="toUserCenter">
        <el-avatar
          :size="32"
          :class="`${!chatUser.chat_profile?.authentication || chatUser.chat_profile.authentication_type === 'password' ? 'cursor-default' : ''}`"
        >
          <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
        </el-avatar>
        <span v-if="chatUser.chat_profile?.authentication" class="ml-8 color-text-primary">
          {{ chatUser.chatUserProfile?.nick_name }}
        </span>
      </div>
    </el-drawer>

    <UserCenter v-model:show="userCenterDrawerShow" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineModel } from 'vue'
import { isAppIcon } from '@/utils/common'
import { t } from '@/locales'
import { Delete, EditPen } from '@element-plus/icons-vue'
import useStore from '@/stores'
import { MsgError } from '@/utils/message'
import UserCenter from './UserCenter.vue'

const show = defineModel<boolean>('show')

const props = defineProps<{
  applicationDetail: any
  chatLogData: any[]
  leftLoading: boolean
  currentChatId: string
}>()

const emit = defineEmits(['newChat', 'clickLog', 'deleteLog'])

const { chatUser, chatLog } = useStore()

const handleClickList = (item: any) => {
  emit('clickLog', item)
}

const updateChatName = (val: string, item: any) => {
  if (!val) return MsgError(t('views.applicationWorkflow.tip.nameMessage'))
  const obj = { abstract: val }
  chatLog.asyncPutChatClientLog(props.applicationDetail.id, item.id, obj, ref(false)).then(() => {
    item.abstract = val
    item.writeStatus = false
  })
}

const deleteChatLog = (row: any) => {
  emit('deleteLog', row)
}

const mouseId = ref('')
const mouseenter = (row: any) => {
  mouseId.value = row.id
}

const userCenterDrawerShow = ref(false)
function toUserCenter() {
  if (
    !chatUser.chat_profile?.authentication ||
    chatUser.chat_profile.authentication_type === 'password'
  )
    return
  userCenterDrawerShow.value = true
}
</script>

<style lang="scss" scoped>
:deep(.left-drawer) {
  .el-drawer__body {
    padding: 16px;
    background:
      linear-gradient(187.61deg, rgba(235, 241, 255, 0.5) 39.6%, rgba(231, 249, 255, 0.5) 94.3%),
      #eef1f4;
    overflow: hidden;

    // .add-button {
    //   border: 1px solid var(--el-color-primary);
    //   color: var(--el-color-primary);
    //   font-weight: 500;
    // }

    .left-height {
      height: calc(100vh - 212px);
    }

    .common-list li.active {
      background-color: #ffffff;
      font-weight: 500;
      color: var(--el-text-color-primary);
      &:hover {
        background-color: #ffffff;
      }
    }

    .user-info {
      border-radius: 6px;
      padding: 4px 8px;
      margin-top: 16px;
      box-sizing: border-box;
    }
  }

  .cursor-default {
    cursor: default;
  }
}

.gradient-divider {
  position: relative;
  text-align: center;
  color: var(--el-color-info);

  ::before {
    content: '';
    width: 17%;
    height: 1px;
    background: linear-gradient(90deg, rgba(222, 224, 227, 0) 0%, #dee0e3 100%);
    position: absolute;
    left: 16px;
    top: 50%;
  }

  ::after {
    content: '';
    width: 17%;
    height: 1px;
    background: linear-gradient(90deg, #dee0e3 0%, rgba(222, 224, 227, 0) 100%);
    position: absolute;
    right: 16px;
    top: 50%;
  }
}
</style>
