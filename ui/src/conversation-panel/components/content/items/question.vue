<template>
  <div class="question-content">
    <div class="question-bubble" :class="bubbleClass">
      <div v-if="content.document_list?.length" class="q-section">
        <div v-for="(f, i) in content.document_list" :key="'doc-'+i" class="q-file-card" @click="download(f)">
          <span class="q-file-icon">📄</span>
          <span class="q-file-name" :title="f.name">{{ f.name }}</span>
        </div>
      </div>
      <div v-if="content.image_list?.length" class="q-section">
        <div class="q-images">
          <template v-for="(img, i) in content.image_list" :key="'img-'+i">
            <img v-if="img.url" :src="resetUrl(img.url)" class="q-img" />
          </template>
        </div>
      </div>
      <div v-if="content.audio_list?.length" class="q-section">
        <div v-for="(a, i) in content.audio_list" :key="'aud-'+i" class="q-audio-wrap">
          <audio :src="resetUrl(a.url)" controls />
        </div>
      </div>
      <div v-if="content.video_list?.length" class="q-section">
        <div class="q-videos">
          <div v-for="(v, i) in content.video_list" :key="'vid-'+i" class="q-video-wrap">
            <video :src="resetUrl(v.url)" controls />
          </div>
        </div>
      </div>
      <div v-if="content.other_list?.length" class="q-section">
        <div v-for="(f, i) in content.other_list" :key="'file-'+i" class="q-file-card" @click="download(f)">
          <span class="q-file-icon">📎</span>
          <span class="q-file-name" :title="f.name">{{ f.name }}</span>
        </div>
      </div>
      <span v-if="content.content">{{ content.content }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { resetUrl } from '@/utils/icon'

const props = defineProps<{ content: any }>()

const bubbleClass = computed(() => {
  const c = props.content
  const count = [c.document_list?.length, c.image_list?.length, c.audio_list?.length, c.video_list?.length, c.other_list?.length]
    .filter((n: number) => n > 0).length
  return count >= 2 ? 'multi-media' : ''
})

const download = (file: any) => {
  if (file.url) window.open(resetUrl(file.url), '_blank')
}
</script>

<style scoped lang="scss">
.question-content {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.question-bubble {
  background: #d6e2ff;
  padding: 12px 16px;
  border-radius: 12px;
  border-bottom-right-radius: 4px;
  max-width: 70%;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.q-section {
  margin-bottom: 8px;
}

.q-images {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.q-img {
  width: 170px;
  height: 170px;
  border-radius: 6px;
  object-fit: cover;
  cursor: pointer;
  display: block;
}

.q-audio-wrap audio {
  width: 350px;
  height: 43px;
  border-radius: 6px;
}

.q-videos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.q-video-wrap video {
  width: 170px;
  border-radius: 6px;
  display: block;
}

.q-file-card {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  max-width: 100%;
  transition: background 0.15s;
}

.q-file-card:hover {
  background: rgba(255, 255, 255, 0.9);
}

.q-file-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.q-file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

@media only screen and (max-width: 768px) {
  .question-bubble { max-width: 85%; }
  .q-img { width: 120px; height: 120px; }
  .q-audio-wrap audio { width: 100%; }
}
</style>
