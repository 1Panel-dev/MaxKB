<template>
  <div class="flex align-center ml-8 mt-8 mb-16">
    <back-button :to="activeMenu"></back-button>
    <el-dropdown placement="bottom-start" trigger="click" @command="changeMenu">
      <span class="el-dropdown-link flex">
        <span class="ellipsis-1"> {{ currentName }}</span>
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <template v-for="(item, index) in list" :key="index">
            <div :class="item.id === id ? 'dropdown-active' : ''">
              <el-dropdown-item :command="item.id">
                <div class="flex">
                  <AppAvatar class="mr-12" shape="square" :size="24">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <span class="ellipsis-1"> {{ item?.name }}</span>
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
              <el-icon class="mr-4"><Plus /></el-icon> 创建数据集
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

const isApplication = computed(() => {
  const { meta } = route as any
  return meta?.activeMenu.includes('application')
})
const isDataset = computed(() => {
  const { meta } = route as any
  return meta?.activeMenu.includes('dataset')
})
function changeMenu(id: string) {
  if (isApplication.value) {
    router.push({ path: `/application/${id}/overview` })
  } else if (isDataset.value) {
    router.push({ path: `/dataset/${id}/document` })
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
