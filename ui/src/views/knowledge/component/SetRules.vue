<template>
  <div class="set-rules">
    <el-row>
      <el-col :span="10" class="p-24">
        <h4 class="title-decoration-1 mb-16">{{ $t('views.document.setRules.title.setting') }}</h4>
        <div class="set-rules__right">
          <el-scrollbar>
            <div class="left-height" @click.stop>
              <el-radio-group v-model="radio" class="set-rules__radio">
                <el-card shadow="never" class="mb-16" :class="radio === '1' ? 'active' : ''">
                  <el-radio value="1" size="large">
                    <p class="mb-4">{{ $t('views.document.setRules.intelligent.label') }}</p>
                    <el-text type="info">{{
                      $t('views.document.setRules.intelligent.text')
                    }}</el-text>
                  </el-radio>
                </el-card>
                <el-card shadow="never" class="mb-16" :class="radio === '2' ? 'active' : ''">
                  <el-radio value="2" size="large">
                    <p class="mb-4">{{ $t('views.document.setRules.advanced.label') }}</p>
                    <el-text type="info">
                      {{ $t('views.document.setRules.advanced.text') }}
                    </el-text>
                  </el-radio>

                  <el-card
                    v-if="radio === '2'"
                    shadow="never"
                    class="card-never mt-16"
                    style="margin-left: 30px"
                  >
                    <div class="set-rules__form">
                      <div class="form-item mb-16">
                        <div class="title flex align-center mb-8">
                          <span style="margin-right: 4px">{{
                            $t('views.document.setRules.patterns.label')
                          }}</span>
                          <el-tooltip
                            effect="dark"
                            :content="$t('views.document.setRules.patterns.tooltip')"
                            placement="right"
                          >
                            <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                          </el-tooltip>
                        </div>
                        <div @click.stop>
                          <el-select
                            v-model="form.patterns"
                            multiple
                            allow-create
                            default-first-option
                            filterable
                            :placeholder="$t('views.document.setRules.patterns.placeholder')"
                          >
                            <el-option
                              v-for="(item, index) in splitPatternList"
                              :key="index"
                              :label="item.key"
                              :value="item.value"
                            >
                            </el-option>
                          </el-select>
                        </div>
                      </div>
                      <div class="form-item mb-16">
                        <div class="title mb-8">
                          {{ $t('views.document.setRules.limit.label') }}
                        </div>
                        <el-slider
                          v-model="form.limit"
                          show-input
                          :show-input-controls="false"
                          :min="50"
                          :max="100000"
                        />
                      </div>
                      <div class="form-item mb-16">
                        <div class="title mb-8">
                          {{ $t('views.document.setRules.with_filter.label') }}
                        </div>
                        <el-switch size="small" v-model="form.with_filter" />
                        <div style="margin-top: 4px">
                          <el-text type="info">
                            {{ $t('views.document.setRules.with_filter.text') }}</el-text
                          >
                        </div>
                      </div>
                    </div>
                  </el-card>
                </el-card>
              </el-radio-group>
            </div>
          </el-scrollbar>
          <div>
            <el-checkbox
              v-model="checkedConnect"
              @change="changeHandle"
              style="white-space: normal"
            >
              {{ $t('views.document.setRules.checkedConnect.label') }}
            </el-checkbox>
          </div>
          <div class="text-right mt-8">
            <el-button @click="splitDocument">
              {{ $t('views.document.buttons.preview') }}</el-button
            >
          </div>
        </div>
      </el-col>

      <el-col :span="14" class="p-24 border-l">
        <div v-loading="loading">
          <h4 class="title-decoration-1 mb-8">{{ $t('views.document.setRules.title.preview') }}</h4>

          <ParagraphPreview v-model:data="paragraphList" :isConnect="checkedConnect" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import ParagraphPreview from '@/views/dataset/component/ParagraphPreview.vue'
import { cutFilename } from '@/utils/utils'
import documentApi from '@/api/document'
import useStore from '@/stores'
import type { KeyValue } from '@/api/type/common'
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const splitPatternList = ref<Array<KeyValue<string, string>>>([])

const radio = ref('1')
const loading = ref(false)
const paragraphList = ref<any[]>([])
const patternLoading = ref<boolean>(false)
const checkedConnect = ref<boolean>(false)

const firstChecked = ref(true)

const form = reactive<{
  patterns: Array<string>
  limit: number
  with_filter: boolean
  [propName: string]: any
}>({
  patterns: [],
  limit: 500,
  with_filter: true
})

function changeHandle(val: boolean) {
  if (val && firstChecked.value) {
    paragraphList.value = paragraphList.value.map((item: any) => ({
      ...item,
      content: item.content.map((v: any) => ({
        ...v,
        problem_list: v.title.trim()
          ? [
              {
                content: v.title.trim()
              }
            ]
          : []
      }))
    }))
    firstChecked.value = false
  }
}
function splitDocument() {
  loading.value = true
  let fd = new FormData()
  documentsFiles.value.forEach((item) => {
    if (item?.raw) {
      fd.append('file', item?.raw)
    }
  })
  if (radio.value === '2') {
    Object.keys(form).forEach((key) => {
      if (key == 'patterns') {
        form.patterns.forEach((item) => fd.append('patterns', item))
      } else {
        fd.append(key, form[key])
      }
    })
  }
  documentApi
    .postSplitDocument(fd)
    .then((res: any) => {
      const list = res.data

      list.map((item: any) => {
        if (item.name.length > 128) {
          item.name = cutFilename(item.name, 128)
        }
        if (checkedConnect.value) {
          item.content.map((v: any) => {
            v['problem_list'] = v.title.trim()
              ? [
                  {
                    content: v.title.trim()
                  }
                ]
              : []
          })
        }
      })

      paragraphList.value = list
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

const initSplitPatternList = () => {
  documentApi.listSplitPattern(patternLoading).then((ok) => {
    splitPatternList.value = ok.data
  })
}

watch(radio, () => {
  if (radio.value === '2') {
    initSplitPatternList()
  }
})

onMounted(() => {
  splitDocument()
})

defineExpose({
  paragraphList,
  checkedConnect,
  loading
})
</script>
<style scoped lang="scss">
.set-rules {
  width: 100%;

  .left-height {
    max-height: calc(var(--create-dataset-height) - 110px);
    overflow-x: hidden;
  }

  &__radio {
    width: 100%;
    display: block;

    .el-radio {
      white-space: break-spaces;
      width: 100%;
      height: 100%;
      line-height: 22px;
      color: var(--app-text-color);
    }

    :deep(.el-radio__label) {
      padding-left: 30px;
      width: 100%;
    }
    :deep(.el-radio__input) {
      position: absolute;
      top: 16px;
    }
    .active {
      border: 1px solid var(--el-color-primary);
    }
  }

  &__form {
    .title {
      font-size: 14px;
      font-weight: 400;
    }
  }
}
</style>
