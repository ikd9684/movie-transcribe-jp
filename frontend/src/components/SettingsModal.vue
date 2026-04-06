<template>
  <div class="modal-overlay" @click.self="$emit('close')" @keydown.esc="$emit('close')">
    <div class="modal" role="dialog" aria-modal="true" aria-label="設定">
      <h2>設定</h2>

      <section>
        <h3>文字起こし</h3>
        <div class="field">
          <label for="whisperModel">Whisper モデル</label>
          <select id="whisperModel" v-model="local.whisperModel">
            <option value="tiny">tiny</option>
            <option value="base">base</option>
            <option value="small">small</option>
            <option value="medium">medium</option>
            <option value="large-v3">large-v3</option>
          </select>
        </div>
        <div class="field">
          <label for="whisperLanguage">音声言語</label>
          <select id="whisperLanguage" v-model="local.whisperLanguage">
            <option value="auto">自動検出</option>
            <option value="en">English</option>
            <option value="zh">中文</option>
            <option value="ko">한국어</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="pt">Portuguese</option>
          </select>
        </div>
      </section>

      <section>
        <h3>翻訳</h3>
        <div class="field">
          <label for="ollamaBaseUrl">Ollama URL</label>
          <input id="ollamaBaseUrl" v-model="local.ollamaBaseUrl" type="text" />
        </div>
        <div class="field">
          <label for="translationModel">LLM モデル</label>
          <select id="translationModel" v-model="local.translationModel" :disabled="modelLoading">
            <option v-if="modelLoading" value="">読み込み中...</option>
            <option v-for="m in modelOptions" :key="m" :value="m">{{ m }}</option>
          </select>
          <span v-if="modelError" class="model-error">{{ modelError }}</span>
        </div>
        <div class="field">
          <label for="translationParallel">翻訳並列数</label>
          <input
            id="translationParallel"
            v-model.number="local.translationParallel"
            type="number"
            min="1"
            max="8"
          />
        </div>
        <div class="field">
          <label for="translationContextWindow">コンテキスト窓</label>
          <input
            id="translationContextWindow"
            v-model.number="local.translationContextWindow"
            type="number"
            min="0"
            max="4"
          />
        </div>
      </section>

      <section>
        <h3>字幕</h3>
        <div class="field">
          <label for="subtitleFontSize">フォントサイズ</label>
          <input
            id="subtitleFontSize"
            v-model.number="local.subtitleFontSize"
            type="number"
            min="12"
            max="48"
          />
        </div>
        <div class="field">
          <label for="subtitlePosition">字幕位置</label>
          <select id="subtitlePosition" v-model="local.subtitlePosition">
            <option value="bottom">下部中央</option>
            <option value="top">上部中央</option>
          </select>
        </div>
      </section>

      <section>
        <h3>出力</h3>
        <div class="field">
          <label for="outputCrf">
            動画品質 (CRF)
            <span class="hint">数値が小さいほど高画質・大容量</span>
          </label>
          <input
            id="outputCrf"
            v-model.number="local.outputCrf"
            type="number"
            min="18"
            max="28"
          />
        </div>
      </section>

      <section class="danger-section">
        <h3>ストレージ</h3>
        <p class="danger-description">アップロードされた動画・生成された字幕・出力動画をすべて削除します。</p>
        <button class="btn-danger" :disabled="clearing" @click="onClearStorage">
          {{ clearing ? '削除中...' : 'ストレージをクリア' }}
        </button>
        <p v-if="clearResult" class="clear-result">{{ clearResult }}</p>
      </section>

      <div class="actions">
        <button class="btn-secondary" @click="onReset">リセット</button>
        <button class="btn-primary" @click="onSave">保存して閉じる</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onMounted, onUnmounted } from 'vue'
import { useSettings, type AppSettings } from '../composables/useSettings'
import { clearStorage } from '../api/client'

const emit = defineEmits<{ close: []; storageCleared: [] }>()

const { settings, save, reset } = useSettings()

const local = reactive<AppSettings>({ ...settings })
const clearing = ref(false)
const clearResult = ref('')

const modelOptions = ref<string[]>([])
const modelLoading = ref(false)
const modelError = ref('')

async function fetchModels() {
  modelLoading.value = true
  modelError.value = ''
  try {
    const res = await fetch(`/api/ollama/models?base_url=${encodeURIComponent(local.ollamaBaseUrl)}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    const names: string[] = (data.models ?? []).map((m: { name: string }) => m.name)
    // 現在の選択値がリストにない場合は先頭に追加
    if (local.translationModel && !names.includes(local.translationModel)) {
      names.unshift(local.translationModel)
    }
    modelOptions.value = names
  } catch (e) {
    modelError.value = 'Ollama に接続できませんでした。URL を確認してください。'
    // 現在値だけをフォールバックとして残す
    if (local.translationModel) modelOptions.value = [local.translationModel]
  } finally {
    modelLoading.value = false
  }
}

watch(() => local.ollamaBaseUrl, fetchModels)

function onSave() {
  Object.assign(settings, local)
  save()
  emit('close')
}

function onReset() {
  reset()
  Object.assign(local, settings)
}

async function onClearStorage() {
  if (!confirm('ストレージをすべて削除しますか？\nアップロード済みファイルと生成済みファイルが削除されます。')) return
  clearing.value = true
  clearResult.value = ''
  try {
    const { deleted_mb } = await clearStorage()
    clearResult.value = `${deleted_mb} MB を削除しました。`
    emit('storageCleared')
  } finally {
    clearing.value = false
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  fetchModels()
})
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  width: 480px;
  max-width: calc(100vw - 32px);
  max-height: calc(100vh - 64px);
  overflow-y: auto;
  color: #1a1a1a;
}

h2 {
  margin: 0 0 16px;
  font-size: 1.25rem;
}

section {
  margin-bottom: 20px;
}

h3 {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #666;
  letter-spacing: 0.05em;
  margin: 0 0 10px;
  padding-bottom: 4px;
  border-bottom: 1px solid #e5e7eb;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
}

.hint {
  font-size: 0.75rem;
  font-weight: 400;
  color: #9ca3af;
  margin-left: 6px;
}

input,
select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.15s;
}

input:focus,
select:focus {
  border-color: #6366f1;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.btn-primary {
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-primary:hover {
  background: #4f46e5;
}

.btn-secondary {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f3f4f6;
}

.danger-section {
  border-top: 1px solid #fee2e2;
  padding-top: 16px;
  margin-bottom: 20px;
}

.danger-section h3 {
  color: #ef4444;
  border-bottom-color: #fee2e2;
}

.danger-description {
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 12px;
}

.btn-danger {
  background: transparent;
  color: #ef4444;
  border: 1px solid #ef4444;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.btn-danger:hover:not(:disabled) {
  background: #ef4444;
  color: #fff;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-result {
  margin-top: 8px;
  font-size: 0.85rem;
  color: #6b7280;
}

.model-error {
  font-size: 0.8rem;
  color: #ef4444;
}
</style>
