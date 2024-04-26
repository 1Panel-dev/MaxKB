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
          <AppAvatar
            v-if="isApplication && isAppIcon(current?.icon)"
            shape="square"
            :size="24"
            style="background: none"
            class="mr-8"
          >
            <img :src="current?.icon" alt="" />
          </AppAvatar>
          <AppAvatar
            v-else-if="isApplication"
            :name="current?.name"
            pinyinColor
            shape="square"
            class="mr-8"
            :size="24"
          />

          <AppAvatar
            v-else-if="isDataset && current?.type === '1'"
            class="mr-8 avatar-purple"
            shape="square"
            :size="24"
          >
            <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <AppAvatar v-else class="mr-8" shape="square" :size="24">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <div class="ellipsis">{{ current?.name }}</div>
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
                      <AppAvatar
                        v-if="isApplication && isAppIcon(item?.icon)"
                        shape="square"
                        :size="24"
                        style="background: none"
                        class="mr-8"
                      >
                        <img :src="item?.icon" alt="" />
                      </AppAvatar>
                      <AppAvatar
                        v-else-if="isApplication"
                        :name="item.name"
                        pinyinColor
                        class="mr-12"
                        shape="square"
                        :size="24"
                      />
                      <AppAvatar
                        v-else-if="isDataset && item.type === '1'"
                        class="mr-12 avatar-purple"
                        shape="square"
                        :size="24"
                      >
                        <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <AppAvatar v-else class="mr-12" shape="square" :size="24">
                        <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <span class="ellipsis"> {{ item?.name }}</span>
                    </div>
                  </el-dropdown-item>
                </div>
              </template>
            </el-dropdown-menu>
            <div class="breadcrumb__footer border-t" style="padding: 8px 11px; min-width: 200px">
              <template v-if="isApplication">
                <div
                  class="w-full text-left cursor"
                  @click="router.push({ path: '/application/create' })"
                >
                  <el-button link>
                    <el-icon class="mr-4"><Plus /></el-icon> 创建应用
                  </el-button>
                </div>
              </template>
              <template v-else-if="isDataset">
                <div
                  class="w-full text-left cursor"
                  @click="router.push({ path: '/dataset/create' })"
                >
                  <el-button link>
                    <el-icon class="mr-4"><Plus /></el-icon> 创建知识库
                  </el-button>
                </div>
              </template>
            </div>
          </div>
        </el-scrollbar>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { onBeforeRouteLeave, useRouter, useRoute } from 'vue-router'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
const { common, dataset, application } = useStore()
const route = useRoute()
const router = useRouter()
const {
  meta: { activeMenu },
  params: { id }
} = route

onBeforeRouteLeave((to, from) => {
  common.saveBreadcrumb(null)
})

const list = ref<any[]>([])
const loading = ref(false)

const breadcrumbData = computed(() => common.breadcrumb)

const current = computed(() => {
  const {
    params: { id }
  } = route
  return list.value?.filter((v) => v.id === id)?.[0]
})
// const current = computed(() => {
//   const {
//     params: { id }
//   } = route
//   return list.value?.filter((v) => v.id === id)?.[0]?.type
// })

const isApplication = computed(() => {
  const { meta } = route as any
  return meta?.activeMenu.includes('application')
})
const isDataset = computed(() => {
  const { meta } = route as any
  return meta?.activeMenu.includes('dataset')
})
function changeMenu(id: string) {
  const lastMatched = route.matched[route.matched.length - 1]
  if (lastMatched) {
    router.push({ name: lastMatched.name, params: { id: id } })
  }
}

function getDataset() {
  loading.value = true
  dataset
    .asyncGetAllDataset()
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
onMounted(() => {
  if (!breadcrumbData.value) {
    if (isDataset.value) {
      getDataset()
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
      color: var(--el-menu-active-color);
    }
  }
  &__footer {
    &:hover {
      background-color: var(--app-text-color-light-1);
    }
  }
}
</style>
