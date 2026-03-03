import { ref, onUnmounted } from 'vue'

export type JobStatus = 'queued' | 'processing' | 'done' | 'error'

export interface JobProgress {
  status: JobStatus
  step: string
  progress: number
  error: string | null
}

export function useJob(jobId: string) {
  const status = ref<JobStatus>('queued')
  const step = ref<string>('')
  const progress = ref<number>(0)
  const error = ref<string | null>(null)

  let es: EventSource | null = new EventSource(`/api/jobs/${jobId}/stream`)

  es.onmessage = (event: MessageEvent) => {
    try {
      const data: JobProgress = JSON.parse(event.data)
      status.value = data.status
      step.value = data.step ?? ''
      progress.value = data.progress ?? 0
      error.value = data.error ?? null

      if (data.status === 'done' || data.status === 'error') {
        es?.close()
        es = null
      }
    } catch {
      // ignore malformed messages
    }
  }

  es.onerror = () => {
    error.value = 'サーバーとの接続が切れました'
    status.value = 'error'
    es?.close()
    es = null
  }

  onUnmounted(() => {
    es?.close()
    es = null
  })

  function downloadSRT(): void {
    triggerDownload(`/api/jobs/${jobId}/download/srt`, `subtitle_${jobId}.srt`)
  }

  function downloadVideo(): void {
    triggerDownload(`/api/jobs/${jobId}/download/video`, `output_${jobId}.mp4`)
  }

  function triggerDownload(url: string, filename: string): void {
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
  }

  return { status, step, progress, error, downloadSRT, downloadVideo }
}
