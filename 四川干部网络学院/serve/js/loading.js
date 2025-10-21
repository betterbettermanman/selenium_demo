function parseValue(val) {
  if (typeof val === 'boolean') {
    return { show: val, size: 40 }
  }
  if (typeof val === 'object' && val !== null) {
    return {
      show: val.show ?? false,
      size: val.size ?? 40,
    }
  }
  return { show: false, size: 40 }
}

export const LoadingDirective = {
  mounted(el, binding) {
    const mask = document.createElement('div')
    mask.className = 'v-loading-mask'

    const spinner = document.createElement('div')
    spinner.className = 'v-loading-spinner'
    mask.appendChild(spinner)

    const { show, size } = parseValue(binding.value)

    // 设置 spinner 大小
    spinner.style.width = spinner.style.height = size + 'px'
    spinner.style.borderWidth = Math.max(2, size / 10) + 'px'

    const isFullscreen = binding.modifiers.fullscreen
    if (isFullscreen) {
      mask.classList.add('v-loading-fullscreen')
      document.body.appendChild(mask)
    } else {
      el.style.position = 'relative'
      el.appendChild(mask)
    }

    mask.style.display = show ? 'flex' : 'none'
    el._vLoadingMask = mask
    el._vLoadingSpinner = spinner
  },
  updated(el, binding) {
    if (!el._vLoadingMask) return
    const { show, size } = parseValue(binding.value)

    // 更新显示状态
    el._vLoadingMask.style.display = show ? 'flex' : 'none'

    // 更新大小
    if (el._vLoadingSpinner) {
      el._vLoadingSpinner.style.width = el._vLoadingSpinner.style.height = size + 'px'
      el._vLoadingSpinner.style.borderWidth = Math.max(2, size / 10) + 'px'
    }
  },
  unmounted(el, binding) {
    if (!el._vLoadingMask) return
    const isFullscreen = binding.modifiers.fullscreen
    if (isFullscreen) {
      document.body.removeChild(el._vLoadingMask)
    } else {
      el.removeChild(el._vLoadingMask)
    }
    delete el._vLoadingMask
    delete el._vLoadingSpinner
  },
}
