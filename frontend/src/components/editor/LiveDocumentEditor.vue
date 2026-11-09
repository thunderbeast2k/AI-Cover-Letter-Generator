<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { Icon } from "@iconify/vue";
import { useToast } from "@/composables/useToast";
import { ApiService } from "@/services/api";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Badge from "@/components/common/Badge.vue";
import ShimmerButton from "@/components/inspira/ShimmerButton.vue";
import BorderBeam from "@/components/inspira/BorderBeam.vue";
import type { PersonalInfo, JobInfo, QualityReport, SpecificSuggestion } from "@/types";

interface Props {
  coverLetter: string;
  personalInfo: PersonalInfo;
  jobInfo: JobInfo;
  templateId: string;
  isGenerating?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isGenerating: false
});

const emit = defineEmits<{
  (e: "update:coverLetter", val: string): void;
  (e: "open-templates"): void;
  (e: "open-quality", report: QualityReport | null): void;
  (e: "save-draft"): void;
  (e: "regenerate"): void;
}>();

const { success, error, info } = useToast();

const localContent = ref(props.coverLetter);
const history = ref<string[]>([]);
const isImproving = ref(false);
const activeImproveAction = ref<string | null>(null);
const isExportingPdf = ref(false);
const isExportingDocx = ref(false);
const selectedSnippet = ref("");
const customRewritePrompt = ref("");
const showSelectionModal = ref(false);

watch(
  () => props.coverLetter,
  (newVal) => {
    if (newVal !== localContent.value) {
      if (localContent.value.trim()) {
        history.value.push(localContent.value);
      }
      localContent.value = newVal;
    }
  }
);

const onInput = (e: Event) => {
  const target = e.target as HTMLTextAreaElement;
  localContent.value = target.value;
  emit("update:coverLetter", target.value);
};

const wordCount = computed(() => {
  if (!localContent.value.trim()) return 0;
  return localContent.value.trim().split(/\s+/).length;
});

const charCount = computed(() => {
  return localContent.value.length;
});

const canUndo = computed(() => {
  return history.value.length > 0;
});

const handleUndo = () => {
  if (history.value.length > 0) {
    const prev = history.value.pop()!;
    localContent.value = prev;
    emit("update:coverLetter", prev);
    info("Reverted to previous version.");
  }
};

const copyToClipboard = async () => {
  if (!localContent.value.trim()) return;
  try {
    await navigator.clipboard.writeText(localContent.value);
    success("Cover letter copied to clipboard!");
  } catch (err) {
    error("Failed to copy to clipboard.");
  }
};

// Check for selected text inside textarea
const handleTextareaSelect = (e: Event) => {
  const target = e.target as HTMLTextAreaElement;
  const start = target.selectionStart;
  const end = target.selectionEnd;
  if (start !== end) {
    selectedSnippet.value = target.value.substring(start, end);
  } else {
    selectedSnippet.value = "";
  }
};

// Trigger AI improvements
const executeImprovement = async (action: string, customInstruction?: string) => {
  if (!localContent.value.trim()) {
    error("Please generate or enter a cover letter first.");
    return;
  }

  isImproving.value = true;
  activeImproveAction.value = action;

  try {
    const result = await ApiService.improveCoverLetter({
      cover_letter: localContent.value,
      action: action,
      selected_text: action === "rewrite_selection" ? selectedSnippet.value : undefined,
      job_title: props.jobInfo.job_title,
      company_name: props.jobInfo.company_name,
      custom_instruction: customInstruction
    });

    history.value.push(localContent.value);

    if (result.is_selection_replacement && selectedSnippet.value) {
      // Replace only the selected text
      const updated = localContent.value.replace(selectedSnippet.value, result.improved_text);
      localContent.value = updated;
      emit("update:coverLetter", updated);
      success("Rewrote selected text successfully!");
      selectedSnippet.value = "";
      showSelectionModal.value = false;
    } else {
      localContent.value = result.improved_text;
      emit("update:coverLetter", result.improved_text);
      success("Cover letter improved successfully!");
    }
  } catch (err: any) {
    error(err.message || "Failed to improve text.");
  } finally {
    isImproving.value = false;
    activeImproveAction.value = null;
  }
};

