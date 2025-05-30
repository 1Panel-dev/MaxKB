<template>
  <el-input
    v-model="filterText"
    :placeholder="$t('common.search')"
    prefix-icon="Search"
    class="p-24 pt-0 pb-0 mb-16 mt-4"
    clearable
  />
  <div class="p-24 pt-0">
    <el-table :data="filterData" :max-height="tableHeight">
      <el-table-column
        prop="name"
        :label="
          isApplication
            ? $t('views.application.applicationForm.form.appName.label')
            : $t('views.dataset.datasetForm.form.datasetName.label')
        "
      >
        <template #default="{ row }">
          <div class="flex align-center">
            <AppAvatar
              v-if="isApplication && isAppIcon(row?.icon)"
              style="background: none"
              class="mr-12"
              shape="square"
              :size="24"
            >
              <img :src="row?.icon" alt="" />
            </AppAvatar>

            <AppAvatar
              v-else-if="row?.name && isApplication"
              :name="row?.name"
              pinyinColor
              shape="square"
              :size="24"
              class="mr-12"
            />
            <AppAvatar
              v-if="row.icon === '1' && isDataset"
              class="mr-8 avatar-purple"
              shape="square"
              :size="24"
            >
              <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
            </AppAvatar>
            <AppAvatar
              v-else-if="row.icon === '2' && isDataset"
              class="mr-8 avatar-purple"
              shape="square"
              :size="24"
              style="background: none"
            >
              <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
            </AppAvatar>
            <AppAvatar v-else-if="isDataset" class="mr-8 avatar-blue" shape="square" :size="24">
              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
            </AppAvatar>
            <auto-tooltip :content="row?.name">
              {{ row?.name }}
            </auto-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('views.team.setting.management')"
        align="center"
        width="100"
        fixed="right"
      >
        <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[TeamEnum.MANAGE]"
            :indeterminate="allIndeterminate[TeamEnum.MANAGE]"
            :label="$t('views.team.setting.management')"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.operate[TeamEnum.MANAGE]"
            @change="(e: boolean) => checkedOperateChange(TeamEnum.MANAGE, row, e)"
          />
        </template>
      </el-table-column>
      <el-table-column
        :label="$t('views.team.setting.check')"
        align="center"
        width="100"
        fixed="right"
      >
        <template #header>
          <el-checkbox
            :disabled="props.manage"
            v-model="allChecked[TeamEnum.USE]"
            :indeterminate="allIndeterminate[TeamEnum.USE]"
            :label="$t('views.team.setting.check')"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.operate[TeamEnum.USE]"
            @change="(e: boolean) => checkedOperateChange(TeamEnum.USE, row, e)"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { TeamEnum } from '@/enums/team'
import { isAppIcon } from '@/utils/application'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  id: String,
  type: String,
  tableHeight: Number,
  manage: Boolean
})

const isDataset = computed(() => props.type === TeamEnum.DATASET)
const isApplication = computed(() => props.type === TeamEnum.APPLICATION)

const emit = defineEmits(['update:data'])
const allChecked: any = ref({
  [TeamEnum.MANAGE]: computed({
    get: () => {
      return filterData.value.some((item: any) => item.operate[TeamEnum.MANAGE])
    },
    set: (val: boolean) => {
      if (val) {
        filterData.value.map((item: any) => {
          item.operate[TeamEnum.MANAGE] = true
          item.operate[TeamEnum.USE] = true
        })
      } else {
        filterData.value.map((item: any) => {
          item.operate[TeamEnum.MANAGE] = false
        })
      }
    }
  }),
  [TeamEnum.USE]: computed({
    get: () => {
      return filterData.value.some((item: any) => item.operate[TeamEnum.USE])
    },
    set: (val: boolean) => {
      if (val) {
        filterData.value.map((item: any) => {
          item.operate[TeamEnum.USE] = true
        })
      } else {
        filterData.value.map((item: any) => {
          item.operate[TeamEnum.USE] = false
          item.operate[TeamEnum.MANAGE] = false
        })
      }
    }
  })
})

const filterText = ref('')

const filterData = computed(() =>
  props.data.filter((v: any) => v.name.toLowerCase().includes(filterText.value.toLowerCase()))
)

const allIndeterminate: any = ref({
  [TeamEnum.MANAGE]: computed(() => {
    const all_not_checked = filterData.value.every((item: any) => !item.operate[TeamEnum.MANAGE])
    if (all_not_checked) {
      return false
    }
    return !filterData.value.every((item: any) => item.operate[TeamEnum.MANAGE])
  }),
  [TeamEnum.USE]: computed(() => {
    const all_not_checked = filterData.value.every((item: any) => !item.operate[TeamEnum.USE])
    if (all_not_checked) {
      return false
    }
    return !filterData.value.every((item: any) => item.operate[TeamEnum.USE])
  })
})

function checkedOperateChange(Name: string | number, row: any, e: boolean) {
  props.data.map((item: any) => {
    if (item.id === row.id) {
      item.operate[Name] = e
      if (Name === TeamEnum.MANAGE && e) {
        item.operate[TeamEnum.USE] = true
      } else if (Name === TeamEnum.USE && !e) {
        item.operate[TeamEnum.MANAGE] = false
      }
    }
  })
}
</script>
<style lang="scss" scoped></style>
