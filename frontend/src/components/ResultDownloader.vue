<template>
  <div class="result-card">
    <div class="success-icon">
      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    </div>

    <h2 class="result-card__title">処理が完了しました</h2>

    <div class="download-buttons">
      <button class="btn-download" @click="downloadSRT">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        SRTファイルをダウンロード
      </button>

      <button class="btn-download btn-download--primary" @click="downloadVideo">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        字幕付き動画をダウンロード
      </button>
    </div>

    <button class="btn-secondary" @click="emit('restart')">
      別の動画を処理する
    </button>
  </div>
</template>

<script setup lang="ts">
import { useJob } from '../composables/useJob'

const props = defineProps<{ jobId: string }>()
const emit = defineEmits<{ restart: [] }>()

const { downloadSRT, downloadVideo } = useJob(props.jobId)
</script>

<style scoped>
.result-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
  max-width: 520px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 40px 32px;
  text-align: center;
}

.success-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #f0fdf4;
  color: #22c55e;
}

.result-card__title {
  font-size: 1.15rem;
  font-weight: 600;
  color: #1a1a1a;
}

.download-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.btn-download {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.btn-download:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-download--primary {
  background: #6366f1;
  color: #fff;
  border-color: #6366f1;
}

.btn-download--primary:hover {
  background: #4f46e5;
  border-color: #4f46e5;
}

.btn-secondary {
  padding: 8px 16px;
  background: transparent;
  color: #6b7280;
  border: none;
  font-size: 0.875rem;
  cursor: pointer;
  transition: color 0.15s;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.btn-secondary:hover {
  color: #374151;
}
</style>