// Launch Quality Check
const runQualityCheck = async () => {
  if (!localContent.value.trim()) {
    error("Please generate or enter a cover letter first.");
    return;
  }
  emit("open-quality", null); // open modal with loading
  try {
    const report = await ApiService.checkQuality({
      cover_letter: localContent.value,
      job_description: props.jobInfo.job_description,
      job_title: props.jobInfo.job_title
    });
    emit("open-quality", report);
  } catch (err: any) {
    error(err.message || "Failed to check letter quality.");
  }
};

// Export Handlers
const handleDownloadPdf = async () => {
  if (!localContent.value.trim()) {
    error("Cannot export empty letter.");
    return;
  }
  isExportingPdf.value = true;
  try {
    await ApiService.downloadPdf({
      cover_letter: localContent.value,
      personal_info: props.personalInfo,
      job_info: props.jobInfo,
      template_id: props.templateId
    });
    success("PDF generated and downloaded!");
  } catch (err: any) {
    error(err.message || "Failed to download PDF.");
  } finally {
    isExportingPdf.value = false;
  }
};

const handleDownloadDocx = async () => {
  if (!localContent.value.trim()) {
    error("Cannot export empty letter.");
    return;
  }
  isExportingDocx.value = true;
  try {
    await ApiService.downloadDocx({
      cover_letter: localContent.value,
      personal_info: props.personalInfo,
      job_info: props.jobInfo,
      template_id: props.templateId
    });
    success("DOCX generated and downloaded!");
  } catch (err: any) {
    error(err.message || "Failed to download DOCX.");
  } finally {
    isExportingDocx.value = false;
  }
};

// Open Rewrite Selection Modal
const promptSelectionRewrite = () => {
  if (!selectedSnippet.value.trim()) {
    info("Please highlight a sentence or paragraph in the letter editor first.");
    return;
  }
  showSelectionModal.value = true;
};
</script>

