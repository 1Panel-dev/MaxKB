<template>
  <div class="breadcrumb ml-4 mt-4 mb-12 flex">
    <back-button :to="activeMenu" class="mt-4"></back-button>
    <el-dropdown
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
          <el-avatar
            v-else-if="isApplication"
            :name="current?.name"
            pinyinColor
            shape="square"
            class="mr-8"
            :size="24"
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
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { onBeforeRouteLeave, useRouter, useRoute } from 'vue-router'
import { isWorkFlow } from '@/utils/application'
import { isAppIcon } from '@/utils/common'

import useStore from '@/stores'
const { common, knowledge, application } = useStore()
const route = useRoute()
const router = useRouter()
const {
  meta: { activeMenu },
  params: { id },
} = route as any

onBeforeRouteLeave((to, from) => {
  common.saveBreadcrumb(null)
})

const CreateKnowledgeDialogRef = ref()
const CreateApplicationDialogRef = ref()
const list = ref<any[]>([])
const loading = ref(false)

const breadcrumbData = computed(() => common.breadcrumb)

const current = computed(() => {
  return list.value?.filter((v) => v.id === id)?.[0]
})

const isApplication = computed(() => {
  return activeMenu.includes('application')
})
const isKnowledge = computed(() => {
  return activeMenu.includes('knowledge')
})

function openCreateDialog() {
  if (isKnowledge.value) {
    CreateKnowledgeDialogRef.value.open()
  } else if (isApplication.value) {
    CreateApplicationDialogRef.value.open()
  }
}

function changeMenu(id: string) {
  const lastMatched = route.matched[route.matched.length - 1]
  if (lastMatched) {
    if (isKnowledge.value) {
      router.push({ name: lastMatched.name, params: { id: id } })
    } else if (isApplication.value) {
      const type = list.value?.filter((v) => v.id === id)?.[0]?.type
      if (
        isWorkFlow(type) &&
        (lastMatched.name === 'AppSetting' || lastMatched.name === 'AppHitTest')
      ) {
        router.push({ path: `/application/${id}/${type}/overview` })
      } else {
        router.push({
          name: lastMatched.name,
          params: { id: id, type: type },
        })
      }
    }
  }
}

function getKnowledge() {
  loading.value = true
  knowledge
    .asyncGetRootKnowledge()
    .then((res: any) => {
      list.value = res.data
      common.saveBreadcrumb(list.value)
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}
function getApplication() {
  loading.value = true
  application
    .asyncGetAllApplication()
    .then((res: any) => {
      list.value = res.data
      common.saveBreadcrumb(list.value)
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}
function refresh() {
  common.saveBreadcrumb(null)
}
onMounted(() => {
  if (!breadcrumbData.value) {
    if (isKnowledge.value) {
      getKnowledge()
    } else if (isApplication.value) {
      getApplication()
    }
  } else {
    list.value = breadcrumbData.value
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
