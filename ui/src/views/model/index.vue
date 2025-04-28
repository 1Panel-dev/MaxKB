<template>
  1111111111
  <!-- <LayoutContainer :header="$t('views.model.title')">
    <div class="model-manage flex main-calc-height">
      <div class="model-manage__left p-8 border-r">
        <h4 class="p-16">{{ $t('views.model.provider') }}</h4>
        <div class="model-list-height-left">
          <div
            class="all-mode flex cursor"
            @click="clickListHandle(allObj as Provider)"
            :class="!active_provider?.provider ? 'all-mode-active' : ''"
          >
            <AppIcon
              class="mr-8"
              style="height: 20px; width: 20px"
              :iconName="'app-all-menu-active'"
            ></AppIcon>
            <span>{{ $t('views.model.modelType.allModel') }}</span>
          </div>

          <el-scrollbar>
            <el-collapse class="model-collapse">
              <el-collapse-item :title="$t('views.model.modelType.publicModel')" name="1">
                <template #title>
                  <img src="@/assets/icon_file-folder_colorful.svg" class="mr-8" />
                  {{ $t('views.model.modelType.publicModel') }}
                </template>
                <common-list
                  :data="online_provider_list"
                  v-loading="loading"
                  @click="clickListHandle"
                  value-key="provider"
                  default-active=""
                  ref="commonList1"
                >
                  <template #default="{ row }">
                    <div class="flex align-center">
                      <span
                        :innerHTML="row.icon"
                        alt=""
                        style="height: 20px; width: 20px"
                        class="mr-8"
                      />
                      <span>{{ row.name }}</span>
                    </div>
                  </template>
                </common-list>
              </el-collapse-item>
              <el-collapse-item :title="$t('views.model.modelType.privateModel')" name="2">
                <template #title>
                  <img src="@/assets/icon_file-folder_colorful.svg" class="mr-8" />
                  {{ $t('views.model.modelType.privateModel') }}
                </template>
                <common-list
                  :data="local_provider_list"
                  v-loading="loading"
                  @click="clickListHandle"
                  value-key="provider"
                  default-active=""
                  ref="commonList2"
                >
                  <template #default="{ row }">
                    <div class="flex align-center">
                      <span
                        :innerHTML="row.icon"
                        alt=""
                        style="height: 20px; width: 20px"
                        class="mr-8"
                      />
                      <span>{{ row.name }}</span>
                    </div>
                  </template>
                </common-list>
              </el-collapse-item>
            </el-collapse>
          </el-scrollbar>
        </div>
      </div>
      <div class="model-manage__right w-full" v-loading="list_model_loading">
        <div class="p-24 pb-0">
          <h4>{{ active_provider?.name }}</h4>
          <div class="flex-between mt-16 mb-16">
            <el-button type="primary" @click="openCreateModel(active_provider)">
              {{ $t('views.model.addModel') }}</el-button
            >
            <div class="flex-between complex-search">
              <el-select
                class="complex-search__left"
                v-model="search_type"
                style="width: 120px"
                @change="search_type_change"
              >
                <el-option :label="$t('common.creator')" value="create_user" />
                <el-option
                  :label="$t('views.model.modelForm.form.permissionType.label')"
                  value="permission_type"
                />
                <el-option
                  :label="$t('views.model.modelForm.form.model_type.label')"
                  value="model_type"
                />
                <el-option
                  :label="$t('views.model.modelForm.form.templateName.label')"
                  value="name"
                />
              </el-select>
              <el-input
                v-if="search_type === 'name'"
                v-model="model_search_form.name"
                @change="list_model"
                :placeholder="$t('views.model.searchBar.placeholder')"
                prefix-icon="Search"
                style="width: 220px"
                clearable
              />
              <el-select
                v-else-if="search_type === 'create_user'"
                v-model="model_search_form.create_user"
                @change="list_model"
                clearable
                style="width: 220px"
              >
                <el-option
                  v-for="u in user_options"
                  :key="u.id"
                  :value="u.id"
                  :label="u.username"
                />
              </el-select>
              <el-select
                v-else-if="search_type === 'permission_type'"
                v-model="model_search_form.permission_type"
                clearable
                @change="list_model"
                style="width: 220px"
              >
                <el-option :label="$t('common.public')" value="PUBLIC" />
                <el-option :label="$t('common.private')" value="PRIVATE" />
              </el-select>
              <el-select
                v-else-if="search_type === 'model_type'"
                v-model="model_search_form.model_type"
                clearable
                @change="list_model"
                style="width: 220px"
              >
                <template v-for="item in modelTypeList" :key="item.value">
                  <el-option :label="item.text" :value="item.value" />
                </template>
              </el-select>
            </div>
          </div>
        </div>
        <div class="model-list-height">
          <el-scrollbar>
            <div class="p-24 pt-0">
              <el-row v-if="model_split_list.length > 0" :gutter="15">
                <template v-for="(row, index) in model_split_list" :key="index">
                  <el-col
                    :xs="24"
                    :sm="24"
                    :md="24"
                    :lg="12"
                    :xl="12"
                    class="mb-16"
                    v-for="(model, i) in row"
                    :key="i"
                  >
                    <ModelCard
                      @change="list_model"
                      :updateModelById="updateModelById"
                      :model="model"
                      :provider_list="provider_list"
                    >
                    </ModelCard>
                  </el-col>
                </template>
              </el-row>
              <el-empty :description="$t('common.noData')" v-else />
            </div>
          </el-scrollbar>
        </div>
      </div>
    </div>
    <CreateModelDialog
      ref="createModelRef"
      @submit="list_model"
      @change="openCreateModel($event)"
    ></CreateModelDialog>

    <SelectProviderDialog
      ref="selectProviderRef"
      @change="(provider, modelType) => openCreateModel(provider, modelType)"
    ></SelectProviderDialog>
  </LayoutContainer> -->
</template>

<script lang="ts" setup>

</script>

<style lang="scss" scoped>
.model-manage {
  &__left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);
  }

  .model-list-height {
    height: calc(var(--create-dataset-height) - 80px);
  }

  .model-list-height-left {
    height: calc(var(--create-dataset-height) - 40px);
  }
  .all-mode {
    padding: 10px 16px;
  }
  .all-mode-active {
    background: var(--el-color-primary-light-9);
    border-radius: 4px;
    color: var(--el-color-primary);
    font-weight: 500;
  }
  .template-collapse {
    border-top: none !important;
    border-bottom: none !important;
    :deep(.el-collapse-item__header) {
      border-bottom: none !important;
      padding-left: 16px;
      font-size: 14px;
      height: 40px;
      &:hover {
        background: var(--app-text-color-light-1);
        border-radius: 4px;
      }
    }
    :deep(.el-collapse-item) {
      margin-top: 2px;
    }
    :deep(.common-list) {
      li {
        padding-left: 30px !important;
      }
    }
    :deep(.el-collapse-item__wrap) {
      border-bottom: none !important;
    }
    :deep(.el-collapse-item__content) {
      padding-bottom: 0 !important;
    }
  }
}
</style>
