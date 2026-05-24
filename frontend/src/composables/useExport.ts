/**
 * useExport — exportação de tabelas para PDF (via impressão), HTML e CSV.
 * Não requer bibliotecas externas; usa apenas APIs nativas do browser.
 */

export interface ExportColumn {
  label: string
  field: string | ((row: Record<string, unknown>) => string | number | null | undefined)
  align?: 'left' | 'center' | 'right'
}

export function useExport() {
  function timestamp() {
    return new Date().toLocaleString('pt-PT')
  }

  // ── Build a complete self-contained HTML document ─────────────────────────
  function buildHtmlDocument(title: string, bodyHtml: string, extraStyles = '') {
    return `<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: #222; padding: 24px; }
    h1 { font-size: 20px; font-weight: bold; color: #1565c0; margin-bottom: 4px; }
    .subtitle { font-size: 11px; color: #888; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 4px; }
    thead th {
      background: #1565c0; color: #fff; padding: 8px 10px;
      text-align: left; font-size: 11px; font-weight: 600; white-space: nowrap;
    }
    thead th.center { text-align: center; }
    tbody td { padding: 6px 10px; border-bottom: 1px solid #e8e8e8; vertical-align: middle; }
    tbody td.center { text-align: center; }
    tbody tr:nth-child(even) td { background: #f5f8ff; }
    .footer { margin-top: 14px; font-size: 10px; color: #bbb; text-align: right; }
    @media print {
      body { padding: 8px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      thead th { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
    ${extraStyles}
  </style>
</head>
<body>
  ${bodyHtml}
  <div class="footer">Sinaptik2 &mdash; ${timestamp()}</div>
</body>
</html>`
  }

  // ── Convert rows + columns into an HTML <table> string ────────────────────
  function rowsToTableHtml(rows: Record<string, unknown>[], columns: ExportColumn[]) {
    const thead = columns
      .map((c) => `<th class="${c.align === 'center' ? 'center' : ''}">${c.label}</th>`)
      .join('')
    const tbody = rows
      .map((row) =>
        `<tr>${columns
          .map((c) => {
            const raw = typeof c.field === 'function' ? c.field(row) : row[c.field as string]
            const val = raw === null || raw === undefined ? '' : String(raw)
            return `<td class="${c.align === 'center' ? 'center' : ''}">${val}</td>`
          })
          .join('')}</tr>`
      )
      .join('\n')
    return `<table><thead><tr>${thead}</tr></thead><tbody>\n${tbody}\n</tbody></table>`
  }

  // ── Trigger a browser download ────────────────────────────────────────────
  function downloadBlob(content: string, filename: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /**
   * Open a print-ready window and trigger the browser's Print → Save as PDF.
   */
  function exportToPDF(title: string, rows: Record<string, unknown>[], columns: ExportColumn[]) {
    const table = rowsToTableHtml(rows, columns)
    const body = `<h1>${title}</h1>
<div class="subtitle">${rows.length} registo(s)</div>
${table}`
    const html = buildHtmlDocument(title, body)
    const win = window.open('', '_blank', 'width=960,height=720')
    if (!win) return
    win.document.write(html)
    win.document.close()
    setTimeout(() => { win.focus(); win.print() }, 350)
  }

  /**
   * Download a standalone HTML file with embedded styles.
   */
  function exportToHTML(title: string, rows: Record<string, unknown>[], columns: ExportColumn[], filename: string) {
    const table = rowsToTableHtml(rows, columns)
    const body = `<h1>${title}</h1>
<div class="subtitle">${rows.length} registo(s) &mdash; ${timestamp()}</div>
${table}`
    downloadBlob(buildHtmlDocument(title, body), `${filename}.html`, 'text/html;charset=utf-8')
  }

  /**
   * Download a UTF-8 CSV file (with BOM for Excel compatibility).
   */
  function exportToCSV(rows: Record<string, unknown>[], columns: ExportColumn[], filename: string) {
    const header = columns.map((c) => `"${c.label}"`).join(',')
    const dataRows = rows.map((row) =>
      columns
        .map((c) => {
          const raw = typeof c.field === 'function' ? c.field(row) : row[c.field as string]
          return `"${String(raw ?? '').replace(/"/g, '""')}"`
        })
        .join(',')
    )
    downloadBlob('﻿' + [header, ...dataRows].join('\n'), `${filename}.csv`, 'text/csv;charset=utf-8')
  }

  /**
   * Print arbitrary HTML (e.g. a timetable grid) — wraps it in the standard doc.
   */
  function printHTML(title: string, innerHtml: string, extraStyles = '') {
    const body = `<h1>${title}</h1>\n${innerHtml}`
    const html = buildHtmlDocument(title, body, extraStyles)
    const win = window.open('', '_blank', 'width=1100,height=800')
    if (!win) return
    win.document.write(html)
    win.document.close()
    setTimeout(() => { win.focus(); win.print() }, 350)
  }

  /**
   * Download arbitrary HTML — wraps it in the standard doc.
   */
  function downloadHTML(title: string, innerHtml: string, filename: string, extraStyles = '') {
    const body = `<h1>${title}</h1>\n${innerHtml}`
    downloadBlob(buildHtmlDocument(title, body, extraStyles), `${filename}.html`, 'text/html;charset=utf-8')
  }

  function sortRows(
    rows: Record<string, unknown>[],
    sortBy: { field: string | ((row: Record<string, unknown>) => string) } | null,
    sortDir: 'asc' | 'desc' = 'asc',
  ): Record<string, unknown>[] {
    if (!sortBy) return rows
    return [...rows].sort((a, b) => {
      const av = String(typeof sortBy.field === 'function' ? sortBy.field(a) : (a[sortBy.field as string] ?? ''))
      const bv = String(typeof sortBy.field === 'function' ? sortBy.field(b) : (b[sortBy.field as string] ?? ''))
      const cmp = av.localeCompare(bv, 'pt', { sensitivity: 'base' })
      return sortDir === 'asc' ? cmp : -cmp
    })
  }

  return { exportToPDF, exportToHTML, exportToCSV, printHTML, downloadHTML, rowsToTableHtml, buildHtmlDocument, sortRows }
}