<template>
  <div class="flex flex-col h-full space-y-4">
    <!-- Top Action Bar -->
    <div
      class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-card p-3 shadow-sm"
    >
      <!-- Left side: Stats & Status -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground font-medium">
          <Icon icon="lucide:file-text" class="h-4 w-4 text-primary" />
          <span>{{ wordCount }} words</span>
          <span>&bull;</span>
          <span>{{ charCount }} chars</span>
        </div>

        <Badge variant="outline" class="capitalize hidden sm:inline-flex">
          {{ props.templateId }} Template
        </Badge>
      </div>

      <!-- Right side: Quick utility buttons -->
      <div class="flex items-center gap-1.5">
        <!-- Undo Button -->
        <button
          :disabled="!canUndo || isImproving"
          class="flex items-center gap-1 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground disabled:opacity-40 transition-colors"
          title="Undo latest AI modification"
          @click="handleUndo"
        >
          <Icon icon="lucide:undo-2" class="h-3.5 w-3.5" />
          <span class="hidden sm:inline">Undo</span>
        </button>

        <!-- Copy Button -->
        <button
          class="flex items-center gap-1 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          title="Copy cover letter text"
          @click="copyToClipboard"
        >
          <Icon icon="lucide:copy" class="h-3.5 w-3.5" />
          <span class="hidden sm:inline">Copy</span>
        </button>

        <!-- Quality Checker Button -->
        <button
          class="flex items-center gap-1 rounded-lg border border-primary/30 bg-primary/5 px-2.5 py-1.5 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
          title="Analyze letter quality"
          @click="runQualityCheck"
        >
          <Icon icon="lucide:gauge" class="h-3.5 w-3.5" />
          <span>Quality Check</span>
        </button>

        <!-- Template Selector Button -->
        <button
          class="flex items-center gap-1 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          title="Switch document layout template"
          @click="emit('open-templates')"
        >
          <Icon icon="lucide:layout-template" class="h-3.5 w-3.5" />
          <span class="hidden sm:inline">Template</span>
        </button>

        <!-- Save Draft Button -->
        <button
          class="flex items-center gap-1 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
          title="Save to local drafts"
          @click="emit('save-draft')"
        >
          <Icon icon="lucide:bookmark" class="h-3.5 w-3.5" />
          <span class="hidden sm:inline">Save Draft</span>
        </button>
      </div>
    </div>

    <!-- AI Polish & Improvement Toolbar -->
    <div
      class="flex flex-wrap items-center gap-1.5 rounded-xl border border-border/80 bg-muted/40 p-2.5 text-xs"
    >
      <span class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1 mr-1">
        <Icon icon="lucide:wand-2" class="h-3.5 w-3.5 text-primary" />
        AI Refine:
      </span>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('improve_writing')"
      >
        Improve Writing
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('make_professional')"
      >
        More Professional
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('make_concise')"
      >
        Make Concise
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('make_confident')"
      >
        More Confident
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('improve_technical')"
      >
        Tech Relevance
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('improve_opening')"
      >
        Refine Opening
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('improve_closing')"
      >
        Refine Closing
      </button>

      <button
        :disabled="isImproving || !localContent.trim()"
        class="rounded-md border border-border bg-card px-2.5 py-1 font-medium hover:border-primary/50 hover:bg-secondary disabled:opacity-40 transition-colors"
        @click="executeImprovement('fix_grammar')"
      >
        Fix Grammar
      </button>

      <!-- Rewrite Selection Trigger -->
      <button
        :disabled="isImproving || !localContent.trim()"
        :class="[
          'rounded-md border px-2.5 py-1 font-medium flex items-center gap-1 transition-colors',
          selectedSnippet
            ? 'border-primary bg-primary/10 text-primary font-semibold'
            : 'border-border bg-card hover:bg-secondary opacity-80'
        ]"
        title="Highlight text in editor to rewrite with custom AI instructions"
        @click="promptSelectionRewrite"
      >
        <Icon icon="lucide:highlighter" class="h-3 w-3" />
        Rewrite Selection
      </button>
    </div>

    <!-- Live Document Paper Canvas -->
    <div class="relative flex-1 rounded-2xl border border-border bg-card shadow-lg p-6 sm:p-10 flex flex-col min-h-[500px] overflow-hidden">
      <!-- Inspira UI BorderBeam running while AI writes or refines -->
      <BorderBeam
        v-if="props.isGenerating || isImproving"
        :size="280"
        :duration="8"
        color-from="#3b82f6"
        color-to="#8b5cf6"
      />

      <!-- Generating / Improving Overlay -->
      <div
        v-if="props.isGenerating || isImproving"
        class="absolute inset-0 z-20 flex flex-col items-center justify-center rounded-2xl bg-card/80 backdrop-blur-sm p-6"
      >
        <LoadingSpinner size="lg" />
        <h4 class="mt-4 text-base font-semibold text-foreground">
          {{ props.isGenerating ? 'Crafting your personalized cover letter...' : 'Refining with AI...' }}
        </h4>
        <p class="text-xs text-muted-foreground mt-1 max-w-sm text-center">
          Synthesizing your qualifications with job specifications using strict factual integrity.
        </p>
      </div>

      <!-- Document Header Preview -->
      <div
        :class="[
          'border-b pb-4 mb-4 transition-all',
          props.templateId === 'minimal' ? 'text-center' : 'text-left',
          props.templateId === 'technical' ? 'border-primary' : 'border-border'
        ]"
      >
        <h2 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
          {{ props.personalInfo.full_name || 'Your Full Name' }}
        </h2>
        <div class="text-xs text-muted-foreground mt-1 flex flex-wrap gap-x-2 gap-y-1 justify-start">
          <span v-if="props.personalInfo.email">{{ props.personalInfo.email }}</span>
          <span v-if="props.personalInfo.phone">&bull; {{ props.personalInfo.phone }}</span>
          <span v-if="props.personalInfo.location">&bull; {{ props.personalInfo.location }}</span>
          <span v-if="props.personalInfo.linkedin_url">&bull; {{ props.personalInfo.linkedin_url }}</span>
        </div>
      </div>

      <!-- Editable Document Textarea -->
      <textarea
        :value="localContent"
        placeholder="Your generated cover letter will appear here. You can edit text directly at any time..."
        class="w-full flex-1 resize-none bg-transparent font-sans text-sm sm:text-base leading-relaxed text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-0 selection:bg-primary/20"
        @input="onInput"
        @select="handleTextareaSelect"
      />
    </div>

    <!-- Export Action Bar -->
    <div class="flex flex-wrap items-center justify-between gap-3 pt-2">
      <div class="text-xs text-muted-foreground flex items-center gap-1.5">
        <Icon icon="lucide:info" class="h-3.5 w-3.5 text-primary" />
        <span>You can edit text directly. Formatted PDF & DOCX maintain standard 1-page bounds.</span>
      </div>

      <div class="flex items-center gap-2">
        <!-- Download DOCX -->
        <button
          :disabled="isExportingDocx || !localContent.trim()"
          class="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-xs font-semibold text-foreground hover:bg-secondary disabled:opacity-50 transition-all shadow-sm"
          @click="handleDownloadDocx"
        >
          <LoadingSpinner v-if="isExportingDocx" size="sm" />
          <Icon v-else icon="lucide:file-type-2" class="h-4 w-4 text-blue-500" />
          <span>Download DOCX</span>
        </button>

        <!-- Download PDF with Shimmer effect -->
        <ShimmerButton
          :disabled="isExportingPdf || !localContent.trim()"
          class="px-5 py-2.5 text-xs font-semibold shadow-md"
          @click="handleDownloadPdf"
        >
          <div class="flex items-center gap-2">
            <LoadingSpinner v-if="isExportingPdf" size="sm" />
            <Icon v-else icon="lucide:download" class="h-4 w-4" />
            <span>Download PDF</span>
          </div>
        </ShimmerButton>
      </div>
    </div>

    <!-- Rewrite Selection Modal -->
    <div
      v-if="showSelectionModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    >
      <div class="w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
          <h4 class="text-base font-semibold text-foreground flex items-center gap-2">
            <Icon icon="lucide:sparkles" class="h-4 w-4 text-primary" />
            Rewrite Selected Passage
          </h4>
          <button
            class="text-muted-foreground hover:text-foreground"
            @click="showSelectionModal = false"
          >
            <Icon icon="lucide:x" class="h-4 w-4" />
          </button>
        </div>

        <div>
          <label class="text-xs font-medium text-muted-foreground">Selected Excerpt:</label>
          <div class="mt-1 max-h-24 overflow-y-auto rounded-lg bg-secondary/80 p-3 text-xs italic font-mono border">
            "{{ selectedSnippet }}"
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-foreground">Specific Instruction (Optional):</label>
          <input
            v-model="customRewritePrompt"
            type="text"
            placeholder="e.g., Make it punchier, emphasize system architecture, or highlight metrics"
            class="mt-1 w-full rounded-lg border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            class="px-3 py-1.5 text-xs rounded-lg border border-border hover:bg-secondary"
            @click="showSelectionModal = false"
          >
            Cancel
          </button>
          <button
            :disabled="isImproving"
            class="px-4 py-1.5 text-xs rounded-lg bg-primary text-white hover:bg-primary/90 flex items-center gap-1.5"
            @click="executeImprovement('rewrite_selection', customRewritePrompt)"
          >
            <LoadingSpinner v-if="isImproving" size="sm" />
            <span>Rewrite Excerpt</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
