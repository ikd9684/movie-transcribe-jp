<template>
  <div class="app">
    <header class="header">
      <h1 class="title">字幕生成アプリ</h1>
      <button class="gear-btn" title="設定" @click="showSettings = true">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      </button>
    </header>

    <main class="main">
      <VideoUploader
        v-if="pageState === 'upload'"
        @uploaded="onUploaded"
      />
      <ProcessingStatus
        v-else-if="pageState === 'processing'"
        :job-id="jobId!"
        @done="pageState = 'done'"
        @retry="onRetry"
      />
      <ResultDownloader
        v-else
        :job-id="jobId!"
        @restart="onRestart"
      />
    </main>

    <SettingsModal v-if="showSettings" @close="showSettings = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SettingsModal from './components/SettingsModal.vue'
import VideoUploader from './components/VideoUploader.vue'
import ProcessingStatus from './components/ProcessingStatus.vue'
import ResultDownloader from './components/ResultDownloader.vue'

type PageState = 'upload' | 'processing' | 'done'

const showSettings = ref(false)
const pageState = ref<PageState>('upload')
const jobId = ref<string | null>(null)

function onUploaded(id: string): void {
  jobId.value = id
  pageState.value = 'processing'
}

function onRetry(): void {
  pageState.value = 'upload'
}

function onRestart(): void {
  jobId.value = null
  pageState.value = 'upload'
}
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f9fafb;
  color: #1a1a1a;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.title {
  font-size: 1.1rem;
  font-weight: 600;
}

.gear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: background 0.15s, color 0.15s;
}

.gear-btn:hover {
  background: #f3f4f6;
  color: #1a1a1a;
}

.main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

</style>
