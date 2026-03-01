import axios from 'axios'
import type { AppSettings } from '../composables/useSettings'

const http = axios.create({ baseURL: '/api' })

export async function uploadVideo(
  file: File,
  settings: AppSettings,
): Promise<{ job_id: string }> {
  const form = new FormData()
  form.append('file', file)
  form.append('settings', JSON.stringify(settings))

  const { data } = await http.post<{ job_id: string }>('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
