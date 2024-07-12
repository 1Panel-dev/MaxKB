<template>
  <div class="theme-setting">
    <h4 class="p-16-24">外观设置</h4>
    <el-scrollbar>
      <div class="p-24 pt-0">
        <div class="app-card p-24">
          <h5 class="mb-16">平台显示主题</h5>
          <el-radio-group
            v-model="themeForm.theme"
            class="app-radio-button-group"
            @change="changeTheme"
          >
            <template v-for="(item, index) in themeList" :key="index">
              <el-radio-button :label="item.label" :value="item.value" />
            </template>
          </el-radio-group>
        </div>
        <div class="app-card p-24 mt-16">
          <h5 class="mb-16">平台登陆设置</h5>
          <el-card shadow="never" class="layout-bg">
            <div class="flex-between">
              <h5 class="mb-16">页面预览</h5>
              <el-button type="primary" link> 恢复默认 </el-button>
            </div>
            <div class="theme-preview">
              <el-row :gutter="8">
                <el-col :span="16">
                  <LoginPreview />
                </el-col>
                <el-col :span="8">
                  <div class="theme-form">
                    <el-card shadow="never" class="mb-8">
                      <div class="flex-between mb-8">
                        <span class="lighter">网站 Logo</span>
                        <el-button size="small"> 替换图片 </el-button>
                      </div>
                      <el-text type="info" size="small"
                        >顶部网站显示的 Logo，建议尺寸 48 x 48，支持 JPG、PNG、SVG，大小不超过
                        200KB</el-text
                      >
                    </el-card>
                    <el-card shadow="never" class="mb-8">
                      <div class="flex-between mb-8">
                        <span class="lighter">登录 Logo</span>
                        <el-button size="small"> 替换图片 </el-button>
                      </div>
                      <el-text type="info" size="small"
                        >登录页面右侧 Logo，建议尺寸 204*52，支持 JPG、PNG、SVG，大小不超过
                        200KB</el-text
                      >
                    </el-card>
                    <el-card shadow="never" class="mb-8">
                      <div class="flex-between mb-8">
                        <span class="lighter">登录背景图</span>
                        <el-button size="small"> 替换图片 </el-button>
                      </div>
                      <el-text type="info" size="small">
                        左侧背景图，矢量图建议尺寸 576*900，位图建议尺寸1152*1800；支持
                        JPG、PNG、SVG，大小不超过 5M
                      </el-text>
                    </el-card>

                    <el-form
                      ref="themeFormRef"
                      :model="themeForm"
                      label-position="top"
                      require-asterisk-position="right"
                      :rules="rules"
                      @submit.prevent
                    >
                      <el-form-item label="网站名称" prop="title">
                        <el-input v-model="themeForm.title" placeholder="请输入网站名称">
                        </el-input>
                        <el-text type="info"> 显示在网页 Tab 的平台名称 </el-text>
                      </el-form-item>
                      <el-form-item label="欢迎语" prop="slogan">
                        <el-input v-model="themeForm.slogan" placeholder="请输入欢迎语"> </el-input>
                        <el-text type="info"> 产品 Logo 下的 欢迎语 </el-text>
                      </el-form-item>
                    </el-form>
                  </div></el-col
                >
              </el-row>
            </div>

            <div class="mt-16">
              <el-text type="info">默认为 MaxKB 登录界面，支持自定义设置</el-text>
            </div>
          </el-card>
        </div>
      </div>
    </el-scrollbar>
    <div class="theme-setting__operate w-full p-16-24">
      <el-button @click="resetTheme">放弃更新</el-button>
      <el-button type="primary"> 保存并应用 </el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import LoginPreview from './LoginPreview.vue'
import { useElementPlusTheme } from 'use-element-plus-theme'

const themeList = [
  {
    label: '默认',
    value: '#3370FF',
    loginBackground: '@/assets/theme/default.jpg'
  },
  {
    label: '活力橙',
    value: '#FF8800',
    loginBackground: '@/assets/theme/orange.jpg'
  },
  {
    label: '松石绿',
    value: '#00B69D',
    loginBackground: '@/assets/theme/green.jpg'
  },
  {
    label: '商务蓝',
    value: '#4954E6',
    loginBackground: '@/assets/theme/default.jpg'
  },
  {
    label: '神秘紫',
    value: '#7F3BF5',
    loginBackground: '@/assets/theme/purple.jpg'
  },
  {
    label: '胭脂红',
    value: '#F01D94',
    loginBackground: '@/assets/theme/red.jpg'
  }
]
const themeFormRef = ref<FormInstance>()
const themeForm = ref({
  theme: '#3370FF',
  icon: '',
  loginLogo: '',
  loginImage: '',
  title: 'MaxKB',
  slogan: '欢迎使用 MaxKB 智能知识库'
})

const rules = reactive<FormRules>({
  title: [{ required: true, message: '请输入网站标题', trigger: 'blur' }],
  slogan: [{ required: true, message: '请输入欢迎语', trigger: 'blur' }]
})

const { changeTheme } = useElementPlusTheme(themeForm.value.theme)

function resetTheme() {
  themeForm.value.theme = '#3370FF'
  changeTheme(themeForm.value.theme)
}

watch(
  () => themeForm.value.theme,
  (val) => {
    if (val) {
      console.log(val)
    }
  }
)
</script>

<style lang="scss" scoped>
.theme-setting {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  padding-bottom: 64px;

  &__operate {
    position: absolute;
    bottom: 0;
    right: 0;
    left: 0;
    background: #ffffff;
    text-align: right;
    box-sizing: border-box;
    box-shadow: 0px -2px 4px 0px rgba(31, 35, 41, 0.08);
  }
  .theme-preview {
    min-width: 1000px;
  }
}
</style>
