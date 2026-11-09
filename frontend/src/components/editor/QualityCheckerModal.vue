<script setup lang="ts">
import { ref } from "vue";
import { Icon } from "@iconify/vue";
import Modal from "@/components/common/Modal.vue";
import Badge from "@/components/common/Badge.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import type { QualityReport, SpecificSuggestion } from "@/types";

interface Props {
  isOpen: boolean;
  isLoading: boolean;
  report: QualityReport | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "apply-correction", suggestion: SpecificSuggestion): void;
}>();

const getScoreColor = (score: number) => {
  if (score >= 85) return "text-emerald-500 border-emerald-500 bg-emerald-500/10";
  if (score >= 70) return "text-blue-500 border-blue-500 bg-blue-500/10";
  if (score >= 50) return "text-amber-500 border-amber-500 bg-amber-500/10";
  return "text-rose-500 border-rose-500 bg-rose-500/10";
};
</script>

<template>
  <Modal
    :is-open="props.isOpen"
    title="Cover Letter Quality Analysis"
    subtitle="AI-powered evaluation of readability, tone, job relevance, and ATS alignment"
    max-width="max-w-2xl"
    @close="emit('close')"
  >
    <!-- Loading State -->
    <div v-if="props.isLoading" class="py-12 text-center space-y-3">
      <LoadingSpinner size="lg" label="Analyzing letter quality..." />
      <p class="text-xs text-muted-foreground">
        Reviewing tone, repetition, grammar, alignment, and ATS keyword presence...
      </p>
    </div>

    <!-- Report Content -->
    <div v-else-if="props.report" class="space-y-6 py-2">
      <!-- Top Score Card -->
      <div class="flex flex-col sm:flex-row items-center gap-6 rounded-xl border border-border bg-card p-5 shadow-sm">
        <div
          :class="[
            'flex h-24 w-24 shrink-0 flex-col items-center justify-center rounded-2xl border-2 font-bold',
            getScoreColor(props.report.overall_score)
          ]"
        >
          <span class="text-3xl tracking-tight">{{ props.report.overall_score }}</span>
          <span class="text-[10px] uppercase tracking-wider opacity-80">Score</span>
        </div>

        <div class="space-y-2 flex-1 text-center sm:text-left">
          <h4 class="text-base font-semibold text-foreground">
            {{ props.report.overall_score >= 80 ? 'Publication Ready' : 'Needs Optimization' }}
          </h4>
          <p class="text-xs text-muted-foreground leading-relaxed">
            {{ props.report.assessment }}
          </p>

          <!-- Category Metrics -->
          <div v-if="props.report.metrics" class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
            <div
              v-for="(val, metric) in props.report.metrics"
              :key="metric"
              class="rounded-lg bg-secondary/60 p-2 text-center"
            >
              <div class="text-[10px] uppercase font-semibold text-muted-foreground">
                {{ metric }}
              </div>
              <div class="text-sm font-bold text-foreground mt-0.5">
                {{ val }}%
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Positive Highlights -->
      <div v-if="props.report.positive_observations?.length" class="space-y-2">
        <h5 class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 uppercase tracking-wider">
          <Icon icon="lucide:check-circle" class="h-4 w-4" />
          Key Strengths
        </h5>
        <ul class="space-y-1.5">
          <li
            v-for="(item, i) in props.report.positive_observations"
            :key="i"
            class="text-xs text-muted-foreground flex items-start gap-2 rounded-lg bg-emerald-500/5 p-2.5 border border-emerald-500/10"
          >
            <Icon icon="lucide:check" class="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
            <span>{{ item }}</span>
          </li>
        </ul>
      </div>

      <!-- Specific Actionable Suggestions -->
      <div v-if="props.report.specific_suggestions?.length" class="space-y-3">
        <h5 class="text-xs font-semibold text-primary flex items-center gap-1.5 uppercase tracking-wider">
          <Icon icon="lucide:sparkles" class="h-4 w-4" />
          Recommended Enhancements
        </h5>

        <div
          v-for="(sug, idx) in props.report.specific_suggestions"
          :key="idx"
          class="rounded-xl border border-border bg-card p-4 space-y-2.5 shadow-sm hover:border-primary/40 transition-colors"
        >
          <div class="flex items-start justify-between gap-2">
            <div>
              <span class="text-xs font-semibold text-foreground flex items-center gap-2">
                {{ sug.title }}
                <Badge variant="outline" class="text-[10px]">{{ sug.category }}</Badge>
              </span>
              <p class="text-xs text-muted-foreground mt-1">
                {{ sug.description }}
              </p>
            </div>
          </div>

          <!-- Suggested text replacement -->
          <div
            v-if="sug.recommended_correction"
            class="rounded-lg bg-secondary/80 p-3 border border-border/80 space-y-2"
          >
            <div class="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between">
              <span>Proposed Replacement:</span>
              <button
                class="text-primary hover:text-primary/80 font-medium flex items-center gap-1 text-xs hover:underline"
                @click="emit('apply-correction', sug)"
              >
                <Icon icon="lucide:check" class="h-3.5 w-3.5" />
                Apply to Editor
              </button>
            </div>
            <p class="text-xs font-mono text-foreground/90 italic">
              "{{ sug.recommended_correction }}"
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        class="px-4 py-2 text-xs font-medium rounded-lg border border-border hover:bg-secondary transition-colors"
        @click="emit('close')"
      >
        Close
      </button>
    </template>
  </Modal>
</template>
