<template>
  <el-scrollbar>
    <div class="execution-details p-8">
      <div v-if="isWorkFlow(props.appType)">
        <template v-for="(item, index) in arraySort(props.detail ?? [], 'index')" :key="index">
          <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
            <div class="flex-between cursor" @click="item['show'] = !item['show']">
              <div class="flex align-center">
                <el-icon class="mr-8 arrow-icon" :class="item['show'] ? 'rotate-90' : ''">
                  <CaretRight/>
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
                <el-icon class="color-success" :size="16" v-if="item.status === 200">
                  <CircleCheck/>
                </el-icon>
                <el-icon class="color-danger" :size="16" v-else>
                  <CircleClose/>
                </el-icon>
              </div>
            </div>
            <el-collapse-transition>
              <div class="mt-12" v-if="item['show']">
                <template v-if="item.status === 200">
                  <!-- 开始 -->
                  <template
                    v-if="
                      item.type === WorkflowType.Start || item.type === WorkflowType.Application
                    "
                  >
                    <div class="card-never border-r-6">
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
                                  <img :src="getImgUrl(f && f?.name)" alt="" width="24"/>
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
                                class="border-r-6"
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
                                class="border-r-6"
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
                                  <img :src="getImgUrl(f && f?.name)" alt="" width="24"/>
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
                  <template v-if="item.type == WorkflowType.SearchKnowledge">
                    <div class="card-never border-r-6">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.searchContent') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">{{ item.question || '-' }}</div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.searchResult') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.paragraph_list?.length > 0">
                          <template
                            v-for="(paragraph, paragraphIndex) in arraySort(
                              item.paragraph_list,
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
                  <template v-if="item.type == WorkflowType.Condition">
                    <div class="card-never border-r-6">
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
                      class="card-never border-r-6"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">
                        {{ $t('views.application.form.roleSettings.label') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.system || '-' }}
                      </div>
                    </div>
                    <div
                      class="card-never border-r-6 mt-8"
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
                      class="card-never border-r-6 mt-8"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8" v-if="item.type == WorkflowType.AiChat">
                      <h5 class="p-8-12">
                        {{ $t('views.applicationWorkflow.nodes.aiChatNode.think') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.reasoning_content || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
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
                    <div class="card-never border-r-6">
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
                    <div class="card-never border-r-6">
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
                    <div class="card-never border-r-6">
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
                    <div class="card-never border-r-6">
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

                  <!-- 工具库 -->
                  <template
                    v-if="
                      item.type === WorkflowType.ToolLib || item.type === WorkflowType.ToolLibCustom
                    "
                  >
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">{{ $t('chat.executionDetails.input') }}</h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.params || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">{{ $t('chat.executionDetails.output') }}</h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.result || '-' }}
                      </div>
                    </div>
                  </template>
                  <!-- 多路召回 -->
                  <template v-if="item.type == WorkflowType.RerankerNode">
                    <div class="card-never border-r-6">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.searchContent') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">{{ item.question || '-' }}</div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
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
                    <div class="card-never border-r-6 mt-8">
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
                    <div class="card-never border-r-6">
                      <h5 class="p-8-12">
                        {{
                          $t('common.param.outputParam')
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
                      class="card-never border-r-6"
                      v-if="item.type !== WorkflowType.Application"
                    >
                      <h5 class="p-8-12">
                        {{ $t('views.application.form.roleSettings.label') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.system || '-' }}
                      </div>
                    </div>
                    <div
                      class="card-never border-r-6 mt-8"
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
                                  class="border-r-6 mr-8"
                                />

                                <span v-else>{{ h.text }}<br/></span>
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
                        <div v-if="item.image_list?.length > 0">
                          <el-space wrap>
                            <template v-for="(f, i) in item.image_list" :key="i">
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
                          {{ item.question || '-' }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
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
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{
                          $t(
                            'views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label',
                          )
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.negative_prompt || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
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
                  <template v-if="item.type == WorkflowType.TextToVideoGenerateNode">
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{
                          $t(
                            'views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label',
                          )
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.negative_prompt || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
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

                  <template v-if="item.type == WorkflowType.ImageToVideoGenerateNode">
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{ $t('chat.executionDetails.currentChat') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{
                          $t(
                            'views.applicationWorkflow.nodes.imageGenerateNode.negative_prompt.label',
                          )
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">
                        {{ item.negative_prompt || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{
                          $t('views.applicationWorkflow.nodes.imageToVideoGenerate.first_frame.label')
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">

                        <div v-if="typeof item.first_frame_url === 'string'">
                          <el-image
                            :src="item.first_frame_url"
                            alt=""
                            fit="cover" style="width: 40px; height: 40px; display: block"
                            class="border-r-6"
                          />
                        </div>
                        <div v-else-if="Array.isArray(item.first_frame_url)">
                          <el-space wrap>
                            <template v-for="(f, i) in item.first_frame_url" :key="i">
                              <el-image
                                :src="f.url"
                                alt=""
                                fit="cover" style="width: 40px; height: 40px; display: block"
                                class="border-r-6"
                              />
                            </template>
                          </el-space>
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-6 mt-8">
                      <h5 class="p-8-12">
                        {{
                          $t('views.applicationWorkflow.nodes.imageToVideoGenerate.last_frame.label')
                        }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter pre-wrap">

                        <div v-if="typeof item.last_frame_url === 'string'">
                          <el-image
                            :src="item.last_frame_url"
                            alt=""
                            fit="cover" style="width: 40px; height: 40px; display: block"
                            class="border-r-6"
                          />
                        </div>
                        <div v-else-if="Array.isArray(item.last_frame_url)">
                          <el-space wrap>
                            <template v-for="(f, i) in item.last_frame_url" :key="i">
                              <el-image
                                :src="f.url"
                                alt=""
                                fit="cover" style="width: 40px; height: 40px; display: block"
                                class="border-r-6"
                              />
                            </template>
                          </el-space>
                        </div>
                        <div v-else>
                          -
                        </div>
                      </div>
                    </div>

                    <div class="card-never border-r-6 mt-8">
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
                    <div class="card-never border-r-6">
                      <h5 class="p-8-12">
                        {{ $t('common.param.inputParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div v-for="(f, i) in item.result_list" :key="i" class="mb-8">
                          <span class="color-secondary">{{ f.name }}:</span> {{ f.input_value }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-6">
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
                    <div class="card-never border-r-6">
                      <h5 class="p-8-12">
                        {{ $t('views.tool.title') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div class="mb-8">
                          <span class="color-secondary">
                            {{ $t('views.tool.title') }}:
                          </span>
                          {{ item.mcp_tool }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-6">
                      <h5 class="p-8-12">
                        {{ $t('views.applicationWorkflow.nodes.mcpNode.toolParam') }}
                      </h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <div v-for="(value, name) in item.tool_params" :key="name" class="mb-8">
                          <span class="color-secondary">{{ name }}:</span> {{ value }}
                        </div>
                      </div>
                    </div>
                    <div class="card-never border-r-6">
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
                  <div class="card-never border-r-6">
                    <h5 class="p-8-12">{{ $t('chat.executionDetails.errMessage') }}</h5>
                    <div class="p-8-12 border-t-dashed lighter">{{ item.err_message || '-' }}</div>
                  </div>
                </template>
              </div>
            </el-collapse-transition>
          </el-card>
        </template>
      </div>

      <template v-else>
        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.paragraphSource.question') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <span class="mb-8">user: {{ problem }}</span>
          </div>
        </div>
        <div v-if="paddedProblem" class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.paragraphSource.questionPadded') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <span class="mb-8">user: {{ paddedProblem }}</span>
          </div>
        </div>
        <div v-if="system" class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('views.application.form.roleSettings.label') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <span class="mb-8">{{ system }}</span>
          </div>
        </div>

        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.history') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <div v-for="(msg, index) in historyRecord" :key="index">
              <span>{{ msg.role }}: </span>
              <span>{{ msg.content }}</span>
            </div>
          </div>
        </div>

        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.executionDetails.currentChat') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <div class="mb-8">{{ $t('chat.executionDetails.knowedMessage') }}:</div>
            <div v-for="(msg, index) in currentChat" :key="index">
              <span>{{ msg.content }}</span>
            </div>
          </div>
        </div>

        <div class="card-never border-r-6 mb-12">
          <h5 class="p-8-12">
            {{ $t('chat.executionDetails.answer') }}
          </h5>
          <div class="p-8-12 border-t-dashed lighter">
            <div v-for="(msg, index) in AiResponse" :key="index">
              <span>{{ msg.content }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import {ref, computed} from 'vue'
import ParagraphCard
  from '@/components/ai-chat/component/knowledge-source-component/ParagraphCard.vue'
import {arraySort} from '@/utils/array'
import {iconComponent} from '@/workflow/icons/utils'
import {WorkflowType} from '@/enums/application'
import {getImgUrl} from '@/utils/common'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import {isWorkFlow} from '@/utils/application'

const props = defineProps<{
  detail?: any[]
  appType?: string
}>()

const messageList = computed(() => {
  const chat_step = props.detail?.find((item) => item.step_type == 'chat_step')
  if (chat_step) {
    return chat_step.message_list
  }
  return []
})
const get_padding_problem = () => {
  return props.detail?.find((item) => item.step_type == 'problem_padding')
}

const get_padded_problem = () => {
  return props.detail?.find((item) => item.step_type == 'problem_padding')
}

const paddedProblem = computed(() => {
  const problem_padded = get_padded_problem()
  if (problem_padded) {
    return problem_padded.padding_problem_text
  } else {
    return ''
  }
})

const problem = computed(() => {
  const problem_padding = get_padding_problem()
  if (problem_padding) {
    return problem_padding.problem_text
  }
  const user_list = messageList.value.filter((item: any) => item.role == 'user')
  if (user_list.length > 0) {
    return user_list[user_list.length - 1].content
  } else {
    return ''
  }
})

const system = computed(() => {
  const user_list = messageList.value.filter((item: any) => item.role == 'system')
  if (user_list.length > 0) {
    return user_list[user_list.length - 1].content
  } else {
    return ''
  }
})

const historyRecord = computed<any>(() => {
  const messages = messageList.value.filter((item: any) => item.role != 'system')
  if (messages.length > 2) {
    return messages.slice(0, messages.length - 2)
  }
  return []
})

const currentChat = computed(() => {
  const messages = messageList.value.filter((item: any) => item.role != 'system')
  return messages.slice(messages.length - 2, messages.length - 1)
})

const AiResponse = computed(() => {
  const messages = messageList.value?.filter((item: any) => item.role != 'system')
  return messages.slice(messages.length - 1, messages.length)
})
</script>
<style lang="scss" scoped>
.execution-details {
  max-height: calc(100vh - 260px);

  .arrow-icon {
    transition: 0.2s;
  }
}
</style>
