import { reactive } from 'vue'

export interface AppSettings {
  whisperModel: string
  whisperLanguage: string
  ollamaBaseUrl: string
  translationModel: string
  translationParallel: number
  translationContextWindow: number
  subtitleFontSize: number
  subtitlePosition: string
  outputCrf: number
}

export const DEFAULT_SETTINGS: AppSettings = {
  whisperModel: 'large-v3',
  whisperLanguage: 'auto',
  ollamaBaseUrl: 'http://localhost:11434',
  translationModel: 'gpt-oss:20b',
  translationParallel: 4,
  translationContextWindow: 2,
  subtitleFontSize: 24,
  subtitlePosition: 'bottom',
  outputCrf: 23,
}

const STORAGE_KEY = 'movie-transcribe-settings'

function loadFromStorage(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULT_SETTINGS }
    return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULT_SETTINGS }
  }
}

const settings = reactive<AppSettings>(loadFromStorage())

function save(): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
}

function reset(): void {
  Object.assign(settings, DEFAULT_SETTINGS)
}

export function useSettings() {
  return { settings, save, reset }
}
