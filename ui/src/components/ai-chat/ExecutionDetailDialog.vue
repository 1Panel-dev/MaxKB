<template>
  <el-dialog
    class="execution-details-dialog responsive-dialog"
    :title="$t('chat.executionDetails.title')"
    v-model="dialogVisible"
    destroy-on-close
    append-to-body
    align-center
    @click.stop
  >
    <el-scrollbar>
      <div class="execution-details">
        <template v-for="(item, index) in arraySort(detail, 'index')" :key="index">
          <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
            <div class="flex-between cursor" @click="current = current === index ? '' : index">
              <div class="flex align-center">
                <el-icon class="mr-8 arrow-icon" :class="current === index ? 'rotate-90' : ''">
                  <CaretRight />
                </el-icon>
                <component
                  :is="iconComponent(`${item.type}-icon`)"
                  class="mr-8"
                  :size="24"
                  :item="item.info"
                />
                <h4>{{ item.name }}</h4>
              </div>
              <div class="flex align-center">
                <span
                  class="mr-16 color-secondary"
                  v-if="
                    item.type === WorkflowType.Question ||
                    item.type === WorkflowType.AiChat ||
                    item.type === WorkflowType.ImageUnderstandNode ||
                    item.type === WorkflowType.ImageGenerateNode ||
                    item.type === WorkflowType.Application
                  "
                  >{{ item?.message_tokens + item?.answer_tokens }} tokens</span
                >
                <span class="mr-16 color-secondary">{{ item?.run_time?.toFixed(2) || 0.0 }} s</span>
                <el-icon class="success" :size="16" v-if="item.status === 200">
                  <CircleCheck />
                </el-icon>
                <el-icon class="danger" :size="16" v-else>
                  <CircleClose />
                </el-icon>
              </div>
            </div>
            <el-collapse-transition>
              <div class="mt-12" v-if="current === index">
                <template v-if="item.status === 200">
                  <!-- 开始 -->
                  <template
                    v-if="
                      item.type === WorkflowType.Start || item.type === WorkflowType.Application
                    "
                  >
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.inputParam') }}
                      </h5>

                      <div class="p-8-12 border-t-dashed lighter">
                        <div class="mb-8">
                          <span class="color-secondary">
                            {{ $t('chat.paragraphSource.question') }}:</span
                          >

                          {{ item.question || '-' }}
                        </div>

                        <div v-for="(f, i) in item.global_fields" :key="i" class="mb-8">
                          <span class="color-secondary">{{ f.label }}:</span> {{ f.value }}
                        </div>
                        <div v-if="item.document_list?.length > 0">
                          <p class="mb-8 color-secondary">
                            {{ $t('common.fileUpload.document') }}:
                          </p>

                          <el-space wrap>
                            <template v-for="(f, i) in item.document_list" :key="i">
                              <el-card
                                shadow="never"
                                style="--el-card-padding: 8px"
                                class="file cursor"
                              >
                                <div class="flex align-center">
                                  <img :src="getImgUrl(f && f?.name)" alt="" width="24" />
                                  <div class="ml-4 ellipsis" :title="f && f?.name">
                                    {{ f && f?.name }}
                                  </div>
                                </div>
                              </el-card>
                            </template>
                          </el-space>
                        </div>
                        <div v-if="item.image_list?.length > 0">
                          <p class="mb-8 color-secondary">{{ $t('common.fileUpload.image') }}:</p>

                          <el-space wrap>
                            <template v-for="(f, i) in item.image_list" :key="i">
                              <el-image
                                :src="f.url"
                                alt=""
                                fit="cover"
                                style="width: 40px; height: 40px; display: block"
                                class="border-r-4"
                              />
                            </template>
                          </el-space>
                        </div>
                        <div v-if="item.audio_list?.length > 0">
                          <p class="mb-8 color-secondary">
                            {{ $t('chat.executionDetails.audioFile') }}:
                          </p>

                          <el-space wrap>
                            <template v-for="(f, i) in item.audio_list" :key="i">
                              <audio
                                :src="f.url"
                                controls
                                style="width: 300px; height: 43px"
                                class="border-r-4"
                              />
                            </template>
                          </el-space>
                        </div>
                        <div v-if="item.other_list?.length > 0">
                          <p class="mb-8 color-secondary">
                            {{ $t('common.fileUpload.document') }}:
                          </p>

                          <el-space wrap>
                            <template v-for="(f, i) in item.other_list" :key="i">
                              <el-card
                                shadow="never"
                                style="--el-card-padding: 8px"
                                class="file cursor"
                              >
                                <div class="flex align-center">
                                  <img :src="getImgUrl(f && f?.name)" alt="" width="24" />
                                  <div class="ml-4 ellipsis" :title="f && f?.name">
                                    {{ f && f?.name }}
                                  </div>
                                </div>
                              </el-card>
                            </template>
                          </el-space>
                        </div>
                      </div>
                    </div>
                  </template>
                  <!-- 知识库检索 -->
                  <template v-if="item.type == WorkflowType.SearchDataset">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.searchContent') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">{{ item.question || '-' }}</div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.searchResult') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.paragraph_list?.length > 0">
                          <template
                            v-for="(paragraph, paragraphIndex) in arraySort(
                              item.paragraph_list,
                              'similarity',
                              true
                            )"
                            :key="paragraphIndex"
                          >
                            <ParagraphCard
                              :data="paragraph"
                              :content="paragraph.content"
                              :index="paragraphIndex"
                            />
                          </template>
                        </template>
                        <template v-else> -</template>
                      </div>
                    </div>
                  </template>
                  <!-- 判断器 -->
                  <template v-if="item.type == WorkflowType.Condition">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.conditionResult') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.branch_name || '-' }}
                      </div>
                    </div>
                  </template>
                  <!-- AI 对话 / 问题优化-->
                  <template
                    v-if="
                      item.type == WorkflowType.AiChat ||
                      item.type == WorkflowType.Question ||
                      item.type == WorkflowType.Application
                    "
                  >
                    <div
                      class="card-never border-r-4"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">
                        {{ $t('views.application.applicationForm.form.roleSettings.label') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.system || '-' }}
                      </div>
                    </div>
                    <div
                      class="card-never border-r-4 mt-8"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">{{ $t('chat.history') }}</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.history_message?.length > 0">
                          <p
                            class="mt-4 mb-4"
                            v-for="(history, historyIndex) in item.history_message"
                            :key="historyIndex"
                          >
                            <span class="color-secondary mr-4">{{ history.role }}:</span
                            ><span>{{ history.content }}</span>
                          </p>
                        </template>
                        <template v-else> -</template>
                      </div>
                    </div>
                    <div
                      class="card-never border-r-4 mt-8"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8" v-if="item.type == WorkflowType.AiChat">
                      <h5 class="p-8-12">
                        {{ $t('views.applicationWorkflow.nodes.aiChatNode.think') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.reasoning_content || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{
                          item.type == WorkflowType.Application
                            ? $t('common.param.outputParam')
                            : $t('chat.executionDetails.answer')
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <MdPreview
                          v-if="item.answer"
                          ref="editorRef"
                          editorId="preview-only"
                          :modelValue="item.answer"
                          style="background: none"
                          noImgZoomIn
                        />
                        <template v-else> -</template>
                      </div>
                    </div>
                  </template>

                  <!-- 指定回复 -->
                  <template v-if="item.type === WorkflowType.Reply">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.replyContent') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <el-scrollbar height="150">
                          <MdPreview
                            v-if="item.answer"
                            ref="editorRef"
                            editorId="preview-only"
                            :modelValue="item.answer"
                            style="background: none"
                            noImgZoomIn
                          />
                          <template v-else> -</template>
                        </el-scrollbar>
                      </div>
                    </div>
                  </template>

                  <!-- 文档内容提取 -->
                  <template v-if="item.type === WorkflowType.DocumentExtractNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12 flex align-center">
                        <span class="mr-4"> {{ $t('common.param.outputParam') }}</span>

                        <el-tooltip
                          effect="dark"
                          :content="$t('chat.executionDetails.paramOutputTooltip')"
                          placement="right"
                        >
                          <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                        </el-tooltip>
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <el-scrollbar height="150">
                          <el-card
                            shadow="never"
                            style="--el-card-padding: 8px"
                            v-for="(file_content, index) in item.content"
                            :key="index"
                            class="mb-8"
                          >
                            <MdPreview
                              v-if="file_content"
                              ref="editorRef"
                              editorId="preview-only"
                              :modelValue="file_content"
                              style="background: none"
                              noImgZoomIn
                            />
                            <template v-else> -</template>
                          </el-card>
                        </el-scrollbar>
                      </div>
                    </div>
                  </template>
                  <template v-if="item.type === WorkflowType.SpeechToTextNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.inputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div class="mb-8">
                          <div v-if="item.audio_list?.length > 0">
                            <p class="mb-8 color-secondary">
                              {{ $t('chat.executionDetails.audioFile') }}:
                            </p>

                            <el-space wrap>
                              <template v-for="(f, i) in item.audio_list" :key="i">
                                <audio
                                  :src="f.url"
                                  controls
                                  style="width: 300px; height: 43px"
                                  class="border-r-4"
                                />
                              </template>
                            </el-space>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.outputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <el-card
                          shadow="never"
                          style="--el-card-padding: 8px"
                          v-for="(file_content, index) in item.content"
                          :key="index"
                          class="mb-8"
                        >
                          <MdPreview
                            v-if="file_content"
                            ref="editorRef"
                            editorId="preview-only"
                            :modelValue="file_content"
                            style="background: none"
                            noImgZoomIn
                          />
                          <template v-else> -</template>
                        </el-card>
                      </div>
                    </div>
                  </template>

                  <template v-if="item.type === WorkflowType.TextToSpeechNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.inputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div class="p-8-12 border-t-dashed lighter">
                          <p class="mb-8 color-secondary">
                            {{ $t('chat.executionDetails.textContent') }}:
                          </p>
                          <div v-if="item.content">
                            <MdPreview
                              ref="editorRef"
                              editorId="preview-only"
                              :modelValue="item.content"
                              style="background: none"
                              noImgZoomIn
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.outputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <p class="mb-8 color-secondary">
                          {{ $t('chat.executionDetails.audioFile') }}:
                        </p>
                        <div v-if="item.answer" v-html="item.answer"></div>
                      </div>
                    </div>
                  </template>

                  <!-- 函数库 -->
                  <template
                    v-if="
                      item.type === WorkflowType.FunctionLib ||
                      item.type === WorkflowType.FunctionLibCustom
                    "
                  >
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">{{ $t('chat.executionDetails.input') }}</h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.params || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">{{ $t('chat.executionDetails.output') }}</h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.result || '-' }}
                      </div>
                    </div>
                  </template>
                  <!-- 多路召回 -->
                  <template v-if="item.type == WorkflowType.RrerankerNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.searchContent') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">{{ item.question || '-' }}</div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.rerankerContent') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.document_list?.length > 0">
                          <template
                            v-for="(paragraph, paragraphIndex) in item.document_list"
                            :key="paragraphIndex"
                          >
                            <ParagraphCard
                              :data="paragraph.metadata"
                              :content="paragraph.page_content"
                              :index="paragraphIndex"
                            />
                          </template>
                        </template>
                        <template v-else> -</template>
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.rerankerResult') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.result_list?.length > 0">
                          <template
                            v-for="(paragraph, paragraphIndex) in item.result_list"
                            :key="paragraphIndex"
                          >
                            <ParagraphCard
                              :data="paragraph.metadata"
                              :content="paragraph.page_content"
                              :index="paragraphIndex"
                              :score="paragraph.metadata?.relevance_score"
                            />
                          </template>
                        </template>
                        <template v-else> -</template>
                      </div>
                    </div>
                  </template>

                  <!-- 表单收集 -->
                  <template v-if="item.type === WorkflowType.FormNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.outputParam')
                        }}<span style="color: #f54a45">{{
                          item.is_submit ? '' : `(${$t('chat.executionDetails.noSubmit')})`
                        }}</span>
                      </h5>

                      <div class="p-8-12 border-t-dashed lighter">
                        <DynamicsForm
                          :disabled="true"
                          label-position="top"
                          require-asterisk-position="right"
                          ref="dynamicsFormRef"
                          :render_data="item.form_field_list"
                          label-suffix=":"
                          v-model="item.form_data"
                          :model="item.form_data"
                        ></DynamicsForm>
                      </div>
                    </div>
                  </template>
                  <!-- 图片理解 -->
                  <template v-if="item.type == WorkflowType.ImageUnderstandNode">
                    <div
                      class="card-never border-r-4"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">
                        {{ $t('views.application.applicationForm.form.roleSettings.label') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.system || '-' }}
                      </div>
                    </div>
                    <div
                      class="card-never border-r-4 mt-8"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">{{ $t('chat.history') }}</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.history_message?.length > 0">
                          <p
                            class="mt-4 mb-4"
                            v-for="(history, historyIndex) in item.history_message"
                            :key="historyIndex"
                          >
                            <span class="color-secondary mr-4">{{ history.role }}:</span>

                            <span v-if="Array.isArray(history.content)">
                              <template v-for="(h, i) in history.content" :key="i">
                                <el-image
                                  v-if="h.type === 'image_url'"
                                  :src="h.image_url.url"
                                  alt=""
                                  fit="cover"
                                  style="width: 40px; height: 40px; display: inline-block"
                                  class="border-r-4 mr-8"
                                />

                                <span v-else>{{ h.text }}<br /></span>
                              </template>
                            </span>

                            <span v-else>{{ history.content }}</span>
                          </p>
                        </template>
                        <template v-else> -</template>
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        <div v-if="item.image_list?.length > 0">
                          <el-space wrap>
                            <template v-for="(f, i) in item.image_list" :key="i">
                              <el-image
                                :src="f.url"
                                alt=""
                                fit="cover"
                                style="width: 40px; height: 40px; display: block"
                                class="border-r-4"
                              />
                            </template>
                          </el-space>
                        </div>
                        <div>
                          {{ item.question || '-' }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{
                          item.type == WorkflowType.Application
                            ? $t('common.param.outputParam')
                            : $t('chat.executionDetails.answer')
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <MdPreview
                          v-if="item.answer"
                          ref="editorRef"
                          editorId="preview-only"
                          :modelValue="item.answer"
                          style="background: none"
                          noImgZoomIn
                        />
                        <template v-else> -</template>
                      </div>
                    </div>
                  </template>
                  <!-- 图片生成 -->
                  <template v-if="item.type == WorkflowType.ImageGenerateNode">
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">
                        {{
                          item.type == WorkflowType.Application
                            ? $t('common.param.outputParam')
                            : $t('chat.executionDetails.answer')
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <MdPreview
                          v-if="item.answer"
                          ref="editorRef"
                          editorId="preview-only"
                          :modelValue="item.answer"
                          style="background: none"
                          noImgZoomIn
                        />
                        <template v-else> -</template>
                      </div>
                    </div>
                  </template>

                  <!-- 变量赋值 -->
                  <template v-if="item.type === WorkflowType.VariableAssignNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.inputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div v-for="(f, i) in item.result_list" :key="i" class="mb-8">
                          <span class="color-secondary">{{ f.name }}:</span> {{ f.input_value }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.outputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div v-for="(f, i) in item.result_list" :key="i" class="mb-8">
                          <span class="color-secondary">{{ f.name }}:</span> {{ f.output_value }}
                        </div>
                      </div>
                    </div>
                  </template>

                  <!-- MCP 节点 -->
                  <template v-if="item.type === WorkflowType.McpNode">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('views.applicationWorkflow.nodes.mcpNode.tool') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div class="mb-8">
                          <span class="color-secondary"> {{ $t('views.applicationWorkflow.nodes.mcpNode.tool') }}: </span> {{ item.mcp_tool }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('views.applicationWorkflow.nodes.mcpNode.toolParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div v-for="(value, name) in item.tool_params" :key="name" class="mb-8">
                          <span class="color-secondary">{{ name }}:</span> {{ value }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">
                        {{ $t('common.param.outputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div v-for="(f, i) in item.result" :key="i" class="mb-8">
                          <span class="color-secondary">result:</span> {{ f }}
                        </div>
                      </div>
                    </div>
                  </template>
                </template>
                <template v-else>
                  <div class="card-never border-r-4">
                    <h5 class="p-8-12">{{ $t('chat.executionDetails.errMessage') }}</h5>
                    <div class="p-8-12 border-t-dashed lighter">{{ item.err_message || '-' }}</div>
                  </div>
                </template>
              </div>
            </el-collapse-transition>
          </el-card>
        </template>
      </div>
    </el-scrollbar>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { cloneDeep } from 'lodash'
import ParagraphCard from './component/ParagraphCard.vue'
import { arraySort } from '@/utils/utils'
import { iconComponent } from '@/workflow/icons/utils'
import { WorkflowType } from '@/enums/workflow'
import { getImgUrl } from '@/utils/utils'
import DynamicsForm from '@/components/dynamics-form/index.vue'

const dialogVisible = ref(false)
const detail = ref<any[]>([])

const current = ref<number | string>('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = []
  }
})

const open = (data: any) => {
  detail.value = cloneDeep(data)
  dialogVisible.value = true
}
onBeforeUnmount(() => {
  dialogVisible.value = false
})
defineExpose({ open })
</script>
<style lang="scss">
.execution-details-dialog {

  .el-dialog__header {
    padding-bottom: 16px;
  }

  .execution-details {
    max-height: calc(100vh - 260px);

    .arrow-icon {
      transition: 0.2s;
    }
  }
}


</style>
