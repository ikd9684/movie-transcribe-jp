<template>
  <div class="status-card">
    <h2 class="status-card__title">
      {{ status === 'error' ? 'エラーが発生しました' : '処理中...' }}
    </h2>

    <div class="progress-bar">
      <div
        class="progress-bar__fill"
        :style="{ width: `${progress}%` }"
        :class="{ 'progress-bar__fill--error': status === 'error' }"
      />
    </div>

    <p class="step-text">
      {{ stepLabel }}
      <span v-if="elapsedText" class="elapsed-text">（{{ elapsedText }}）</span>
    </p>

    <ul class="step-list">
      <li
        v-for="(s, i) in STEPS"
        :key="s.label"
        class="step-list__item"
        :class="{
          'step-list__item--done': progress >= s.threshold,
          'step-list__item--active': i === activeIndex,
        }"
      >
        <span class="step-list__icon">
          <svg v-if="progress >= s.threshold" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span v-else-if="i === activeIndex" class="step-list__spinner" />
          <span v-else class="step-list__dot" />
        </span>
        {{ s.label }}
      </li>
    </ul>

    <div v-if="status === 'error'" class="error-section">
      <p class="error-section__msg">{{ error ?? '不明なエラー' }}</p>
      <button class="btn-secondary" @click="emit('retry')">やり直す</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted, onUnmounted } from 'vue'
import { useJob } from '../composables/useJob'

const props = defineProps<{ jobId: string }>()
const emit = defineEmits<{ done: []; retry: [] }>()

const STEPS = [
  { label: '音声抽出', threshold: 20 },
  { label: '文字起こし', threshold: 50 },
  { label: '日本語翻訳', threshold: 75 },
  { label: '字幕ファイル生成', threshold: 85 },
  { label: '字幕焼き込み', threshold: 100 },
]

const { status, step, progress, error } = useJob(props.jobId)

const stepLabel = computed(() => {
  if (status.value === 'done') return '完了'
  if (status.value === 'error') return ''
  return step.value || '待機中...'
})

const activeIndex = computed(() => {
  if (status.value === 'done' || status.value === 'error') return -1
  return STEPS.findIndex(s => progress.value < s.threshold)
})

// Elapsed time counter
const elapsedSeconds = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  timer = setInterval(() => {
    if (status.value !== 'done' && status.value !== 'error') {
      elapsedSeconds.value++
    }
  }, 1000)
})

onUnmounted(() => {
  if (timer !== null) clearInterval(timer)
})

const elapsedText = computed(() => {
  if (status.value === 'done' || status.value === 'error' || elapsedSeconds.value === 0) return ''
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return m > 0 ? `${m}分${s}秒経過` : `${s}秒経過`
})

watch(status, (val) => {
  if (val === 'done') emit('done')
})
</script>

<style scoped>
.status-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 520px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 32px;
}

.status-card__title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #1a1a1a;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar__fill {
  height: 100%;
  background: #6366f1;
  border-radius: 999px;
  transition: width 0.5s ease;
}

.progress-bar__fill--error {
  background: #ef4444;
}

.step-text {
  font-size: 0.875rem;
  color: #6b7280;
  min-height: 1.25rem;
}

.step-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-list__item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.875rem;
  color: #9ca3af;
  transition: color 0.15s;
}

.step-list__item--done {
  color: #1a1a1a;
}

.step-list__item--active {
  color: #6366f1;
  font-weight: 500;
}

.step-list__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: #6366f1;
  flex-shrink: 0;
}

.step-list__dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d1d5db;
}

.step-list__spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.elapsed-text {
  color: #9ca3af;
  font-size: 0.8rem;
}

.error-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 4px;
}

.error-section__msg {
  font-size: 0.875rem;
  color: #ef4444;
}

.btn-secondary {
  align-self: flex-start;
  padding: 8px 16px;
  background: transparent;
  color: #6366f1;
  border: 1px solid #6366f1;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.btn-secondary:hover {
  background: #6366f1;
  color: #fff;
}
</style>
