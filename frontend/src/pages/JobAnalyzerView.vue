<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { ApiService } from "@/services/api";
import { useToast } from "@/composables/useToast";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Badge from "@/components/common/Badge.vue";
import ShimmerButton from "@/components/inspira/ShimmerButton.vue";
import BorderBeam from "@/components/inspira/BorderBeam.vue";
import DotPattern from "@/components/inspira/DotPattern.vue";
import AnimatedGradientText from "@/components/inspira/AnimatedGradientText.vue";
import type { JobAnalysis } from "@/types";

const router = useRouter();
const { success, error, info } = useToast();

const rawJobDescription = ref("");
const jobTitle = ref("");
const companyName = ref("");
const isAnalyzing = ref(false);
const analysisResult = ref<JobAnalysis | null>(null);

const runAnalysis = async () => {
  if (!rawJobDescription.value.trim() || rawJobDescription.value.trim().length < 20) {
    error("Please enter a job description with at least 20 characters.");
    return;
  }

  isAnalyzing.value = true;
  try {
    const res = await ApiService.analyzeJob({
      job_description: rawJobDescription.value,
      job_title: jobTitle.value.trim() || undefined,
      company_name: companyName.value.trim() || undefined
    });

    analysisResult.value = res;
    success("Job description analyzed successfully!");
  } catch (err: any) {
    error(err.message || "Failed to analyze job description.");
  } finally {
    isAnalyzing.value = false;
  }
};

const sendToWorkspace = () => {
  if (!analysisResult.value) return;
  router.push({
    path: "/workspace",
    query: {
      jobTitle: analysisResult.value.job_title || jobTitle.value,
      company: analysisResult.value.company_name || companyName.value,
      jobDesc: rawJobDescription.value
    }
  });
};

