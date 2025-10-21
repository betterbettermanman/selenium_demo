;(function(global) {
  const queue = []
  let showing = false

  const typeStyles = {
    info: { background: 'rgba(0, 0, 0, 0.75)', color: '#fff' },
    success: { background: '#ecfdf5', color: '#059669' },
    error: { background: '#fef2f2', color: '#dc2626' },
  }

  const posMap = {
    top: { top: '20px', left: '50%', transform: 'translateX(-50%)' },
    bottom: { bottom: '20px', left: '50%', transform: 'translateX(-50%)' },
    center: { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
    'top-left': { top: '20px', left: '20px' },
    'top-right': { top: '20px', right: '20px' },
    'bottom-left': { bottom: '20px', left: '20px' },
    'bottom-right': { bottom: '20px', right: '20px' },
  }

  function showNext() {
    if (queue.length === 0) {
      showing = false
      return
    }
    showing = true
    const { message, duration, position, type } = queue.shift()

    const toast = document.createElement('div')
    toast.className = 'toast'
    toast.textContent = message

    // 基础样式
    Object.assign(toast.style, {
      position: 'fixed',
      padding: '10px 20px',
      borderRadius: '6px',
      fontSize: '14px',
      zIndex: 9999,
      opacity: '0',
      transition: 'opacity 0.3s, transform 0.3s',
      maxWidth: '80%',
      wordBreak: 'break-word',
      textAlign: 'center',
      ...typeStyles[type] || typeStyles.info,
      ...posMap[position] || posMap.top,
    })

    document.body.appendChild(toast)

    // 动画显示
    setTimeout(() => {
      toast.style.opacity = '1'
    }, 50)

    // 自动隐藏 & 移除
    setTimeout(() => {
      toast.style.opacity = '0'
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast)
        showNext() // 显示队列中下一条
      }, 300)
    }, duration)
  }

  function $toast(message, duration = 3000, position = 'top', type = 'info') {
    queue.push({ message, duration, position, type })
    if (!showing) showNext()
  }

  // 挂载全局
  global.$toast = $toast
})(window)
