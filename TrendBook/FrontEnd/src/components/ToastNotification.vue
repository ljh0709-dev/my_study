<template>
  <Transition name="toast">
    <div v-if="visible" class="toast" :class="variant" role="status" aria-live="polite">
      {{ message }}
    </div>
  </Transition>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  variant: { type: String, default: 'success' },
  duration: { type: Number, default: 3000 },
})

const visible = ref(false)
let timer = null

const clearTimer = () => {
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
}

watch(
  () => props.message,
  (value) => {
    clearTimer()
    if (!value) {
      visible.value = false
      return
    }
    visible.value = true
    timer = setTimeout(() => {
      visible.value = false
    }, props.duration)
  },
  { immediate: true },
)

onBeforeUnmount(clearTimer)
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  padding: 12px 20px;
  border-radius: var(--radius-full);
  font-size: 0.88rem;
  font-weight: 400;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  pointer-events: none;
}

.toast.success {
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.toast.error {
  background: var(--color-error-container);
  color: var(--color-on-error-container);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(12px);
}
</style>