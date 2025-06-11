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
            <KnowledgeIcon v-if="isKnowledge" :type="row.icon" />

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
            v-model="row.permission[AuthorizationEnum.MANAGE]"
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
            v-model="allChecked[AuthorizationEnum.VIEW]"
            :indeterminate="allIndeterminate[AuthorizationEnum.VIEW]"
            :label="$t('views.resourceAuthorization.setting.check')"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.permission[AuthorizationEnum.VIEW]"
            @change="(e: boolean) => checkedOperateChange(AuthorizationEnum.VIEW, row, e)"
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

const isKnowledge = computed(() => props.type === AuthorizationEnum.KNOWLEDGE)
const isApplication = computed(() => props.type === AuthorizationEnum.APPLICATION)

const emit = defineEmits(['update:data'])
const allChecked: any = ref({
  [AuthorizationEnum.MANAGE]: computed({
    get: () => {
      return filterData.value.some((item: any) => item.permission[AuthorizationEnum.MANAGE])
    },
    set: (val: boolean) => {
      if (val) {
        filterData.value.map((item: any) => {
          item.permission[AuthorizationEnum.MANAGE] = true
          item.permission[AuthorizationEnum.VIEW] = true
        })
      } else {
        filterData.value.map((item: any) => {
          item.permission[AuthorizationEnum.MANAGE] = false
        })
      }
    },
  }),
  [AuthorizationEnum.VIEW]: computed({
    get: () => {
      return filterData.value.some((item: any) => item.permission[AuthorizationEnum.VIEW])
    },
    set: (val: boolean) => {
      if (val) {
        filterData.value.map((item: any) => {
          item.permission[AuthorizationEnum.VIEW] = true
        })
      } else {
        filterData.value.map((item: any) => {
          item.permission[AuthorizationEnum.VIEW] = false
          item.permission[AuthorizationEnum.MANAGE] = false
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
      (item: any) => !item.permission[AuthorizationEnum.MANAGE],
    )
    if (all_not_checked) {
      return false
    }
    return !filterData.value.every((item: any) => item.permission[AuthorizationEnum.MANAGE])
  }),
  [AuthorizationEnum.VIEW]: computed(() => {
    const all_not_checked = filterData.value.every(
      (item: any) => !item.permission[AuthorizationEnum.VIEW],
    )
    if (all_not_checked) {
      return false
    }
    return !filterData.value.every((item: any) => item.permission[AuthorizationEnum.VIEW])
  }),
})

function checkedOperateChange(Name: string | number, row: any, e: boolean) {
  props.data.map((item: any) => {
    if (item.id === row.id) {
      item.permission[Name] = e
      if (Name === AuthorizationEnum.MANAGE && e) {
        item.permission[AuthorizationEnum.VIEW] = true
      } else if (Name === AuthorizationEnum.VIEW && !e) {
        item.permission[AuthorizationEnum.MANAGE] = false
      }
    }
  })
}
</script>
<style lang="scss" scoped></style>
