<template>
  <el-input
    v-model="filterText"
    placeholder="搜索"
    prefix-icon="Search"
    class="p-24 pt-0 pb-0 mb-16 mt-4"
    clearable
  />
  <div class="p-24 pt-0">
    <el-table :data="filterData" :max-height="tableHeight">
      <el-table-column prop="name" :label="isApplication ? '应用名称' : '知识库名称'">
        <template #default="{ row }">
          <div class="flex align-center">
            <AppAvatar
              v-if="isApplication"
              :name="row.name"
              pinyinColor
              class="mr-12"
              shape="square"
              :size="24"
            />
            <AppAvatar v-else-if="isDataset" class="mr-12 avatar-blue" shape="square" :size="24">
              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
            </AppAvatar>
            <auto-tooltip :content="row?.name">
              {{ row?.name }}
            </auto-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="管理" align="center" width="60" fixed="right">
        <!-- <template #header>
        <el-checkbox
          v-model="allChecked[MANAGE]"
          label="管理"
          @change="handleCheckAllChange($event, MANAGE)"
        />
      </template> -->
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.operate[TeamEnum.MANAGE]"
            @change="checkedOperateChange(TeamEnum.MANAGE, row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="使用" align="center" width="60" fixed="right">
        <!-- <template #header>
        <el-checkbox
          v-model="allChecked[USE]"
          label="使用"
          @change="handleCheckAllChange($event, USE)"
        />
      </template> -->
        <template #default="{ row }">
          <el-checkbox
            :disabled="props.manage"
            v-model="row.operate[TeamEnum.USE]"
            @change="checkedOperateChange(TeamEnum.USE, row)"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { TeamEnum } from '@/enums/team'

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
  [TeamEnum.MANAGE]: false,
  [TeamEnum.USE]: false
})

const filterText = ref('')

const filterData = computed(() => props.data.filter((v: any) => v.name.includes(filterText.value)))

watch(
  () => props.data,
  (val) => {
    Object.keys(allChecked.value).map((item) => {
      allChecked.value[item] = compare(item)
    })
    emit('update:data', val)
  },
  {
    deep: true
  }
)

function handleCheckAllChange(val: string | number | boolean, Name: string | number) {
  if (val) {
    props.data.map((item: any) => {
      item.operate[Name] = true
    })
  } else {
    props.data.map((item: any) => {
      item.operate[Name] = false
    })
  }
}
function checkedOperateChange(Name: string | number, row: any) {
  if (Name === TeamEnum.MANAGE && row.operate[TeamEnum.MANAGE]) {
    props.data.map((item: any) => {
      if (item.id === row.id) {
        item.operate[TeamEnum.USE] = true
      }
    })
  }
  allChecked.value[Name] = compare(Name)
}

function compare(attrs: string | number) {
  const filterData = props.data.filter((item: any) => item?.operate[attrs])
  return props.data.length > 0 && filterData.length === props.data.length
}

onMounted(() => {
  Object.keys(allChecked.value).map((item) => {
    allChecked.value[item] = compare(item)
  })
})
</script>
<style lang="scss" scope></style>
