<template>
  <div class="breadcrumb ml-4 mt-4 mb-12 flex">
    <back-button :to="activeMenu" class="mt-4"></back-button>
    <div class="flex align-center">
      <el-avatar
        v-if="isApplication && isAppIcon(current?.icon)"
        shape="square"
        :size="24"
        style="background: none"
        class="mr-8"
      >
        <img :src="current?.icon" alt="" />
      </el-avatar>
      <LogoIcon
        v-else-if="isApplication"
        height="28px"
        style="width: 28px; height: 28px; display: block"
        class="mr-8"
      />
      <KnowledgeIcon v-else-if="isKnowledge" :type="current?.type" class="mr-8" />

      <div class="ellipsis" :title="current?.name">{{ current?.name }}</div>
    </div>
    <!-- <el-dropdown
      placement="bottom"
      trigger="click"
      @command="changeMenu"
      class="w-full"
      style="display: block"
    >
      <div class="breadcrumb-hover flex-between cursor">
        <div class="flex align-center">
          <el-avatar
            v-if="isApplication && isAppIcon(current?.icon)"
            shape="square"
            :size="24"
            style="background: none"
            class="mr-8"
          >
            <img :src="current?.icon" alt="" />
          </el-avatar>
          <LogoIcon
            v-else-if="isApplication"
            height="28px"
            style="width: 28px; height: 28px; display: block"
          />
          <KnowledgeIcon v-else-if="isKnowledge" :type="current?.type" />

          <div class="ellipsis" :title="current?.name">{{ current?.name }}</div>
        </div>

        <el-button text>
          <el-icon><CaretBottom /></el-icon>
        </el-button>
      </div>
      <template #dropdown>
        <el-scrollbar>
          <div style="max-height: 400px">
            <el-dropdown-menu>
              <template v-for="(item, index) in list" :key="index">
                <div :class="item.id === id ? 'dropdown-active' : ''">
                  <el-dropdown-item :command="item.id">
                    <div class="flex align-center">
                      <el-avatar
                        v-if="isApplication && isAppIcon(item?.icon)"
                        shape="square"
                        :size="24"
                        style="background: none"
                        class="mr-8"
                      >
                        <img :src="item?.icon" alt="" />
                      </el-avatar>

                      <el-avatar
                        v-else-if="isApplication"
                        :name="item.name"
                        pinyinColor
                        class="mr-12"
                        shape="square"
                        :size="24"
                      />

                      <KnowledgeIcon v-if="isKnowledge" :type="item.type" />

                      <span class="ellipsis" :title="item?.name"> {{ item?.name }}</span>
                    </div>
                  </el-dropdown-item>
                </div>
              </template>
            </el-dropdown-menu>
          </div>
        </el-scrollbar>
        <div class="breadcrumb__footer border-t" style="padding: 8px 11px; min-width: 200px">
          <template v-if="isApplication">
            <div class="w-full text-left cursor" @click="openCreateDialog">
              <el-button link>
                <el-icon class="mr-4"><Plus /></el-icon>
                {{ $t('views.application.createApplication') }}
              </el-button>
            </div>
          </template>
          <template v-else-if="isKnowledge">
            <div class="w-full text-left cursor" @click="openCreateDialog">
              <el-button link>
                <el-icon class="mr-4"><Plus /></el-icon> {{ $t('views.knowledge.createKnowledge') }}
              </el-button>
            </div>
          </template>
        </div>
      </template>
    </el-dropdown> -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { onBeforeRouteLeave, useRouter, useRoute } from 'vue-router'
import { isAppIcon } from '@/utils/common'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

import useStore from '@/stores'
const { common, application } = useStore()
const route = useRoute()

const {
  meta: { activeMenu },
  params: { id },
} = route as any

const type = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

onBeforeRouteLeave((to, from) => {
  common.saveBreadcrumb(null)
})

const loading = ref(false)

const current = ref<any>(null)

const isApplication = computed(() => {
  return activeMenu.includes('application')
})
const isKnowledge = computed(() => {
  return activeMenu.includes('knowledge')
})

function getKnowledgeDetail() {
  loading.value = true
  loadSharedApi({ type: 'knowledge', systemType: type.value })
    .getKnowledgeDetail(id)
    .then((res: any) => {
      current.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getApplicationDetail() {
  loading.value = true
  application
    .asyncGetApplicationDetail(id)
    .then((res: any) => {
      current.value = res.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  if (isKnowledge.value) {
    getKnowledgeDetail()
  } else if (isApplication.value) {
    getApplicationDetail()
  }
})
</script>

<style scoped lang="scss">
:deep(.dropdown-active) {
  background-color: var(--el-dropdown-menuItem-hover-fill);
  .el-dropdown-menu__item {
    color: var(--el-dropdown-menuItem-hover-color);
  }
}
.breadcrumb {
  .breadcrumb-hover {
    padding: 4px;
    border-radius: 4px;
    &:hover {
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
    }
  }
  &__footer {
    &:hover {
      background-color: var(--app-text-color-light-1);
    }
  }
}
</style>
