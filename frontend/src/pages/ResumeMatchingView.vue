<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { ApiService } from "@/services/api";
import { useToast } from "@/composables/useToast";
import ResumeUploader from "@/components/resume/ResumeUploader.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Badge from "@/components/common/Badge.vue";
import ShimmerButton from "@/components/inspira/ShimmerButton.vue";
import NumberTicker from "@/components/inspira/NumberTicker.vue";
import DotPattern from "@/components/inspira/DotPattern.vue";
import type { ResumeMatch, ParsedResume } from "@/types";

const router = useRouter();
const { success, error, info } = useToast();

const resumeSkillsInput = ref("Python, TypeScript, React, Docker, PostgreSQL, REST APIs");
const candidateProjects = ref("Built an automated microservice deployment system and real-time dashboard.");
const candidateExperience = ref("2 years software development experience.");
const jobDescription = ref("");
const jobTitle = ref("");
const isMatching = ref(false);
const matchResult = ref<ResumeMatch | null>(null);

const handleParsedResume = (data: ParsedResume) => {
  if (data.technical_skills?.length) {
    resumeSkillsInput.value = data.technical_skills.join(", ");
  }
  if (data.projects) candidateProjects.value = data.projects;
  if (data.relevant_experience) candidateExperience.value = data.relevant_experience;
  info("Resume credentials populated into matching form.");
};

const runMatch = async () => {
  if (!jobDescription.value.trim() || jobDescription.value.trim().length < 15) {
    error("Please enter a job description to compare against.");
    return;
  }

  const skillsList = resumeSkillsInput.value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  isMatching.value = true;
  try {
    const res = await ApiService.matchResume({
      candidate_skills: skillsList,
      job_description: jobDescription.value,
      candidate_projects: candidateProjects.value,
      candidate_experience: candidateExperience.value,
      job_title: jobTitle.value.trim() || undefined
    });

    matchResult.value = res;
    success("Resume-to-job match computed!");
  } catch (err: any) {
    error(err.message || "Failed to calculate match.");
  } finally {
    isMatching.value = false;
  }
};

const sendToWorkspace = () => {
  const skillsList = resumeSkillsInput.value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  router.push({
    path: "/workspace",
    query: {
      jobTitle: jobTitle.value,
      jobDesc: jobDescription.value
    }
  });
};

