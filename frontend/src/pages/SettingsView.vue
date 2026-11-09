<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Icon } from "@iconify/vue";
import { ApiService } from "@/services/api";
import { useDrafts } from "@/composables/useDrafts";
import { useToast } from "@/composables/useToast";
import Badge from "@/components/common/Badge.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import type { BackendHealth } from "@/types";

const { clearAllDrafts } = useDrafts();
const { success, info } = useToast();

const health = ref<BackendHealth | null>(null);
const isLoading = ref(true);
const backendUnavailable = ref(false);

const fetchHealth = async () => {
  isLoading.value = true;
  backendUnavailable.value = false;
  try {
    health.value = await ApiService.getHealth();
  } catch (err) {
    console.error("Health check error:", err);
    health.value = null;
    backendUnavailable.value = true;
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchHealth();
});

const handleClearStorage = () => {
  if (confirm("Are you sure you want to clear all locally saved drafts? This action cannot be undone.")) {
    clearAllDrafts();
    success("All local browser drafts cleared.");
  }
};
</script>

<template>
  <div class="space-y-8 max-w-4xl">
    <!-- Header -->
    <div class="border-b pb-4">
      <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
        <Icon icon="lucide:settings" class="h-6 w-6 text-primary" />
        Application Settings & Diagnostics
      </h1>
      <p class="text-xs text-muted-foreground mt-0.5">
        System environment health, AI model configurations, local storage maintenance, and ATS standards.
      </p>
    </div>

    <!-- Backend Diagnostics Card -->
    <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div class="flex items-center justify-between border-b pb-3">
        <div class="flex items-center gap-2.5">
          <Icon icon="lucide:server" class="h-5 w-5 text-primary" />
          <h3 class="text-sm font-bold text-foreground">Backend Service Diagnostics</h3>
        </div>
        <button
          class="text-xs text-primary hover:underline flex items-center gap-1"
          @click="fetchHealth"
        >
          <Icon icon="lucide:refresh-cw" class="h-3.5 w-3.5" :class="{ 'animate-spin': isLoading }" />
          <span>Refresh</span>
        </button>
      </div>

      <div v-if="isLoading" class="py-6 text-center">
        <LoadingSpinner size="md" label="Checking server status..." />
      </div>

      <div v-else-if="health" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Gemini API Status</div>
            <div
              class="flex items-center gap-1.5 text-sm font-bold"
              :class="health.status === 'Connected' ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'"
            >
              <span
                class="h-2 w-2 rounded-full"
                :class="health.status === 'Connected' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'"
              />
              {{ health.status }}
            </div>
          </div>

          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Configured Gemini Model</div>
            <div class="text-sm font-mono font-bold text-foreground truncate">
              {{ health.config.model }}
            </div>
          </div>

          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Gemini API Key Configured</div>
            <div class="text-sm font-semibold text-foreground">
              <Badge :variant="(health.config.has_gemini_key ?? health.config.has_openai_key) ? 'success' : 'warning'">
                {{ (health.config.has_gemini_key ?? health.config.has_openai_key) ? 'Yes' : 'No' }}
              </Badge>
            </div>
          </div>

          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Demo Mode</div>
            <div class="text-sm font-semibold text-foreground">
              <Badge :variant="health.config.demo_mode ? 'warning' : 'outline'">
                {{ health.config.demo_mode ? 'Enabled' : 'Disabled' }}
              </Badge>
            </div>
          </div>
        </div>

        <div v-if="health.connection?.message" class="text-xs text-muted-foreground flex items-center gap-1.5 pt-1">
          <Icon icon="lucide:info" class="h-4 w-4 shrink-0 text-primary" />
          <span>{{ health.connection.message }}</span>
        </div>
      </div>

      <div v-else-if="backendUnavailable" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Gemini API Status</div>
            <div class="flex items-center gap-1.5 text-sm font-bold text-destructive">
              <span class="h-2 w-2 rounded-full bg-destructive" />
              Backend Unavailable
            </div>
          </div>

          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Configured Gemini Model</div>
            <div class="text-sm font-mono font-bold text-muted-foreground">—</div>
          </div>

          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Gemini API Key Configured</div>
            <div class="text-sm font-semibold text-muted-foreground">
              <Badge variant="outline">Unknown</Badge>
            </div>
          </div>

          <div class="rounded-xl bg-secondary/60 p-3.5 space-y-1">
            <div class="text-[10px] uppercase font-bold text-muted-foreground">Demo Mode</div>
            <div class="text-sm font-semibold text-muted-foreground">
              <Badge variant="outline">Unknown</Badge>
            </div>
          </div>
        </div>

        <div class="rounded-xl bg-destructive/10 p-4 text-xs text-destructive flex items-center gap-2">
          <Icon icon="lucide:alert-circle" class="h-4 w-4 shrink-0" />
          <span>Backend server unreachable at http://127.0.0.1:5000. Ensure Flask is running.</span>
        </div>
      </div>

      <div v-else class="rounded-xl bg-destructive/10 p-4 text-xs text-destructive flex items-center gap-2">
        <Icon icon="lucide:alert-circle" class="h-4 w-4 shrink-0" />
        <span>Backend server unreachable at http://127.0.0.1:5000. Ensure Flask is running.</span>
      </div>
    </div>

    <!-- Google Gemini Configuration Guide -->
    <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div class="flex items-center gap-2.5">
        <Icon icon="lucide:key" class="h-5 w-5 text-indigo-500" />
        <h3 class="text-sm font-bold text-foreground">Configuring Google Gemini Credentials</h3>
      </div>
      <p class="text-xs text-muted-foreground leading-relaxed">
        To configure your Google Gemini API key or switch models, edit the <code class="px-1.5 py-0.5 rounded bg-muted font-mono text-[11px]">backend/.env</code> file:
      </p>

      <div class="rounded-xl bg-muted/60 p-4 font-mono text-xs text-foreground space-y-1 border">
        <div>GEMINI_API_KEY=your_gemini_api_key</div>
        <div>GEMINI_MODEL=gemini-3.8-flash</div>
        <div>DEMO_MODE=false</div>
      </div>

      <p class="text-[11px] text-muted-foreground italic">
        * Important security rule: The Gemini API key is held strictly by the Python backend and never exposed to the frontend browser.
      </p>
    </div>

    <!-- Local Browser Storage Maintenance -->
    <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-3">
      <div class="flex items-center gap-2.5">
        <Icon icon="lucide:database" class="h-5 w-5 text-amber-500" />
        <h3 class="text-sm font-bold text-foreground">Browser Local Storage</h3>
      </div>
      <p class="text-xs text-muted-foreground leading-relaxed">
        Cover letter drafts are stored inside your browser's <code class="px-1 py-0.5 rounded bg-muted text-[11px]">localStorage</code>. They persist across reloads on this machine.
      </p>

      <div class="pt-2">
        <button
          class="px-4 py-2 text-xs font-semibold rounded-xl border border-destructive/30 text-destructive hover:bg-destructive/10 transition-colors flex items-center gap-1.5"
          @click="handleClearStorage"
        >
          <Icon icon="lucide:trash-2" class="h-4 w-4" />
          <span>Clear Local Storage Drafts</span>
        </button>
      </div>
    </div>

    <!-- ATS & Cover Letter Best Practices -->
    <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div class="flex items-center gap-2.5">
        <Icon icon="lucide:check-square" class="h-5 w-5 text-emerald-500" />
        <h3 class="text-sm font-bold text-foreground">Applicant Tracking System (ATS) Best Practices</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground leading-relaxed">
        <div class="space-y-1.5 rounded-xl bg-secondary/40 p-4 border border-border/50">
          <h4 class="font-bold text-foreground flex items-center gap-1.5">
            <Icon icon="lucide:check" class="h-4 w-4 text-emerald-500" />
            Always Do
          </h4>
          <ul class="space-y-1 pl-5 list-disc">
            <li>Mirror exact skill names stated in the job post (e.g. "TypeScript", "FastAPI").</li>
            <li>Connect project outcomes with real-world technical problems.</li>
            <li>Keep formatting clean and within one standard page.</li>
            <li>Use the provided export functions to generate standard PDF or DOCX.</li>
          </ul>
        </div>

        <div class="space-y-1.5 rounded-xl bg-secondary/40 p-4 border border-border/50">
          <h4 class="font-bold text-foreground flex items-center gap-1.5">
            <Icon icon="lucide:x" class="h-4 w-4 text-rose-500" />
            Never Do
          </h4>
          <ul class="space-y-1 pl-5 list-disc">
            <li>Never fabricate credentials, employment history, or degrees.</li>
            <li>Avoid repetitive cliché filler like "I am writing to express my interest".</li>
            <li>Don't submit multi-column text that confuses legacy ATS parsers.</li>
            <li>Don't send scanned image PDFs without an underlying text layer.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
