<template>
  <div>
    <!-- 推理过程组件 -->
    <ReasoningRander :content="reasoning_content" v-if="reasoning_content?.trim()" />
    <template v-for="(item, index) in md_view_list" :key="index">
      <div
        v-if="item.type === 'question'"
        @click="sendMessage ? sendMessage(item.content, 'new') : (content: string) => {}"
        class="problem-button mt-4 mb-4 flex"
        :class="sendMessage ? 'cursor' : 'disabled'"
      >
        <el-icon class="mr-8" style="margin-top: 2px;">
          <EditPen />
        </el-icon>
        {{ item.content }}
      </div>
      <HtmlRander v-else-if="item.type === 'html_rander'" :source="item.content"></HtmlRander>
      <EchartsRander
        v-else-if="item.type === 'echarts_rander'"
        :option="item.content"
      ></EchartsRander>
      <FormRander
        :chat_record_id="chat_record_id"
        :runtime_node_id="runtime_node_id"
        :child_node="child_node"
        :disabled="disabled"
        :send-message="sendMessage"
        v-else-if="item.type === 'form_rander'"
        :form_setting="item.content"
      ></FormRander>
      <MdPreview
        v-else
        ref="editorRef"
        editorId="preview-only"
        :modelValue="item.content"
        :key="index"
        class="maxkb-md"
      />
    </template>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { config } from 'md-editor-v3'
import HtmlRander from './HtmlRander.vue'
import EchartsRander from './EchartsRander.vue'
import FormRander from './FormRander.vue'
import ReasoningRander from './ReasoningRander.vue'
config({
  markdownItConfig(md) {
    md.renderer.rules.image = (tokens, idx, options, env, self) => {
      tokens[idx].attrSet('style', 'display:inline-block;min-height:33px;padding:0;margin:0')
      if (tokens[idx].content) {
        tokens[idx].attrSet('title', tokens[idx].content)
      }
      tokens[idx].attrSet(
        'onerror',
        'this.src="/ui/assets/load_error.png";this.onerror=null;this.height="33px"'
      )
      return md.renderer.renderToken(tokens, idx, options)
    }
    md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
      tokens[idx].attrSet('target', '_blank')
      return md.renderer.renderToken(tokens, idx, options)
    }
    document.appendChild
  }
})
const props = withDefaults(
  defineProps<{
    source?: string
    reasoning_content?: string
    inner_suffix?: boolean
    sendMessage?: (question: string, type: 'old' | 'new', other_params_data?: any) => void
    child_node?: any
    chat_record_id?: string
    runtime_node_id?: string
    disabled?: boolean
  }>(),
  {
    source: '',
    disabled: false
  }
)
const editorRef = ref()
const md_view_list = computed(() => {
  const temp_source = props.source
  return split_form_rander(
    split_echarts_rander(split_html_rander(split_quick_question([temp_source])))
  )
})

const split_quick_question = (result: Array<string>) => {
  return result
    .map((item) => split_quick_question_(item))
    .reduce((x: any, y: any) => {
      return [...x, ...y]
    }, [])
}
const split_quick_question_ = (source: string) => {
  const temp_md_quick_question_list = source.match(/<quick_question>[\d\D]*?<\/quick_question>/g)
  const md_quick_question_list = temp_md_quick_question_list
    ? temp_md_quick_question_list.filter((i) => i)
    : []
  const split_quick_question_value = source
    .split(/<quick_question>[\d\D]*?<\/quick_question>/g)
    .filter((item) => item !== undefined)
    .filter((item) => !md_quick_question_list?.includes(item))
  const result = Array.from(
    { length: md_quick_question_list.length + split_quick_question_value.length },
    (v, i) => i
  ).map((index) => {
    if (index % 2 == 0) {
      return { type: 'md', content: split_quick_question_value[Math.floor(index / 2)] }
    } else {
      return {
        type: 'question',
        content: md_quick_question_list[Math.floor(index / 2)]
          .replace('<quick_question>', '')
          .replace('</quick_question>', '')
      }
    }
  })
  return result
}
const split_html_rander = (result: Array<any>) => {
  return result
    .map((item) => split_html_rander_(item.content, item.type))
    .reduce((x: any, y: any) => {
      return [...x, ...y]
    }, [])
}

