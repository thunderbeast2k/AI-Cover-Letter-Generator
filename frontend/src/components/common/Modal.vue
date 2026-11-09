<script setup lang="ts">
import { Icon } from "@iconify/vue";

interface Props {
  isOpen: boolean;
  title: string;
  subtitle?: string;
  maxWidth?: string;
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: "",
  maxWidth: "max-w-xl"
});

const emit = defineEmits<{
  (e: "close"): void;
}>();
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="props.isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="emit('close')"
      >
        <div
          :class="[
            'relative w-full rounded-2xl border border-border bg-card p-6 shadow-2xl transition-all',
            props.maxWidth
          ]"
        >
          <!-- Modal Header -->
          <div class="flex items-start justify-between mb-4 border-b border-border/60 pb-3">
            <div>
              <h3 class="text-lg font-semibold text-foreground">
                {{ props.title }}
              </h3>
              <p v-if="props.subtitle" class="text-xs text-muted-foreground mt-0.5">
                {{ props.subtitle }}
              </p>
            </div>
            <button
              class="rounded-lg p-1.5 text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
              @click="emit('close')"
            >
              <Icon icon="lucide:x" class="h-5 w-5" />
            </button>
          </div>

          <!-- Modal Body -->
          <div class="max-h-[75vh] overflow-y-auto pr-1">
            <slot />
          </div>

          <!-- Modal Footer -->
          <div v-if="$slots.footer" class="mt-5 border-t border-border/60 pt-3 flex justify-end gap-2">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
