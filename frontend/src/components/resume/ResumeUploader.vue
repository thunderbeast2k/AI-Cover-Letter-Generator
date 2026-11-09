<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";
import { ApiService } from "@/services/api";
import type { ParsedResume } from "@/types";
import { useToast } from "@/composables/useToast";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Badge from "@/components/common/Badge.vue";

const emit = defineEmits<{
  (e: "parsed", data: ParsedResume): void;
  (e: "cleared"): void;
}>();

const { error, success } = useToast();

const isDragging = ref(false);
const isUploading = ref(false);
const uploadProgress = ref(0);
const uploadedFileName = ref<string | null>(null);
const parsedResult = ref<ParsedResume | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = true;
};

const handleDragLeave = () => {
  isDragging.value = false;
};

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    processFile(e.dataTransfer.files[0]);
  }
};

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    processFile(target.files[0]);
  }
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const processFile = async (file: File) => {
  const allowed = [".pdf", ".docx"];
  const ext = "." + file.name.split(".").pop()?.toLowerCase();

  if (!allowed.includes(ext)) {
    error(`Unsupported file type: ${ext}. Please upload a PDF or DOCX file.`);
    return;
  }

  // 5MB limit
  if (file.size > 5 * 1024 * 1024) {
    error("File exceeds 5MB size limit. Please upload a smaller document.");
    return;
  }

  isUploading.value = true;
  uploadProgress.value = 25;
  uploadedFileName.value = file.name;

  try {
    uploadProgress.value = 60;
    const result = await ApiService.parseResume(file);
    uploadProgress.value = 100;
    parsedResult.value = result;

    if (result.warnings && result.warnings.length > 0) {
      result.warnings.forEach((w) => error(w, "Parser Notice"));
    }

    success("Resume parsed successfully! Details populated into your form.");
    emit("parsed", result);
  } catch (err: any) {
    uploadedFileName.value = null;
    parsedResult.value = null;
    error(err.message || "Failed to parse resume document.");
  } finally {
    isUploading.value = false;
    if (fileInput.value) fileInput.value.value = "";
  }
};

const removeFile = () => {
  uploadedFileName.value = null;
  parsedResult.value = null;
  emit("cleared");
};
</script>

<template>
  <div class="space-y-4">
    <!-- Dropzone Area -->
    <div
      v-if="!uploadedFileName"
      :class="[
        'relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-all cursor-pointer',
        isDragging
          ? 'border-primary bg-primary/5 scale-[1.01]'
          : 'border-border/80 hover:border-primary/50 hover:bg-muted/40'
      ]"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        class="hidden"
        @change="handleFileSelect"
      />

      <div
        class="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-3 shadow-inner"
      >
        <Icon icon="lucide:file-up" class="h-7 w-7" />
      </div>

      <h4 class="text-base font-semibold text-foreground">
        Upload your Resume (PDF or DOCX)
      </h4>
      <p class="text-xs text-muted-foreground mt-1 max-w-sm">
        Drag and drop your file here, or click to browse. Max size 5 MB.
      </p>

      <div class="flex items-center gap-4 mt-4 text-[11px] text-muted-foreground/80 font-medium">
        <span class="flex items-center gap-1">
          <Icon icon="lucide:check-circle" class="h-3.5 w-3.5 text-emerald-500" />
          Text Extraction
        </span>
        <span class="flex items-center gap-1">
          <Icon icon="lucide:shield-check" class="h-3.5 w-3.5 text-emerald-500" />
          Secure & Deleted After Parse
        </span>
        <span class="flex items-center gap-1">
          <Icon icon="lucide:cpu" class="h-3.5 w-3.5 text-emerald-500" />
          Multi-page Support
        </span>
      </div>
    </div>

    <!-- Upload Progress State -->
    <div
      v-else-if="isUploading"
      class="rounded-xl border border-border bg-card p-6 text-center space-y-3"
    >
      <LoadingSpinner size="lg" label="Extracting resume content..." />
      <p class="text-xs text-muted-foreground">
        Analyzing document structure, extracting contact info and technical skills...
      </p>
      <div class="w-full bg-secondary h-2 rounded-full overflow-hidden max-w-xs mx-auto">
        <div
          class="bg-primary h-full transition-all duration-300"
          :style="{ width: `${uploadProgress}%` }"
        />
      </div>
    </div>

    <!-- Parsed State Banner -->
    <div
      v-else
      class="rounded-xl border border-emerald-500/30 bg-emerald-50/50 dark:bg-emerald-950/20 p-4 transition-all"
    >
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-3">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
          >
            <Icon icon="lucide:file-check-2" class="h-5 w-5" />
          </div>
          <div>
            <h5 class="text-sm font-semibold text-foreground flex items-center gap-2">
              {{ uploadedFileName }}
              <Badge variant="success">Parsed</Badge>
            </h5>
            <p class="text-xs text-muted-foreground">
              {{ parsedResult?.full_name || 'Candidate profile' }} &bull;
              {{ parsedResult?.technical_skills.length || 0 }} skills detected &bull;
              {{ parsedResult?.page_count || 1 }} page(s)
            </p>
          </div>
        </div>

        <button
          class="text-xs text-muted-foreground hover:text-destructive flex items-center gap-1 px-2 py-1 rounded-md hover:bg-destructive/10 transition-colors"
          title="Remove resume"
          @click="removeFile"
        >
          <Icon icon="lucide:trash-2" class="h-4 w-4" />
          Remove
        </button>
      </div>

      <!-- Skills Preview Chips -->
      <div
        v-if="parsedResult && parsedResult.technical_skills.length > 0"
        class="mt-3 flex flex-wrap gap-1.5 pt-3 border-t border-emerald-500/20"
      >
        <span
          v-for="skill in parsedResult.technical_skills.slice(0, 10)"
          :key="skill"
          class="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-medium"
        >
          {{ skill }}
        </span>
        <span
          v-if="parsedResult.technical_skills.length > 10"
          class="text-[11px] px-2 py-0.5 rounded-full bg-secondary text-muted-foreground"
        >
          +{{ parsedResult.technical_skills.length - 10 }} more
        </span>
      </div>
    </div>
  </div>
</template>