const loadSampleJob = () => {
  jobTitle.value = "Senior Full Stack Engineer";
  companyName.value = "Vercel";
  rawJobDescription.value = `We are looking for a Senior Full Stack Engineer to join our Core Platform team.
Responsibilities:
- Architect and develop high-throughput serverless systems and modern edge APIs.
- Collaborate with frontend designers and infrastructure teams to scale global web infrastructure.
- Write clean, maintainable, and thoroughly tested TypeScript and Python code.

Requirements:
- 4+ years of professional experience with React, Next.js, TypeScript, and Node.js.
- Deep familiarity with distributed systems, AWS/GCP, Docker, and PostgreSQL.
- Strong knowledge of RESTful APIs, GraphQL, and modern CI/CD automation pipelines.
- Excellent communication, team leadership, and asynchronous problem-solving skills.
- Bachelor's degree in Computer Science or equivalent practical experience.

Nice to have:
- Experience with WebAssembly, Rust, or Edge computing runtimes.
- Contributions to popular open-source web frameworks.`;
  info("Sample job description loaded.");
};
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl border border-border bg-card/60 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <DotPattern class="opacity-30" />
      <div class="relative z-10">
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Icon icon="lucide:briefcase" class="h-6 w-6 text-primary" />
          Job Description Analyzer
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          Deconstruct job posts into structured technical requirements, frameworks, keywords, and responsibilities.
        </p>
      </div>

      <button
        class="self-start sm:self-auto relative z-10 transition-transform active:scale-95"
        @click="loadSampleJob"
      >
        <AnimatedGradientText class="cursor-pointer">
          <Icon icon="lucide:sparkles" class="h-3.5 w-3.5 text-blue-500" />
          <span>Load Sample Job Post</span>
        </AnimatedGradientText>
      </button>
    </div>

    <!-- Input Section -->
    <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="text-xs font-semibold text-foreground">Target Role (Optional)</label>
          <input
            v-model="jobTitle"
            type="text"
            placeholder="e.g. Senior Software Engineer"
            class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div>
          <label class="text-xs font-semibold text-foreground">Company Name (Optional)</label>
          <input
            v-model="companyName"
            type="text"
            placeholder="e.g. Stripe"
            class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      <div>
        <label class="text-xs font-semibold text-foreground">Job Description Text *</label>
        <textarea
          v-model="rawJobDescription"
          rows="7"
          placeholder="Paste the full job posting text here..."
          class="mt-1 w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
        />
      </div>

      <div class="flex justify-end pt-1">
        <ShimmerButton
          :disabled="isAnalyzing"
          class="px-6 py-2.5 text-xs font-semibold shadow-md"
          @click="runAnalysis"
        >
          <div class="flex items-center gap-2">
            <LoadingSpinner v-if="isAnalyzing" size="sm" />
            <Icon v-else icon="lucide:scan" class="h-4 w-4" />
            <span>Analyze Job Requirements</span>
          </div>
        </ShimmerButton>
      </div>
    </div>

    <!-- Analysis Results Section -->
    <div v-if="analysisResult" class="relative overflow-hidden rounded-3xl border border-border bg-card/80 p-6 sm:p-8 shadow-sm space-y-6">
      <BorderBeam :size="250" :duration="12" color-from="#3b82f6" color-to="#10b981" />
      <div class="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b pb-4">
        <div>
          <h2 class="text-lg font-bold text-foreground flex items-center gap-2">
            <span>{{ analysisResult.job_title || jobTitle || 'Analyzed Position' }}</span>
            <span v-if="analysisResult.company_name" class="text-muted-foreground font-normal">
              at {{ analysisResult.company_name }}
            </span>
          </h2>
          <p class="text-xs text-muted-foreground mt-0.5">
            Key criteria extracted to align your application with hiring manager expectations.
          </p>
        </div>

        <button
          class="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-white hover:bg-primary/90 transition-all shadow-sm"
          @click="sendToWorkspace"
        >
          <Icon icon="lucide:arrow-right-circle" class="h-4 w-4" />
          <span>Apply to Cover Letter</span>
        </button>
      </div>

      <!-- Result Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <!-- Programming Languages & Frameworks -->
        <div class="rounded-2xl border border-border bg-card p-5 space-y-3 shadow-sm">
          <h4 class="text-xs font-bold text-foreground flex items-center gap-2 uppercase tracking-wider">
            <Icon icon="lucide:code-2" class="h-4 w-4 text-blue-500" />
            Languages & Frameworks
          </h4>
          <div class="flex flex-wrap gap-1.5 pt-1">
            <Badge
              v-for="lang in analysisResult.programming_languages"
              :key="lang"
              variant="default"
            >
              {{ lang }}
            </Badge>
            <Badge
              v-for="fw in analysisResult.frameworks"
              :key="fw"
              variant="secondary"
            >
              {{ fw }}
            </Badge>
            <span
              v-if="analysisResult.programming_languages.length === 0 && analysisResult.frameworks.length === 0"
              class="text-xs text-muted-foreground italic"
            >
              No specific languages highlighted.
            </span>
          </div>
        </div>

        <!-- Tools, Cloud & Databases -->
        <div class="rounded-2xl border border-border bg-card p-5 space-y-3 shadow-sm">
          <h4 class="text-xs font-bold text-foreground flex items-center gap-2 uppercase tracking-wider">
            <Icon icon="lucide:cloud" class="h-4 w-4 text-purple-500" />
            Tools & Infrastructure
          </h4>
          <div class="flex flex-wrap gap-1.5 pt-1">
            <Badge
              v-for="tool in analysisResult.tools"
              :key="tool"
              variant="outline"
            >
              {{ tool }}
            </Badge>
            <span v-if="analysisResult.tools.length === 0" class="text-xs text-muted-foreground italic">
              No specific tooling specified.
            </span>
          </div>
        </div>

        <!-- Experience & Qualifications -->
        <div class="rounded-2xl border border-border bg-card p-5 space-y-3 shadow-sm">
          <h4 class="text-xs font-bold text-foreground flex items-center gap-2 uppercase tracking-wider">
            <Icon icon="lucide:graduation-cap" class="h-4 w-4 text-emerald-500" />
            Experience & Education
          </h4>
          <div class="space-y-2 text-xs text-muted-foreground">
            <div>
              <span class="font-semibold text-foreground">Experience:</span>
              <p class="mt-0.5">{{ analysisResult.experience_requirements || 'Not explicitly stated' }}</p>
            </div>
            <div>
              <span class="font-semibold text-foreground">Education:</span>
              <p class="mt-0.5">{{ analysisResult.educational_qualifications || 'Not explicitly stated' }}</p>
            </div>
          </div>
        </div>

        <!-- Key Responsibilities -->
        <div class="md:col-span-2 rounded-2xl border border-border bg-card p-5 space-y-3 shadow-sm">
          <h4 class="text-xs font-bold text-foreground flex items-center gap-2 uppercase tracking-wider">
            <Icon icon="lucide:list-checks" class="h-4 w-4 text-amber-500" />
            Core Responsibilities
          </h4>
          <ul class="space-y-1.5 text-xs text-muted-foreground">
            <li
              v-for="(resp, i) in analysisResult.responsibilities"
              :key="i"
              class="flex items-start gap-2 rounded-lg bg-secondary/50 p-2 border border-border/50"
            >
              <Icon icon="lucide:check" class="h-3.5 w-3.5 text-emerald-500 shrink-0 mt-0.5" />
              <span>{{ resp }}</span>
            </li>
          </ul>
        </div>

        <!-- ATS Search Keywords -->
        <div class="rounded-2xl border border-border bg-card p-5 space-y-3 shadow-sm">
          <h4 class="text-xs font-bold text-foreground flex items-center gap-2 uppercase tracking-wider">
            <Icon icon="lucide:key" class="h-4 w-4 text-rose-500" />
            Important ATS Keywords
          </h4>
          <div class="flex flex-wrap gap-1.5 pt-1">
            <span
              v-for="kw in analysisResult.keywords"
              :key="kw"
              class="text-[11px] px-2.5 py-1 rounded-lg bg-secondary text-foreground font-mono"
            >
              {{ kw }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
