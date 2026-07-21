<template>
  <div class="question-content">
    <div class="question-bubble" :class="bubbleClass">
      <div v-if="content.documents?.length" class="q-section">
        <div v-for="(f, i) in content.documents" :key="'doc-'+i" class="q-file-card" @click="download(f)">
          <span class="q-file-icon">📄</span>
          <span class="q-file-name" :title="f.name">{{ f.name }}</span>
        </div>
      </div>
      <div v-if="content.images?.length" class="q-section">
        <div class="q-images">
          <template v-for="(img, i) in content.images" :key="'img-'+i">
            <img v-if="img.url" :src="img.url" class="q-img" />
          </template>
        </div>
      </div>
      <div v-if="content.audio?.length" class="q-section">
        <div v-for="(a, i) in content.audio" :key="'aud-'+i" class="q-audio-wrap">
          <audio :src="a.url" controls />
        </div>
      </div>
      <div v-if="content.video?.length" class="q-section">
        <div class="q-videos">
          <div v-for="(v, i) in content.video" :key="'vid-'+i" class="q-video-wrap">
            <video :src="v.url" controls />
          </div>
        </div>
      </div>
      <div v-if="content.files?.length" class="q-section">
        <div v-for="(f, i) in content.files" :key="'file-'+i" class="q-file-card" @click="download(f)">
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

const props = defineProps<{ content: any }>()

const bubbleClass = computed(() => {
  const c = props.content
  const count = [c.documents?.length, c.images?.length, c.audio?.length, c.video?.length, c.files?.length]
    .filter((n: number) => n > 0).length
  return count >= 2 ? 'multi-media' : ''
})

const download = (file: any) => {
  if (file.url) window.open(file.url, '_blank')
}
</script>

<style scoped>
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
