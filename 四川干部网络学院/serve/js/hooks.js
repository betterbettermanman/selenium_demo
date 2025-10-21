const { ref } = window.Vue

export function useBoolean(flag = false) {
  const boolean = ref(flag)
  const toggleBoolean = (toggleFlag = undefined) => {
    if (toggleFlag !== undefined) {
      boolean.value = toggleFlag
      return
    }
    boolean.value = !boolean.value
  }
  return [boolean, toggleBoolean]
}

export function debounce(fn, delay = 300, immediate = false) {
  let timer = null
  let invoked = false

  function debounced(...args) {
    const context = this

    if (immediate && !invoked) {
      fn.apply(context, args)
      invoked = true
    }

    clearTimeout(timer)
    timer = setTimeout(() => {
      if (!immediate) {
        fn.apply(context, args)
      }
      invoked = false
    }, delay)
  }

  // 允许手动取消
  debounced.cancel = function() {
    clearTimeout(timer)
    timer = null
    invoked = false
  }

  return debounced
}