const split_html_rander_ = (source: string, type: string) => {
  const temp_md_quick_question_list = source.match(/<html_rander>[\d\D]*?<\/html_rander>/g)
  const md_quick_question_list = temp_md_quick_question_list
    ? temp_md_quick_question_list.filter((i) => i)
    : []
  const split_quick_question_value = source
    .split(/<html_rander>[\d\D]*?<\/html_rander>/g)
    .filter((item) => item !== undefined)
    .filter((item) => !md_quick_question_list?.includes(item))
  const result = Array.from(
    { length: md_quick_question_list.length + split_quick_question_value.length },
    (v, i) => i
  ).map((index) => {
    if (index % 2 == 0) {
      return { type: type, content: split_quick_question_value[Math.floor(index / 2)] }
    } else {
      return {
        type: 'html_rander',
        content: md_quick_question_list[Math.floor(index / 2)]
          .replace('<html_rander>', '')
          .replace('</html_rander>', '')
      }
    }
  })
  return result
}

const split_echarts_rander = (result: Array<any>) => {
  return result
    .map((item) => split_echarts_rander_(item.content, item.type))
    .reduce((x: any, y: any) => {
      return [...x, ...y]
    }, [])
}

const split_echarts_rander_ = (source: string, type: string) => {
  const temp_md_quick_question_list = source.match(/<echarts_rander>[\d\D]*?<\/echarts_rander>/g)
  const md_quick_question_list = temp_md_quick_question_list
    ? temp_md_quick_question_list.filter((i) => i)
    : []
  const split_quick_question_value = source
    .split(/<echarts_rander>[\d\D]*?<\/echarts_rander>/g)
    .filter((item) => item !== undefined)
    .filter((item) => !md_quick_question_list?.includes(item))
  const result = Array.from(
    { length: md_quick_question_list.length + split_quick_question_value.length },
    (v, i) => i
  ).map((index) => {
    if (index % 2 == 0) {
      return { type: type, content: split_quick_question_value[Math.floor(index / 2)] }
    } else {
      return {
        type: 'echarts_rander',
        content: md_quick_question_list[Math.floor(index / 2)]
          .replace('<echarts_rander>', '')
          .replace('</echarts_rander>', '')
      }
    }
  })
  return result
}

const split_form_rander = (result: Array<any>) => {
  return result
    .map((item) => split_form_rander_(item.content, item.type))
    .reduce((x: any, y: any) => {
      return [...x, ...y]
    }, [])
}

const split_form_rander_ = (source: string, type: string) => {
  const temp_md_quick_question_list = source.match(/<form_rander>[\d\D]*?<\/form_rander>/g)
  const md_quick_question_list = temp_md_quick_question_list
    ? temp_md_quick_question_list.filter((i) => i)
    : []
  const split_quick_question_value = source
    .split(/<form_rander>[\d\D]*?<\/form_rander>/g)
    .filter((item) => item !== undefined)
    .filter((item) => !md_quick_question_list?.includes(item))
  const result = Array.from(
    { length: md_quick_question_list.length + split_quick_question_value.length },
    (v, i) => i
  ).map((index) => {
    if (index % 2 == 0) {
      return { type: type, content: split_quick_question_value[Math.floor(index / 2)] }
    } else {
      return {
        type: 'form_rander',
        content: md_quick_question_list[Math.floor(index / 2)]
          .replace('<form_rander>', '')
          .replace('</form_rander>', '')
      }
    }
  })
  return result
}
</script>
<style lang="scss" scoped>
.problem-button {
  width: 100%;
  border: none;
  border-radius: 8px;
  background: var(--app-layout-bg-color);
  padding: 12px;
  box-sizing: border-box;
  color: var(--el-text-color-regular);
  word-break: break-all;

  &:hover {
    background: var(--el-color-primary-light-9);
  }

  &.disabled {
    &:hover {
      background: var(--app-layout-bg-color);
    }
  }

  :deep(.el-icon) {
    color: var(--el-color-primary);
  }
}
</style>
