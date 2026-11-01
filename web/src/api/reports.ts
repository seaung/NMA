export type ReportType = 'compliance' | 'vulnerabilities'

/** 导出报表为 Excel（直接使用 fetch 下载二进制，绕过 JSON 信封拦截器） */
export async function exportReport(type: ReportType = 'compliance'): Promise<void> {
  const raw = localStorage.getItem('nma_auth')
  const token = raw ? (JSON.parse(raw).access as string) : ''
  const url =
    type === 'vulnerabilities' ? '/api/v1/reports/?type=vulnerabilities' : '/api/v1/reports/'
  const resp = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
  if (!resp.ok) throw new Error('报表导出失败')
  const blob = await resp.blob()
  const filename = type === 'vulnerabilities' ? 'vulnerabilities.xlsx' : 'compliance_report.xlsx'
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(a.href)
}
