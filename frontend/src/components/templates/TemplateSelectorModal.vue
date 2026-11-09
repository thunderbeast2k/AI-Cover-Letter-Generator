<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";
import Modal from "@/components/common/Modal.vue";
import Badge from "@/components/common/Badge.vue";
import { TEMPLATES } from "@/utils/templates";

interface Props {
  isOpen: boolean;
  activeTemplateId: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "select", templateId: string): void;
}>();

const selected = ref(props.activeTemplateId || "classic");

const handleSelect = (id: string) => {
  selected.value = id;
  emit("select", id);
};
</script>

<template>
  <Modal
    :is-open="props.isOpen"
    title="Choose Cover Letter Template"
    subtitle="Templates format the document layout, headers, and export styles without changing your letter content."
    max-width="max-w-2xl"
    @close="emit('close')"
  >
    <div class="grid grid-cols-1 gap-3 py-2">
      <div
        v-for="tmpl in TEMPLATES"
        :key="tmpl.id"
        :class="[
          'relative flex items-start gap-4 rounded-xl border p-4 cursor-pointer transition-all',
          selected === tmpl.id
            ? 'border-primary bg-primary/5 ring-1 ring-primary'
            : 'border-border bg-card hover:border-primary/40 hover:bg-muted/30'
        ]"
        @click="handleSelect(tmpl.id)"
      >
        <!-- Template Icon / Preview Glyph -->
        <div
          :class="[
            'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl font-bold transition-colors',
            selected === tmpl.id
              ? 'bg-primary text-white'
              : 'bg-secondary text-foreground'
          ]"
        >
          <Icon
            :icon="
              tmpl.id === 'technical'
                ? 'lucide:code-2'
                : tmpl.id === 'minimal'
                ? 'lucide:layout-template'
                : tmpl.id === 'graduate'
                ? 'lucide:graduation-cap'
                : tmpl.id === 'internship'
                ? 'lucide:briefcase'
                : 'lucide:file-text'
            "
            class="h-6 w-6"
          />
        </div>

        <!-- Info -->
        <div class="flex-1 space-y-1">
          <div class="flex items-center justify-between">
            <h5 class="text-sm font-semibold text-foreground flex items-center gap-2">
              {{ tmpl.name }}
              <Badge variant="outline" class="text-[10px]">{{ tmpl.badge }}</Badge>
            </h5>
            <span v-if="selected === tmpl.id" class="text-primary flex items-center gap-1 text-xs font-semibold">
              <Icon icon="lucide:check-circle-2" class="h-4 w-4" />
              Active
            </span>
          </div>

          <p class="text-xs text-muted-foreground leading-relaxed">
            {{ tmpl.description }}
          </p>

          <div class="text-[11px] text-muted-foreground/80 pt-1 flex items-center gap-1.5">
            <Icon icon="lucide:target" class="h-3.5 w-3.5 text-primary" />
            <span class="font-medium">Best for:</span> {{ tmpl.suitableFor }}
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        class="px-4 py-2 text-xs font-medium rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors shadow-sm"
        @click="emit('close')"
      >
        Done
      </button>
    </template>
  </Modal>
</template>
