<template>
  <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
    <div class="flex-between cursor" @click="data['show'] = !data['show']">
      <div class="flex align-center">
        <el-icon class="mr-8 arrow-icon" :class="data['show'] ? 'rotate-90' : ''">
          <CaretRight />
        </el-icon>
        <component
          :is="iconComponent(`${data.type}-icon`)"
          class="mr-8"
          :size="24"
          :item="data.info"
        />
        <h4>{{ data.name }}</h4>
      </div>
      <div class="flex align-center">
        <span
          class="mr-16 color-secondary"
          v-if="
            data.type === WorkflowType.Question ||
            data.type === WorkflowType.AiChat ||
            data.type === WorkflowType.ImageUnderstandNode ||
            data.type === WorkflowType.ImageGenerateNode ||
            data.type === WorkflowType.Application ||
            data.type == WorkflowType.IntentNode ||
            data.type === WorkflowType.VideoUnderstandNode
          "
          >{{ data?.message_tokens + data?.answer_tokens }} tokens</span
        >
        <span class="mr-16 color-secondary">{{ data?.run_time?.toFixed(2) || 0.0 }} s</span>
        <el-icon class="color-success" :size="16" v-if="data.status === 200">
          <CircleCheck />
        </el-icon>
        <el-icon class="color-danger" :size="16" v-else>
          <CircleClose />
        </el-icon>
      </div>
    </div>
    <el-collapse-transition>
      <div class="mt-12" v-if="data['show']">
        <template v-if="data.status === 200 || data.type == WorkflowType.LoopNode">
          <!-- 开始 -->
          <template
            v-if="data.type === WorkflowType.Start || data.type === WorkflowType.Application"
          >
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.inputParam') }}
              </h5>

              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <span class="color-secondary"> {{ $t('chat.paragraphSource.question') }}:</span>

                  {{ data.question || '-' }}
                </div>

                <div v-for="(f, i) in data.global_fields" :key="i" class="mb-8">
                  <span class="color-secondary">{{ f.label }}:</span> {{ f.value }}
                </div>
                <div v-if="data.document_list?.length > 0">
                  <p class="mb-8 color-secondary">{{ $t('common.fileUpload.document') }}:</p>

                  <el-space wrap>
                    <template v-for="(f, i) in data.document_list" :key="i">
                      <el-card shadow="never" style="--el-card-padding: 8px" class="file cursor">
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
                <div v-if="data.image_list?.length > 0">
                  <p class="mb-8 color-secondary">{{ $t('common.fileUpload.image') }}:</p>

                  <el-space wrap>
                    <template v-for="(f, i) in data.image_list" :key="i">
                      <el-image
                        :src="f.url"
                        alt=""
                        fit="cover"
                        style="width: 40px; height: 40px; display: block"
                        class="border-r-6"
                      />
                    </template>
                  </el-space>
                </div>
                <div v-if="data.audio_list?.length > 0">
                  <p class="mb-8 color-secondary">{{ $t('chat.executionDetails.audioFile') }}:</p>

                  <el-space wrap>
                    <template v-for="(f, i) in data.audio_list" :key="i">
                      <audio
                        :src="f.url"
                        controls
                        style="width: 300px; height: 43px"
                        class="border-r-6"
                      />
                    </template>
                  </el-space>
                </div>
                <div v-if="data.video_list?.length > 0">
                  <p class="mb-8 color-secondary">{{ $t('common.fileUpload.image') }}:</p>

                  <el-space wrap>
                    <template v-for="(f, i) in data.video_list" :key="i">
                      <video
                        :src="f.url"
                        style="width: 170px; display: block"
                        controls
                        autoplay
                        class="border-r-6"
                      />
                    </template>
                  </el-space>
                </div>
                <div v-if="data.other_list?.length > 0">
                  <p class="mb-8 color-secondary">{{ $t('common.fileUpload.document') }}:</p>

                  <el-space wrap>
                    <template v-for="(f, i) in data.other_list" :key="i">
                      <el-card shadow="never" style="--el-card-padding: 8px" class="file cursor">
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
          <template v-if="data.type == WorkflowType.SearchKnowledge">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.searchContent') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">{{ data.question || '-' }}</div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.searchResult') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <template v-if="data.paragraph_list?.length > 0">
                  <template
                    v-for="(paragraph, paragraphIndex) in arraySort(
                      data.paragraph_list,
                      'similarity',
                      true,
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
          <template v-if="data.type == WorkflowType.Condition">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.conditionResult') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                {{ data.branch_name || '-' }}
              </div>
            </div>
          </template>
          <!-- AI 对话 / 问题优化 / 意图识别-->
          <template
            v-if="
              data.type == WorkflowType.AiChat ||
              data.type == WorkflowType.Question ||
              data.type == WorkflowType.Application ||
              data.type == WorkflowType.IntentNode
            "
          >
            <div class="card-never border-r-6" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">
                {{ $t('views.application.form.roleSettings.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                {{ data.system || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">{{ $t('chat.history') }}</h5>
              <div class="p-8-12 border-t-dashed lighter">
                <template v-if="data.history_message?.length > 0">
                  <p
                    class="mt-4 mb-4"
                    v-for="(history, historyIndex) in data.history_message"
                    :key="historyIndex"
                  >
                    <span class="color-secondary mr-4">{{ history.role }}:</span
                    ><span>{{ history.content }}</span>
                  </p>
                </template>
                <template v-else> -</template>
              </div>
            </div>
            <div class="card-never border-r-6 mt-8" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.currentChat') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.question || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8" v-if="data.type == WorkflowType.AiChat">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.aiChatNode.think') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.reasoning_content || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{
                  data.type == WorkflowType.Application
                    ? $t('common.param.outputParam')
                    : $t('chat.executionDetails.answer')
                }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <MdPreview
                  v-if="data.answer"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="data.answer"
                  style="background: none"
                  noImgZoomIn
                />
                <template v-else> -</template>
              </div>
            </div>
          </template>

          <!-- 指定回复 -->
          <template v-if="data.type === WorkflowType.Reply">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.replyContent') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <el-scrollbar height="150">
                  <MdPreview
                    v-if="data.answer"
                    ref="editorRef"
                    editorId="preview-only"
                    :modelValue="data.answer"
                    style="background: none"
                    noImgZoomIn
                  />
                  <template v-else> -</template>
                </el-scrollbar>
              </div>
            </div>
          </template>

          <!-- 文档内容提取 -->
          <template v-if="data.type === WorkflowType.DocumentExtractNode">
            <div class="card-never border-r-6">
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
                    v-for="(file_content, index) in data.content"
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
          <template v-if="data.type === WorkflowType.SpeechToTextNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.inputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <div v-if="data.audio_list?.length > 0">
                    <p class="mb-8 color-secondary">{{ $t('chat.executionDetails.audioFile') }}:</p>

                    <el-space wrap>
                      <template v-for="(f, i) in data.audio_list" :key="i">
                        <audio
                          :src="f.url"
                          controls
                          style="width: 300px; height: 43px"
                          class="border-r-6"
                        />
                      </template>
                    </el-space>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <el-card
                  shadow="never"
                  style="--el-card-padding: 8px"
                  v-for="(file_content, index) in data.content"
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

          <template v-if="data.type === WorkflowType.TextToSpeechNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.inputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div class="p-8-12 border-t-dashed lighter">
                  <p class="mb-8 color-secondary">{{ $t('chat.executionDetails.textContent') }}:</p>
                  <div v-if="data.content">
                    <MdPreview
                      ref="editorRef"
                      editorId="preview-only"
                      :modelValue="data.content"
                      style="background: none"
                      noImgZoomIn
                    />
                  </div>
                </div>
              </div>
            </div>
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <p class="mb-8 color-secondary">{{ $t('chat.executionDetails.audioFile') }}:</p>
                <div v-if="data.answer" v-html="data.answer"></div>
              </div>
            </div>
          </template>

          <!-- 工具库 -->
          <template
            v-if="data.type === WorkflowType.ToolLib || data.type === WorkflowType.ToolLibCustom"
          >
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">{{ $t('chat.executionDetails.input') }}</h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.params || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">{{ $t('chat.executionDetails.output') }}</h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.result || '-' }}
              </div>
            </div>
          </template>
          <!-- 多路召回 -->
          <template v-if="data.type == WorkflowType.RerankerNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.searchContent') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">{{ data.question || '-' }}</div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.rerankerContent') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <template v-if="data.document_list?.length > 0">
                  <template
                    v-for="(paragraph, paragraphIndex) in data.document_list"
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
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.rerankerResult') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <template v-if="data.result_list?.length > 0">
                  <template
                    v-for="(paragraph, paragraphIndex) in data.result_list"
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
          <template v-if="data.type === WorkflowType.FormNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam')
                }}<span style="color: #f54a45">{{
                  data.is_submit ? '' : `(${$t('chat.executionDetails.noSubmit')})`
                }}</span>
              </h5>

              <div class="p-8-12 border-t-dashed lighter">
                <DynamicsForm
                  :disabled="true"
                  label-position="top"
                  require-asterisk-position="right"
                  ref="dynamicsFormRef"
                  :render_data="data.form_field_list"
                  label-suffix=":"
                  v-model="data.form_data"
                  :model="data.form_data"
                ></DynamicsForm>
              </div>
            </div>
          </template>
          <!-- 图片理解 -->
          <template v-if="data.type == WorkflowType.ImageUnderstandNode">
            <div class="card-never border-r-6" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">
                {{ $t('views.application.form.roleSettings.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                {{ data.system || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">{{ $t('chat.history') }}</h5>
              <div class="p-8-12 border-t-dashed lighter">
                <template v-if="data.history_message?.length > 0">
                  <p
                    class="mt-4 mb-4"
                    v-for="(history, historyIndex) in data.history_message"
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
                          class="border-r-6 mr-8"
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
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.currentChat') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                <div v-if="data.image_list?.length > 0">
                  <el-space wrap>
                    <template v-for="(f, i) in data.image_list" :key="i">
                      <el-image
                        :src="f.url"
                        alt=""
                        fit="cover"
                        style="width: 40px; height: 40px; display: block"
                        class="border-r-6"
                      />
                    </template>
                  </el-space>
                </div>
                <div>
                  {{ data.question || '-' }}
                </div>
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{
                  data.type == WorkflowType.Application
                    ? $t('common.param.outputParam')
                    : $t('chat.executionDetails.answer')
                }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <MdPreview
                  v-if="data.answer"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="data.answer"
                  style="background: none"
                  noImgZoomIn
                />
                <template v-else> -</template>
              </div>
            </div>
          </template>
          <!-- 视频理解 -->
          <template v-if="data.type == WorkflowType.VideoUnderstandNode">
            <div class="card-never border-r-6" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">
                {{ $t('views.application.form.roleSettings.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                {{ data.system || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8" v-if="data.type !== WorkflowType.Application">
              <h5 class="p-8-12">{{ $t('chat.history') }}</h5>
              <div class="p-8-12 border-t-dashed lighter">
                <template v-if="data.history_message?.length > 0">
                  <p
                    class="mt-4 mb-4"
                    v-for="(history, historyIndex) in data.history_message"
                    :key="historyIndex"
                  >
                    <span class="color-secondary mr-4">{{ history.role }}:</span>

                    <span v-if="Array.isArray(history.content)">
                      <template v-for="(h, i) in history.content" :key="i">
                        <video
                          v-if="h.type === 'video_url'"
                          :src="h.video_url.url"
                          style="width: 40px; height: 40px; display: inline-block"
                          class="border-r-6 mr-8"
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
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.currentChat') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                <div v-if="data.video_list?.length > 0">
                  <el-space wrap>
                    <template v-for="(f, i) in data.video_list" :key="i">
                      <video
                        :src="f.url"
                        style="width: 100px; display: block"
                        class="border-r-6"
                        autoplay
                        controls
                      />
                    </template>
                  </el-space>
                </div>
                <div>
                  {{ data.question || '-' }}
                </div>
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{
                  data.type == WorkflowType.Application
                    ? $t('common.param.outputParam')
                    : $t('chat.executionDetails.answer')
                }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <MdPreview
                  v-if="data.answer"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="data.answer"
                  style="background: none"
                  noImgZoomIn
                />
                <template v-else> -</template>
              </div>
            </div>
          </template>
          <!-- 图片生成 -->
          <template v-if="data.type == WorkflowType.ImageGenerateNode">
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.currentChat') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.question || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.negative_prompt || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{
                  data.type == WorkflowType.Application
                    ? $t('common.param.outputParam')
                    : $t('chat.executionDetails.answer')
                }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <MdPreview
                  v-if="data.answer"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="data.answer"
                  style="background: none"
                  noImgZoomIn
                />
                <template v-else> -</template>
              </div>
            </div>
          </template>
          <template v-if="data.type == WorkflowType.TextToVideoGenerateNode">
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.currentChat') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.question || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.negative_prompt || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{
                  data.type == WorkflowType.Application
                    ? $t('common.param.outputParam')
                    : $t('chat.executionDetails.answer')
                }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <MdPreview
                  v-if="data.answer"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="data.answer"
                  style="background: none"
                  noImgZoomIn
                />
                <template v-else> -</template>
              </div>
            </div>
          </template>

          <template v-if="data.type == WorkflowType.ImageToVideoGenerateNode">
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('chat.executionDetails.currentChat') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.question || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.negative_prompt || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.imageToVideoGenerate.first_frame.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                <div v-if="typeof data.first_frame_url === 'string'">
                  <el-image
                    :src="data.first_frame_url"
                    alt=""
                    fit="cover"
                    style="width: 40px; height: 40px; display: block"
                    class="border-r-6"
                  />
                </div>
                <div v-else-if="Array.isArray(data.first_frame_url)">
                  <el-space wrap>
                    <template v-for="(f, i) in data.first_frame_url" :key="i">
                      <el-image
                        :src="f.url"
                        alt=""
                        fit="cover"
                        style="width: 40px; height: 40px; display: block"
                        class="border-r-6"
                      />
                    </template>
                  </el-space>
                </div>
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.imageToVideoGenerate.last_frame.label') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                <div v-if="typeof data.last_frame_url === 'string'">
                  <el-image
                    :src="data.last_frame_url"
                    alt=""
                    fit="cover"
                    style="width: 40px; height: 40px; display: block"
                    class="border-r-6"
                  />
                </div>
                <div v-else-if="Array.isArray(data.last_frame_url)">
                  <el-space wrap>
                    <template v-for="(f, i) in data.last_frame_url" :key="i">
                      <el-image
                        :src="f.url"
                        alt=""
                        fit="cover"
                        style="width: 40px; height: 40px; display: block"
                        class="border-r-6"
                      />
                    </template>
                  </el-space>
                </div>
                <div v-else>-</div>
              </div>
            </div>

            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{
                  data.type == WorkflowType.Application
                    ? $t('common.param.outputParam')
                    : $t('chat.executionDetails.answer')
                }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <MdPreview
                  v-if="data.answer"
                  ref="editorRef"
                  editorId="preview-only"
                  :modelValue="data.answer"
                  style="background: none"
                  noImgZoomIn
                />
                <template v-else> -</template>
              </div>
            </div>
          </template>
          <!-- 变量赋值 -->
          <template v-if="data.type === WorkflowType.VariableAssignNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.inputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(f, i) in data.result_list" :key="i" class="mb-8">
                  <span class="color-secondary">{{ f.name }}:</span> {{ f.input_value }}
                </div>
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(f, i) in data.result_list" :key="i" class="mb-8">
                  <span class="color-secondary">{{ f.name }}:</span> {{ f.output_value }}
                </div>
              </div>
            </div>
          </template>

          <!-- 变量拆分 -->
          <template
            v-if="
              data.type === WorkflowType.VariableSplittingNode ||
              data.type == WorkflowType.ParameterExtractionNode
            "
          >
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.inputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.request || '-' }}
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(f, i) in data.result" :key="i" class="mb-8">
                  <span class="color-secondary">{{ i }}:</span> {{ f }}
                </div>
              </div>
            </div>
          </template>
          <!-- 变量聚合 -->
          <template v-if="data.type === WorkflowType.VariableAggregationNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.variableAggregationNode.Strategy') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter pre-wrap">
                {{ data.strategy }}
              </div>
            </div>
            <div
              class="card-never border-r-6 mt-8"
              v-for="(group, groupI) in data.group_list"
              :key="groupI"
            >
              <h5 class="p-8-12">
                {{ group.label+ ' '+ $t('common.param.inputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(f, i) in group.variable_list" :key="i" class="mb-8">
                  <span class="color-secondary">{{ `${f.node_name}.${f.field}` }}:</span> {{ f.value }}
                </div>
              </div>
            </div>
            <div class="card-never border-r-6 mt-8">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(f, i) in data.result" :key="i" class="mb-8">
                  <span class="color-secondary">{{ i }}:</span> {{ f }}
                </div>
              </div>
            </div>
          </template>
          <!-- MCP 节点 -->
          <template v-if="data.type === WorkflowType.McpNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('views.tool.title') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <span class="color-secondary"> {{ $t('views.tool.title') }}: </span>
                  {{ data.mcp_tool }}
                </div>
              </div>
            </div>
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('views.applicationWorkflow.nodes.mcpNode.toolParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(value, name) in data.tool_params" :key="name" class="mb-8">
                  <span class="color-secondary">{{ name }}:</span> {{ value }}
                </div>
              </div>
            </div>
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div v-for="(f, i) in data.result" :key="i" class="mb-8">
                  <span class="color-secondary">result:</span> {{ f }}
                </div>
              </div>
            </div>
          </template>
          <!-- 循环 节点 -->
          <div class="card-never border-r-6" v-if="data.type === WorkflowType.LoopNode">
            <h5 class="p-8-12">
              {{ $t('views.applicationWorkflow.nodes.loopNode.loopSetting') }}
            </h5>

            <div class="p-8-12 border-t-dashed lighter">
              <div class="mb-8">
                <span class="color-secondary">
                  {{ $t('views.applicationWorkflow.nodes.loopNode.loopType.label') }}:</span
                >
                {{ data.loop_type || '-' }}
              </div>
              <div>
                <span class="color-secondary">
                  {{ $t('views.applicationWorkflow.nodes.loopNode.loopArray.label') }}:</span
                >
                {{
                  data.loop_type === 'NUMBER'
                    ? data.number
                    : Object.keys(data.loop_node_data) || '-'
                }}
              </div>
            </div>
            <h5 class="p-8-12">
              {{ $t('views.applicationWorkflow.nodes.loopNode.loopDetail') }}
            </h5>
            <div class="p-8-12 border-t-dashed lighter">
              <template v-if="data.type === WorkflowType.LoopNode">
                <el-radio-group v-model="currentLoopNode" class="app-radio-button-group mb-8">
                  <template v-for="(loop, loopIndex) in data.loop_node_data" :key="loopIndex">
                    <el-radio-button :label="loopIndex" :value="loopIndex" />
                  </template>
                </el-radio-group>
                <template
                  v-for="(cLoop, cIndex) in Object.values(
                    data.loop_node_data?.[currentLoopNode] || [],
                  )"
                  :key="cIndex"
                >
                  <ExecutionDetailCard :data="cLoop"></ExecutionDetailCard>
                </template>
              </template>
            </div>
          </div>
          <!-- 循环开始 节点-->
          <template v-if="data.type === WorkflowType.LoopStartNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.inputParam') }}
              </h5>

              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <span class="color-secondary">
                    {{ $t('views.applicationWorkflow.nodes.loopStartNode.loopItem') }}:</span
                  >

                  {{ data.current_item }}
                </div>
                <div class="mb-8">
                  <span class="color-secondary">
                    {{ $t('views.applicationWorkflow.nodes.loopStartNode.loopIndex') }}:</span
                  >

                  {{ data.current_index }}
                </div>
              </div>
            </div>
          </template>
          <!-- 循环跳过 节点-->
          <template v-if="data.type === WorkflowType.LoopContinueNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>

              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <span class="color-secondary">
                    {{ $t('views.applicationWorkflow.nodes.loopContinueNode.isContinue') }}:</span
                  >

                  {{ data.is_continue }}
                </div>
              </div>
            </div>
          </template>
          <!-- 循环退出 节点-->
          <template v-if="data.type === WorkflowType.LoopBreakNode">
            <div class="card-never border-r-6">
              <h5 class="p-8-12">
                {{ $t('common.param.outputParam') }}
              </h5>

              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <span class="color-secondary">
                    {{ $t('views.applicationWorkflow.nodes.loopBreakNode.isBreak') }}:</span
                  >

                  {{ data.is_break }}
                </div>
              </div>
            </div>
          </template>
          <!-- 文档检索 -->
          <template v-if="data.type === WorkflowType.SearchDocument">
            <div class="card-never border-r-6">
              <h5 class="p-8-12 flex align-center">
                <span class="mr-4"> {{ $t('common.param.outputParam') }}</span>
              </h5>
              <div class="p-8-12 border-t-dashed lighter">
                <div class="mb-8">
                  <span class="color-secondary"> knowledge_list:</span>
                  {{ data.knowledge_items?.map((v: any) => v.name).join(',') }}
                </div>
                <div class="mb-8">
                  <span class="color-secondary"> document_list:</span>
                  {{ data.document_items?.map((v: any) => v.name).join(',') }}
                </div>
              </div>
            </div>
          </template>
          <slot></slot>
        </template>
        <template v-else>
          <div class="card-never border-r-6">
            <h5 class="p-8-12">{{ $t('chat.executionDetails.errMessage') }}</h5>
            <div class="p-8-12 border-t-dashed lighter">{{ data.err_message || '-' }}</div>
          </div>
        </template>
      </div>
    </el-collapse-transition>
  </el-card>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import ParagraphCard from '@/components/ai-chat/component/knowledge-source-component/ParagraphCard.vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import { iconComponent } from '@/workflow/icons/utils'
import { WorkflowType } from '@/enums/application'
import { getImgUrl } from '@/utils/common'
import { arraySort } from '@/utils/array'

import { t } from '@/locales'

const props = defineProps<{
  data: any
}>()
const currentLoopNode = ref(0)
</script>
<style lang="scss" scoped></style>
