import { ref } from "vue";

export interface Toast {
  id: string;
  type: "success" | "error" | "info" | "warning";
  title?: string;
  message: string;
  duration?: number;
}

const toasts = ref<Toast[]>([]);

export function useToast() {
  function addToast(toast: Omit<Toast, "id">) {
    const id = Math.random().toString(36).substring(2, 9);
    const duration = toast.duration ?? 4000;
    const newToast: Toast = {
      ...toast,
      id,
      duration
    };

    toasts.value.push(newToast);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  function success(message: string, title: string = "Success") {
    addToast({ type: "success", title, message });
  }

  function error(message: string, title: string = "Error") {
    addToast({ type: "error", title, message, duration: 6000 });
  }

  function info(message: string, title: string = "Notice") {
    addToast({ type: "info", title, message });
  }

  function warning(message: string, title: string = "Warning") {
    addToast({ type: "warning", title, message, duration: 5000 });
  }

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    info,
    warning
  };
}