const getScoreColor = (score: number) => {
  if (score >= 80) return "text-emerald-500 border-emerald-500 bg-emerald-500/10";
  if (score >= 65) return "text-blue-500 border-blue-500 bg-blue-500/10";
  if (score >= 45) return "text-amber-500 border-amber-500 bg-amber-500/10";
  return "text-rose-500 border-rose-500 bg-rose-500/10";
};
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl border border-border bg-card/60 p-6 shadow-xs">
      <DotPattern class="opacity-30" />
      <div class="relative z-10">
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Icon icon="lucide:git-compare" class="h-6 w-6 text-primary" />
          Resume & Job Description Matching
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          Heuristic alignment analysis comparing your demonstrated skills, hands-on projects, and target role criteria.
        </p>
      </div>
    </div>

    <!-- 2 Column Input Form -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left: Candidate Credentials -->
      <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
        <div>
          <h3 class="text-sm font-semibold text-foreground flex items-center gap-2">
            <Icon icon="lucide:file-user" class="h-4 w-4 text-primary" />
            Applicant Profile & Skills
          </h3>
          <p class="text-xs text-muted-foreground mt-0.5">
            Upload your resume or enter your active skills and projects below.
          </p>
        </div>

        <ResumeUploader @parsed="handleParsedResume" />

        <div class="pt-2 border-t space-y-3">
          <div>
            <label class="text-xs font-semibold text-foreground">Skills (Comma-separated)</label>
            <textarea
              v-model="resumeSkillsInput"
              rows="3"
              placeholder="e.g. Python, React, Docker, PostgreSQL, AWS..."
              class="mt-1 w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground">Hands-on Projects / Capstones</label>
            <textarea
              v-model="candidateProjects"
              rows="2"
              placeholder="e.g. Distributed Crawler in Python; E-commerce portal..."
              class="mt-1 w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>
        </div>
      </div>

      <!-- Right: Target Job Description -->
      <div class="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4 flex flex-col justify-between">
        <div class="space-y-4">
          <div>
            <h3 class="text-sm font-semibold text-foreground flex items-center gap-2">
              <Icon icon="lucide:briefcase" class="h-4 w-4 text-primary" />
              Target Job Specification
            </h3>
            <p class="text-xs text-muted-foreground mt-0.5">
              Paste the position requirements to compute exact alignment.
            </p>
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground">Job Title (Optional)</label>
            <input
              v-model="jobTitle"
              type="text"
              placeholder="e.g. Full Stack Engineer"
              class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground">Job Description *</label>
            <textarea
              v-model="jobDescription"
              rows="8"
              placeholder="Paste the target job description..."
              class="mt-1 w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>
        </div>

        <div class="pt-2">
          <ShimmerButton
            :disabled="isMatching"
            class="w-full py-3 text-xs font-semibold shadow-md"
            @click="runMatch"
          >
            <div class="flex items-center justify-center gap-2">
              <LoadingSpinner v-if="isMatching" size="sm" />
              <Icon v-else icon="lucide:calculator" class="h-4 w-4" />
              <span>Calculate Match Estimate</span>
            </div>
          </ShimmerButton>
        </div>
      </div>
    </div>

    <!-- Match Analysis Results -->
    <div v-if="matchResult" class="space-y-6">
      <div class="rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-sm space-y-6">
        <!-- Top Score Banner -->
        <div class="flex flex-col sm:flex-row items-center gap-6 pb-6 border-b">
          <div
            :class="[
              'flex h-28 w-28 shrink-0 flex-col items-center justify-center rounded-3xl border-2 font-bold transition-all shadow-md',
              getScoreColor(matchResult.match_percentage)
            ]"
          >
            <NumberTicker :value="matchResult.match_percentage" suffix="%" class="text-4xl tracking-tight" />
            <span class="text-[10px] uppercase tracking-wider opacity-80">Match Est.</span>
          </div>

          <div class="space-y-2 flex-1 text-center sm:text-left">
            <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2">
              <h3 class="text-lg font-bold text-foreground">
                {{ matchResult.match_percentage >= 75 ? 'Strong Candidate Alignment' : 'Moderate Alignment' }}
              </h3>
              <Badge v-if="matchResult.is_fresher_friendly" variant="success">
                <Icon icon="lucide:graduation-cap" class="h-3 w-3 mr-1" />
                Fresher Friendly Role
              </Badge>
            </div>
            <p class="text-xs text-muted-foreground leading-relaxed">
              {{ matchResult.experience_match_summary }}
            </p>
            <p class="text-[11px] text-muted-foreground/80 font-mono italic">
              {{ matchResult.scoring_explanation }}
            </p>
          </div>

          <button
            class="shrink-0 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-white hover:bg-primary/90 transition-all shadow-sm flex items-center gap-2"
            @click="sendToWorkspace"
          >
            <Icon icon="lucide:pen-tool" class="h-4 w-4" />
            <span>Generate Letter from Match</span>
          </button>
        </div>

        <!-- Skills Breakdown Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Matched Skills -->
          <div class="rounded-xl border border-emerald-500/20 bg-emerald-50/30 dark:bg-emerald-950/20 p-5 space-y-3">
            <h4 class="text-xs font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-2 uppercase tracking-wider">
              <Icon icon="lucide:check-circle" class="h-4 w-4" />
              Matched Technical Skills ({{ matchResult.matched_skills.length }})
            </h4>
            <div class="flex flex-wrap gap-1.5 pt-1">
              <span
                v-for="s in matchResult.matched_skills"
                :key="s"
                class="text-xs px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-medium border border-emerald-500/20"
              >
                {{ s }}
              </span>
              <span v-if="matchResult.matched_skills.length === 0" class="text-xs text-muted-foreground italic">
                No direct skill matches detected.
              </span>
            </div>
          </div>

          <!-- Missing Skills -->
          <div class="rounded-xl border border-amber-500/20 bg-amber-50/30 dark:bg-amber-950/20 p-5 space-y-3">
            <h4 class="text-xs font-bold text-amber-700 dark:text-amber-400 flex items-center gap-2 uppercase tracking-wider">
              <Icon icon="lucide:alert-circle" class="h-4 w-4" />
              Unlisted or Missing Skills ({{ matchResult.missing_skills.length }})
            </h4>
            <div class="flex flex-wrap gap-1.5 pt-1">
              <span
                v-for="s in matchResult.missing_skills"
                :key="s"
                class="text-xs px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-700 dark:text-amber-300 font-medium border border-amber-500/20"
              >
                {{ s }}
              </span>
              <span v-if="matchResult.missing_skills.length === 0" class="text-xs text-muted-foreground italic">
                All major job skills are covered!
              </span>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div class="space-y-3 pt-2">
          <h4 class="text-xs font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
            <Icon icon="lucide:lightbulb" class="h-4 w-4 text-primary" />
            Strategic Improvement Recommendations
          </h4>
          <ul class="space-y-2">
            <li
              v-for="(rec, idx) in matchResult.recommendations"
              :key="idx"
              class="flex items-start gap-2.5 rounded-xl border border-border bg-card p-3 text-xs text-muted-foreground"
            >
              <Icon icon="lucide:arrow-right" class="h-4 w-4 text-primary shrink-0 mt-0.5" />
              <span>{{ rec }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
