<template>
  <div class="uploader">
    <div
      class="drop-zone"
      :class="{ 'drop-zone--active': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <svg class="drop-zone__icon" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="16 16 12 12 8 16" />
        <line x1="12" y1="12" x2="12" y2="21" />
        <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
      </svg>
      <p class="drop-zone__text">ここに動画をドロップ</p>
      <p class="drop-zone__subtext">または クリックして選択</p>
      <input
        ref="fileInput"
        type="file"
        accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm,video/x-m4v,.mp4,.mov,.avi,.mkv,.webm,.m4v"
        class="drop-zone__input"
        @change="onFileChange"
      />
    </div>

    <div v-if="selectedFile" class="file-info">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
        <polyline points="13 2 13 9 20 9" />
      </svg>
      <span class="file-info__name">{{ selectedFile.name }}</span>
      <span class="file-info__size">{{ formatSize(selectedFile.size) }}</span>
    </div>

    <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

    <button
      class="btn-primary"
      :disabled="!selectedFile || uploading"
      @click="startUpload"
    >
      <span v-if="uploading" class="spinner" />
      {{ uploading ? 'アップロード中...' : 'アップロード開始' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSettings } from '../composables/useSettings'
import { uploadVideo } from '../api/client'

const emit = defineEmits<{ uploaded: [jobId: string] }>()

const { settings } = useSettings()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const errorMsg = ref<string | null>(null)

const ALLOWED_EXTENSIONS = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'm4v']

function validate(file: File): string | null {
  const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return `対応していない形式です（${ALLOWED_EXTENSIONS.join(', ')}）`
  }
  return null
}

function pickFile(file: File): void {
  const err = validate(file)
  if (err) {
    errorMsg.value = err
    selectedFile.value = null
    return
  }
  errorMsg.value = null
  selectedFile.value = file
}

function onDrop(event: DragEvent): void {
  isDragging.value = false
  const file = event.dataTransfer?.files[0]
  if (file) pickFile(file)
}

function onFileChange(event: Event): void {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) pickFile(file)
}

async function startUpload(): Promise<void> {
  if (!selectedFile.value || uploading.value) return
  uploading.value = true
  errorMsg.value = null
  try {
    const { job_id } = await uploadVideo(selectedFile.value, settings)
    emit('uploaded', job_id)
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    errorMsg.value = `アップロードに失敗しました: ${msg}`
  } finally {
    uploading.value = false
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<style scoped>
.uploader {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  max-width: 520px;
}

.drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 48px 24px;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.drop-zone:hover,
.drop-zone--active {
  border-color: #6366f1;
  background: #f5f3ff;
}

.drop-zone__icon {
  color: #9ca3af;
}

.drop-zone--active .drop-zone__icon {
  color: #6366f1;
}

.drop-zone__text {
  font-size: 0.95rem;
  font-weight: 500;
  color: #374151;
}

.drop-zone__subtext {
  font-size: 0.8rem;
  color: #9ca3af;
}

.drop-zone__input {
  display: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f3f4f6;
  border-radius: 6px;
  color: #374151;
  font-size: 0.875rem;
}

.file-info__name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-info__size {
  color: #6b7280;
  white-space: nowrap;
}

.error-msg {
  font-size: 0.875rem;
  color: #ef4444;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) {
  background: #4f46e5;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
