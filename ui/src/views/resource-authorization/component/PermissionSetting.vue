<template>
  <el-input
    v-model="filterText"
    :placeholder="$t('common.search')"
    prefix-icon="Search"
    class="mb-16 mt-4"
    clearable
  />
  <div class="pt-0">
    <el-table :data="filterData" :max-height="tableHeight">
      <el-table-column prop="name" :label="$t('common.name')">
        <template #default="{ row }">
          <div class="flex align-center">
            <el-avatar
              v-if="isApplication && isAppIcon(row?.icon)"
              style="background: none"
              class="mr-12"
              shape="square"
              :size="24"
            >
              <img :src="row?.icon" alt="" />
            </el-avatar>

            <el-avatar
              v-else-if="row?.name && isApplication"
              :name="row?.name"
              pinyinColor
              shape="square"
              :size="24"
              class="mr-12"
            />
            <el-avatar
              v-if="row.icon === '1' && isDataset"
              class="mr-8 avatar-purple"
              shape="square"
              :size="24"
            >
              <img src="@/assets/knowledge/icon_web.svg" style="width: 58%" alt="" />
            </el-avatar>
            <el-avatar
              v-else-if="row.icon === '2' && isDataset"
              class="mr-8 avatar-purple"
              shape="square"
              :size="24"
              style="background: none"
            >
              <img src="@/assets/knowledge/logo_lark.svg" style="width: 100%" alt="" />
            </el-avatar>
            <el-avatar v-else-if="isDataset" class="mr-8 avatar-blue" shape="square" :size="24">
              <img src="@/assets/knowledge/icon_document.svg" style="width: 58%" alt="" />
            </el-avatar>
            <auto-tooltip :content="row?.name">
              {{ row?.name }}
            </auto-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('views.resourceAuthorization.setting.management')"
        align="center"
        width="100"
        fixed="right"
      >
        <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.MANAGE]"
            :indeterminate="allIndeterminate[AuthorizationEnum.MANAGE]"
            :label="$t('views.resourceAuthorization.setting.management')"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.operate[AuthorizationEnum.MANAGE]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.MANAGE, row, e)"
          />
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('views.resourceAuthorization.setting.check')"
        align="center"
        width="100"
        fixed="right"
      >
        <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[AuthorizationEnum.USE]"
            :indeterminate="allIndeterminate[AuthorizationEnum.USE]"
            :label="$t('views.resourceAuthorization.setting.check')"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.operate[AuthorizationEnum.USE]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.USE, row, e)"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { AuthorizationEnum } from '@/enums/system'
import { isAppIcon } from '@/utils/common'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  id: String,
  type: String,
  tableHeight: Number,
  manage: Boolean,
})

const isDataset = computed(() => props.type === AuthorizationEnum.DATASET)
const isApplication = computed(() => props.type === AuthorizationEnum.APPLICATION)

const emit = defineEmits(['update:data'])
const allChecked: any = ref({
  [AuthorizationEnum.MANAGE]: computed({
    get: () => {
      return filterData.value.some((item: any) => item.operate[AuthorizationEnum.MANAGE])
    },
    set: (val: boolean) => {
      if (val) {
        filterData.value.map((item: any) => {
          item.operate[AuthorizationEnum.MANAGE] = true
          item.operate[AuthorizationEnum.USE] = true
        })
      } else {
        filterData.value.map((item: any) => {
          item.operate[AuthorizationEnum.MANAGE] = false
        })
      }
    },
  }),
  [AuthorizationEnum.USE]: computed({
    get: () => {
      return filterData.value.some((item: any) => item.operate[AuthorizationEnum.USE])
    },
    set: (val: boolean) => {
      if (val) {
        filterData.value.map((item: any) => {
          item.operate[AuthorizationEnum.USE] = true
        })
      } else {
        filterData.value.map((item: any) => {
          item.operate[AuthorizationEnum.USE] = false
          item.operate[AuthorizationEnum.MANAGE] = false
        })
      }
    },
  }),
})

const filterText = ref('')

const filterData = computed(() =>
  props.data.filter((v: any) => v.name.toLowerCase().includes(filterText.value.toLowerCase())),
)

const allIndeterminate: any = ref({
  [AuthorizationEnum.MANAGE]: computed(() => {
    const all_not_checked = filterData.value.every(
      (item: any) => !item.operate[AuthorizationEnum.MANAGE],
    )
    if (all_not_checked) {
      return false
    }
    return !filterData.value.every((item: any) => item.operate[AuthorizationEnum.MANAGE])
  }),
  [AuthorizationEnum.USE]: computed(() => {
    const all_not_checked = filterData.value.every(
      (item: any) => !item.operate[AuthorizationEnum.USE],
    )
    if (all_not_checked) {
      return false
    }
    return !filterData.value.every((item: any) => item.operate[AuthorizationEnum.USE])
  }),
})

function checkedOperateChange(Name: string | number, row: any, e: boolean) {
  props.data.map((item: any) => {
    if (item.id === row.id) {
      item.operate[Name] = e
      if (Name === AuthorizationEnum.MANAGE && e) {
        item.operate[AuthorizationEnum.USE] = true
      } else if (Name === AuthorizationEnum.USE && !e) {
        item.operate[AuthorizationEnum.MANAGE] = false
      }
    }
  })
}
</script>
<style lang="scss" scoped></style>
