<template>
  <div class="ml-8 mt-8 mb-16 flex">
    <back-button :to="activeMenu"></back-button>
    <el-dropdown
      placement="top"
      trigger="click"
      @command="changeMenu"
      class="w-full"
      style="display: block"
    >
      <div class="flex-between">
        <div class="flex align-center">
          <AppAvatar
            v-if="isApplication"
            :name="currentName"
            pinyinColor
            shape="square"
            class="mr-8"
            :size="24"
          />
          <AppAvatar
            v-else-if="isDataset && currentType === '1'"
            class="mr-8 avatar-purple"
            shape="square"
            :size="24"
          >
            <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <AppAvatar v-else class="mr-8" shape="square" :size="24">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <div class="ellipsis">{{ currentName }}</div>
        </div>

        <el-button text>
          <el-icon><CaretBottom /></el-icon>
        </el-button>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <template v-for="(item, index) in list" :key="index">
            <div :class="item.id === id ? 'dropdown-active' : ''">
              <el-dropdown-item :command="item.id">
                <div class="flex align-center">
                  <AppAvatar
                    v-if="isApplication"
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
        <div class="border-t" style="padding: 8px 11px; min-width: 200px">
          <template v-if="isApplication">
            <el-button link @click="router.push({ path: '/application/create' })">
              <el-icon class="mr-4"><Plus /></el-icon> 创建应用
            </el-button>
          </template>
          <template v-else-if="isDataset">
            <el-button link @click="router.push({ path: '/dataset/create' })">
              <el-icon class="mr-4"><Plus /></el-icon> 创建知识库
            </el-button>
          </template>
        </div>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { onBeforeRouteLeave, useRouter, useRoute } from 'vue-router'
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

const currentName = computed(() => {
  const {
    params: { id }
  } = route
  return list.value?.filter((v) => v.id === id)?.[0]?.name
})
const currentType = computed(() => {
  const {
    params: { id }
  } = route
  return list.value?.filter((v) => v.id === id)?.[0]?.type
})

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
    .asyncGetAllDateset()
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
</style>
