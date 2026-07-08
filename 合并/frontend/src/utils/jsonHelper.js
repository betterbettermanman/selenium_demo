/**
 * 严格解析 JSON 文本，用于特定课表等字段。
 * 空内容返回 null；根节点必须是对象或数组。
 */
export function parseJsonStrict(text, fieldName = 'JSON') {
  if (text == null || String(text).trim() === '') {
    return null
  }

  const raw = String(text).trim()
  let parsed

  try {
    parsed = JSON.parse(raw)
  } catch (e) {
    const detail = e.message ? `：${e.message}` : ''
    throw new Error(`${fieldName} 格式不正确${detail}`)
  }

  if (parsed === null || typeof parsed !== 'object') {
    throw new Error(`${fieldName} 必须是 JSON 对象或数组`)
  }

  return parsed
}

/** 格式化为带缩进的 JSON 字符串 */
export function stringifyJsonPretty(value, indent = 2) {
  if (value == null || value === '') {
    return ''
  }
  if (typeof value === 'string') {
    return stringifyJsonPretty(parseJsonStrict(value), indent)
  }
  return JSON.stringify(value, null, indent)
}

/** 校验 JSON 文本，返回校验结果 */
export function validateJsonText(text, fieldName = 'JSON') {
  try {
    const parsed = parseJsonStrict(text, fieldName)
    return {
      valid: true,
      error: '',
      parsed,
      formatted: parsed == null ? '' : stringifyJsonPretty(parsed),
    }
  } catch (e) {
    return {
      valid: false,
      error: e.message,
      parsed: null,
      formatted: '',
    }
  }
}

/** 列表展示用：格式化 JSON，无效时显示提示 */
export function formatJsonDisplay(value) {
  if (value == null || value === '') {
    return '-'
  }
  try {
    const parsed = typeof value === 'string' ? parseJsonStrict(value, 'JSON') : value
    if (parsed == null) return '-'
    return stringifyJsonPretty(parsed)
  } catch {
    return typeof value === 'string' ? value : JSON.stringify(value)
  }
}

/** 列表预览：单行摘要 */
export function formatJsonPreview(value, maxLength = 60) {
  const formatted = formatJsonDisplay(value)
  if (formatted === '-') return formatted
  const singleLine = formatted.replace(/\s+/g, ' ')
  if (singleLine.length <= maxLength) return singleLine
  return `${singleLine.slice(0, maxLength)}...`
}
