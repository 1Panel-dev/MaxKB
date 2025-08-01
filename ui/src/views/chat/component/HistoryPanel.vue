<template>
  <div class="history-component h-full">
    <el-menu
      :default-active="currentChatId"
      :collapse="isPcCollapse"
      collapse-transition
      popper-class="chat-pc-popper"
      class="h-full"
    >
      <div style="padding: 16px 18px 0 18px">
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
          <h4
            v-show="!isPcCollapse"
            :style="{ color: applicationDetail?.custom_theme?.header_font_color }"
          >
            {{ applicationDetail?.name }}
          </h4>
        </div>
        <el-button
          type="primary"
          plain
          v-show="!isPcCollapse"
          class="add-button primary medium w-full"
          @click="newChat"
        >
          <AppIcon iconName="app-create-chat"></AppIcon>
          <span class="ml-4">{{ $t('chat.createChat') }}</span>
        </el-button>
        <div v-show="!isPcCollapse" class="flex-between p-8 pb-0 color-secondary mt-8">
          <span>{{ $t('chat.history') }}</span>
          <el-tooltip effect="dark" :content="$t('chat.clearChat')" placement="right">
            <el-button text @click.stop="clearChat">
              <AppIcon iconName="app-delete"></AppIcon>
            </el-button>
          </el-tooltip>
        </div>
      </div>
      <div v-show="!isPcCollapse" class="left-height">
        <el-scrollbar>
          <div class="p-16 pt-0">
            <common-list
              :data="chatLogData"
              class="mt-8"
              v-loading="leftLoading"
              :defaultActive="currentChatId"
              @click="handleClickList"
              @mouseenter="mouseenter"
              @mouseleave="mouseId = ''"
            >
              <template #default="{ row }">
                <div class="flex-between">
                  <span :title="row.abstract" class="ellipsis" style="max-width: 180px">
                    {{ row.abstract }}
                  </span>
                  <div @click.stop v-show="mouseId === row.id && row.id !== 'new'">
                    <el-dropdown trigger="click" :teleported="false">
                      <el-button text>
                        <AppIcon iconName="app-more"></AppIcon>
                      </el-button>

                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click.stop="editLogTitle(row)">
                            <AppIcon iconName="app-edit"></AppIcon>
                            {{ $t('common.edit') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click.stop="deleteChatLog(row)">
                            <AppIcon iconName="app-delete"></AppIcon>
                            {{ $t('common.delete') }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </template>

              <template #empty>
                <div class="text-center">
                  <el-text type="info">{{ $t('chat.noHistory') }}</el-text>
                </div>
              </template>
            </common-list>
          </div>
          <div v-if="chatLogData?.length" class="text-center lighter color-secondary">
            <span>{{ $t('chat.only20history') }}</span>
          </div>
        </el-scrollbar>
      </div>
      <el-menu-item index="1" v-show="isPcCollapse" @click="newChat">
        <AppIcon iconName="app-create-chat"></AppIcon>
        <template #title>{{ $t('chat.createChat') }}</template>
      </el-menu-item>

      <el-sub-menu v-show="isPcCollapse" index="2">
        <template #title>
          <AppIcon iconName="app-history-outlined" />
        </template>
        <el-menu-item-group v-loading="leftLoading">
          <template #title>
            <div class="flex-between w-full">
              <span>{{ $t('chat.history') }}</span>
              <el-tooltip effect="dark" :content="$t('chat.clearChat')" placement="right">
                <el-button text @click.stop="clearChat">
                  <AppIcon iconName="app-delete"></AppIcon>
                </el-button>
              </el-tooltip>
            </div>
          </template>
          <el-menu-item
            v-for="row in chatLogData"
            :index="row.id"
            :key="row.id"
            @click="handleClickList(row)"
            @mouseenter="mouseenter(row)"
            @mouseleave="mouseId = ''"
          >
            <div class="flex-between w-full lighter">
              <span :title="row.abstract" class="ellipsis">
                {{ row.abstract }}
              </span>
              <div @click.stop class="flex" v-show="mouseId === row.id && row.id !== 'new'">
                <el-dropdown trigger="click" :teleported="false">
                  <AppIcon iconName="app-more" class="mt-4 lighter"></AppIcon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click.stop="editLogTitle(row)">
                        <AppIcon iconName="app-edit"></AppIcon>
                        {{ $t('common.edit') }}
                      </el-dropdown-item>
                      <el-dropdown-item @click.stop="deleteChatLog(row)">
                        <AppIcon iconName="app-delete"></AppIcon>
                        {{ $t('common.delete') }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-menu-item>
        </el-menu-item-group>
        <div v-if="!chatLogData?.length" class="text-center">
          <el-text type="info">{{ $t('chat.noHistory') }}</el-text>
        </div>
      </el-sub-menu>
    </el-menu>
    <slot></slot>
    <EditTitleDialog ref="EditTitleDialogRef" @refresh="refreshFieldTitle" />
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { isAppIcon } from '@/utils/common'
import EditTitleDialog from './EditTitleDialog.vue'
const props = defineProps<{
  applicationDetail: any
  chatLogData: any[]
  leftLoading?: boolean
  currentChatId: string
  isPcCollapse?: boolean
}>()
const emit = defineEmits(['newChat', 'clickLog', 'deleteLog', 'refreshFieldTitle', 'clearChat'])

const EditTitleDialogRef = ref()

const mouseId = ref('')

function mouseenter(row: any) {
  mouseId.value = row.id
}
const newChat = () => {
  emit('newChat')
}

const handleClickList = (item: any) => {
  emit('clickLog', item)
}

const deleteChatLog = (row: any) => {
  emit('deleteLog', row)
}

const clearChat = () => {
  emit('clearChat')
}

function editLogTitle(row: any) {
  EditTitleDialogRef.value.open(row, props.applicationDetail.id)
}

function refreshFieldTitle(chatId: string, abstract: string) {
  emit('refreshFieldTitle', chatId, abstract)
}
</script>
<style lang="scss" scoped>
.history-component {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--el-menu-border-color);
  background: var(--el-color-primary-light-06) !important;
  :deep(.el-menu) {
    background: none;
    border: none;
    &:not(.el-menu--collapse) {
      width: 280px;
    }
    &.el-menu--collapse {
      .el-sub-menu.is-active .el-sub-menu__title {
        color: var(--el-text-color-primary) !important;
      }
    }
    .el-sub-menu__title:hover {
      background-color: var(--el-color-primary-light-9) !important;
    }
  }

  .left-height {
    height: calc(100vh - 210px);
  }

  :deep(.common-list li.active) {
    background-color: #ffffff;
    font-weight: 500;
    color: var(--el-text-color-primary);
    &:hover {
      background-color: #ffffff;
    }
  }

  .add-button {
    border: 1px solid var(--el-color-primary-light-6);
    background-color: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }
}
</style>
<style lang="scss">
.chat-pc-popper {
  background: #ffffff !important;
  .el-menu {
    background: var(--el-color-primary-light-06) !important;
  }
  .el-menu-item-group__title {
    padding: 8px 8px 8px 16px;
    font-weight: 500;
    color: var(--app-text-color-secondary);
  }
  .el-menu-item {
    border-radius: 6px;
    height: 40px;
    margin: 0 8px;
    padding-left: 8px;
    padding-right: 8px;
    &:hover {
      background-color: rgba(31, 35, 41, 0.1);
    }
    &.is-active {
      background-color: #ffffff;
      color: var(--el-text-color-primary);
      // & > div {
      //   font-weight: 500;
      // }
    }
  }
}
</style>
