<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Icon } from "@iconify/vue";
import { ApiService } from "@/services/api";
import { useToast } from "@/composables/useToast";
import { useDrafts } from "@/composables/useDrafts";
import ResumeUploader from "@/components/resume/ResumeUploader.vue";
import LiveDocumentEditor from "@/components/editor/LiveDocumentEditor.vue";
import QualityCheckerModal from "@/components/editor/QualityCheckerModal.vue";
import TemplateSelectorModal from "@/components/templates/TemplateSelectorModal.vue";
import ShimmerButton from "@/components/inspira/ShimmerButton.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import Badge from "@/components/common/Badge.vue";
import type {
  PersonalInfo,
  JobInfo,
  ProfessionalInfo,
  ParsedResume,
  QualityReport,
  SpecificSuggestion,
  WritingStyle
} from "@/types";

const route = useRoute();
const { success, error, info, warning } = useToast();
const { getDraft, saveDraft } = useDrafts();

// Workspace Tabs
const activeTab = ref<"resume" | "personal" | "job" | "professional" | "style">("job");

// Form State
const personalInfo = reactive<PersonalInfo>({
  full_name: "",
  email: "",
  phone: "",
  location: "",
  linkedin_url: "",
  portfolio_url: "",
  github_url: ""
});

const jobInfo = reactive<JobInfo>({
  job_title: "",
  company_name: "",
  hiring_manager_name: "",
  company_location: "",
  job_description: "",
  application_type: "Full-time"
});

const professionalInfo = reactive<ProfessionalInfo>({
  technical_skills: [],
  relevant_experience: "",
  projects: "",
  achievements: "",
  certifications: "",
  education: "",
  additional_info: ""
});

const newSkillInput = ref("");
const selectedStyle = ref<WritingStyle>("Professional");
const activeTemplateId = ref("classic");
const currentCoverLetter = ref("");
const activeDraftId = ref<string | null>(null);

// Loading & Modal States
const isGenerating = ref(false);
const isQualityModalOpen = ref(false);
const isQualityLoading = ref(false);
const qualityReport = ref<QualityReport | null>(null);
const isTemplateModalOpen = ref(false);

const writingStyles: { name: WritingStyle; description: string; icon: string }[] = [
  { name: "Professional", description: "Balanced, polite, corporate-ready", icon: "lucide:briefcase" },
  { name: "Concise", description: "Punchy, high-impact, under 250 words", icon: "lucide:zap" },
  { name: "Confident", description: "Assertive, outcome-driven, leadership", icon: "lucide:award" },
  { name: "Technical", description: "Architecture, deep tech stack focus", icon: "lucide:code-2" },
  { name: "Creative", description: "Narrative storytelling hook", icon: "lucide:feather" },
  { name: "Entry-Level / Fresher", description: "Emphasizes projects & coursework", icon: "lucide:graduation-cap" },
  { name: "Executive", description: "Strategic, visionary, business-scale", icon: "lucide:crown" }
];

onMounted(() => {
  // If navigated with draftId, load draft
  const draftId = route.query.draftId as string;
  if (draftId) {
    const draft = getDraft(draftId);
    if (draft) {
      activeDraftId.value = draft.id;
      currentCoverLetter.value = draft.cover_letter;
      selectedStyle.value = draft.writing_style as WritingStyle;
      activeTemplateId.value = draft.template_id || "classic";
      Object.assign(personalInfo, draft.personal_info);
      Object.assign(jobInfo, draft.job_info);
      Object.assign(professionalInfo, draft.professional_info);
      info(`Loaded draft: ${draft.title}`);
    }
  }

  // If passed query params e.g. from job analyzer
  if (route.query.jobTitle) {
    jobInfo.job_title = route.query.jobTitle as string;
  }
  if (route.query.company) {
    jobInfo.company_name = route.query.company as string;
  }
  if (route.query.jobDesc) {
    jobInfo.job_description = route.query.jobDesc as string;
  }
});

// Resume Parsed Handler
const handleResumeParsed = (data: ParsedResume) => {
  if (data.full_name) personalInfo.full_name = data.full_name;
  if (data.email) personalInfo.email = data.email;
  if (data.phone) personalInfo.phone = data.phone;
  if (data.location) personalInfo.location = data.location;
  if (data.linkedin_url) personalInfo.linkedin_url = data.linkedin_url;
  if (data.github_url) personalInfo.github_url = data.github_url;
  if (data.portfolio_url) personalInfo.portfolio_url = data.portfolio_url;

  if (data.technical_skills && data.technical_skills.length > 0) {
    professionalInfo.technical_skills = Array.from(new Set([...professionalInfo.technical_skills, ...data.technical_skills]));
  }
  if (data.relevant_experience) professionalInfo.relevant_experience = data.relevant_experience;
  if (data.projects) professionalInfo.projects = data.projects;
  if (data.achievements) professionalInfo.achievements = data.achievements;
  if (data.certifications) professionalInfo.certifications = data.certifications;
  if (data.education) professionalInfo.education = data.education;

  // Auto-switch to job info tab so user enters the target position
  activeTab.value = "job";
};

// Skill Management
const addSkill = () => {
  const s = newSkillInput.value.trim();
  if (s && !professionalInfo.technical_skills.includes(s)) {
    professionalInfo.technical_skills.push(s);
    newSkillInput.value = "";
  }
};

const removeSkill = (s: string) => {
  professionalInfo.technical_skills = professionalInfo.technical_skills.filter((item) => item !== s);
};

// Generate Cover Letter
const generateLetter = async () => {
  if (!personalInfo.full_name.trim()) {
    error("Please enter candidate full name in the Personal tab.");
    activeTab.value = "personal";
    return;
  }
  if (!jobInfo.job_title.trim() || !jobInfo.company_name.trim()) {
    error("Please enter Job Title and Company Name in the Job tab.");
    activeTab.value = "job";
    return;
  }
  if (!jobInfo.job_description.trim() || jobInfo.job_description.length < 15) {
    error("Please provide a job description or key requirements.");
    activeTab.value = "job";
    return;
  }

  isGenerating.value = true;
  try {
    const res = await ApiService.generateCoverLetter({
      personal_info: personalInfo,
      job_info: jobInfo,
      professional_info: professionalInfo,
      writing_style: selectedStyle.value,
      template_id: activeTemplateId.value
    });

    currentCoverLetter.value = res.cover_letter;
    if (res.demo_mode) {
      info("Generated using Demo Mode (offline). Set GEMINI_API_KEY in backend/.env to use live Gemini models.");
    } else {
      success("Personalized cover letter generated!");
    }
  } catch (err: any) {
    const errorMsg = err.response?.data?.error || err.message || "Failed to generate cover letter.";
    error(errorMsg);
  } finally {
    isGenerating.value = false;
  }
};

// Save Local Draft
const handleSaveDraft = () => {
  if (!currentCoverLetter.value.trim()) {
    error("Cannot save an empty draft.");
    return;
  }

  const defaultTitle = `${jobInfo.job_title || 'Application'} at ${jobInfo.company_name || 'Target Company'}`;
  const saved = saveDraft({
    id: activeDraftId.value || undefined,
    title: defaultTitle,
    cover_letter: currentCoverLetter.value,
    writing_style: selectedStyle.value,
    template_id: activeTemplateId.value,
    personal_info: personalInfo,
    job_info: jobInfo,
    professional_info: professionalInfo
  });

  activeDraftId.value = saved.id;
  success(`Draft saved locally: "${saved.title}"`);
};

// Quality Check Modal Handlers
const openQualityModal = (report: QualityReport | null) => {
  qualityReport.value = report;
  isQualityLoading.value = report === null;
  isQualityModalOpen.value = true;
};

const handleApplyCorrection = (sug: SpecificSuggestion) => {
  if (sug.recommended_correction) {
    // Append or replace
    currentCoverLetter.value += `\n\n${sug.recommended_correction}`;
    success(`Applied suggestion: "${sug.title}"`);
  }
};

// Clear letter with confirmation
const clearLetter = () => {
  if (confirm("Are you sure you want to clear the editor? Any unsaved edits will be lost.")) {
    currentCoverLetter.value = "";
    info("Editor cleared.");
  }
};
</script>

<template>
  <div class="space-y-6">
    <!-- Workspace Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Icon icon="lucide:pen-tool" class="h-6 w-6 text-primary" />
          Cover Letter Workspace
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          Configure applicant qualifications and target job criteria on the left; craft and export your live letter on the right.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          v-if="currentCoverLetter"
          class="text-xs text-muted-foreground hover:text-destructive flex items-center gap-1 px-3 py-1.5 rounded-lg border hover:bg-destructive/10 transition-colors"
          @click="clearLetter"
        >
          <Icon icon="lucide:trash" class="h-3.5 w-3.5" />
          <span>Clear Editor</span>
        </button>

        <ShimmerButton
          :disabled="isGenerating"
          class="px-5 py-2 text-xs font-semibold shadow-sm"
          @click="generateLetter"
        >
          <div class="flex items-center gap-2">
            <LoadingSpinner v-if="isGenerating" size="sm" />
            <Icon v-else icon="lucide:sparkles" class="h-4 w-4" />
            <span>Generate Letter</span>
          </div>
        </ShimmerButton>
      </div>
    </div>

    <!-- 2-Column Responsive Workspace Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- LEFT SECTION: Input & Configuration (5 cols) -->
      <div class="lg:col-span-5 space-y-4">
        <!-- Tab Navigation Buttons -->
        <div class="flex flex-wrap rounded-xl border border-border bg-muted/40 p-1 text-xs font-medium">
          <button
            :class="[
              'flex-1 min-w-[70px] rounded-lg py-2 px-2.5 text-center transition-all',
              activeTab === 'resume'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            ]"
            @click="activeTab = 'resume'"
          >
            Resume
          </button>

          <button
            :class="[
              'flex-1 min-w-[70px] rounded-lg py-2 px-2.5 text-center transition-all',
              activeTab === 'job'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            ]"
            @click="activeTab = 'job'"
          >
            Job Info
          </button>

          <button
            :class="[
              'flex-1 min-w-[70px] rounded-lg py-2 px-2.5 text-center transition-all',
              activeTab === 'personal'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            ]"
            @click="activeTab = 'personal'"
          >
            Personal
          </button>

          <button
            :class="[
              'flex-1 min-w-[70px] rounded-lg py-2 px-2.5 text-center transition-all',
              activeTab === 'professional'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            ]"
            @click="activeTab = 'professional'"
          >
            Skills & Work
          </button>

          <button
            :class="[
              'flex-1 min-w-[70px] rounded-lg py-2 px-2.5 text-center transition-all',
              activeTab === 'style'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            ]"
            @click="activeTab = 'style'"
          >
            Style
          </button>
        </div>

        <!-- TAB CONTENT: RESUME UPLOAD -->
        <div v-show="activeTab === 'resume'" class="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
          <div>
            <h3 class="text-sm font-semibold text-foreground">Fast-Track with Resume Upload</h3>
            <p class="text-xs text-muted-foreground mt-0.5">
              PyMuPDF and python-docx extract your skills, past experience, and projects directly into this form.
            </p>
          </div>

          <ResumeUploader
            @parsed="handleResumeParsed"
            @cleared="() => info('Resume removed')"
          />
        </div>

        <!-- TAB CONTENT: JOB SPECIFICATION -->
        <div v-show="activeTab === 'job'" class="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
          <div>
            <h3 class="text-sm font-semibold text-foreground">Target Opportunity</h3>
            <p class="text-xs text-muted-foreground mt-0.5">
              Specify the position and paste the job description so the AI targets relevant requirements.
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-foreground">Job Title *</label>
              <input
                v-model="jobInfo.job_title"
                type="text"
                placeholder="e.g. Senior Full Stack Engineer"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-foreground">Company Name *</label>
              <input
                v-model="jobInfo.company_name"
                type="text"
                placeholder="e.g. Stripe, Acme Corp"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-foreground">Hiring Manager / Team (Optional)</label>
              <input
                v-model="jobInfo.hiring_manager_name"
                type="text"
                placeholder="e.g. Engineering Hiring Team"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-foreground">Application Type</label>
              <select
                v-model="jobInfo.application_type"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="Full-time">Full-time</option>
                <option value="Internship">Internship</option>
                <option value="Graduate role">Graduate / Fresher Role</option>
                <option value="Contract">Contract / Freelance</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground">Company Location (Optional)</label>
            <input
              v-model="jobInfo.company_location"
              type="text"
              placeholder="e.g. San Francisco, CA or Remote"
              class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs font-semibold text-foreground">Job Description / Requirements *</label>
              <router-link
                to="/analyzer"
                class="text-[11px] text-primary hover:underline flex items-center gap-1"
              >
                <span>Job Analyzer</span>
                <Icon icon="lucide:external-link" class="h-3 w-3" />
              </router-link>
            </div>
            <textarea
              v-model="jobInfo.job_description"
              rows="6"
              placeholder="Paste the job requirements, responsibilities, and qualifications..."
              class="w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>
        </div>

        <!-- TAB CONTENT: PERSONAL INFO -->
        <div v-show="activeTab === 'personal'" class="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
          <div>
            <h3 class="text-sm font-semibold text-foreground">Personal & Contact Info</h3>
            <p class="text-xs text-muted-foreground mt-0.5">
              These details format the header of your letter and official PDF/DOCX downloads.
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-foreground">Full Name *</label>
              <input
                v-model="personalInfo.full_name"
                type="text"
                placeholder="e.g. Jordan Miller"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-foreground">Email Address *</label>
              <input
                v-model="personalInfo.email"
                type="email"
                placeholder="e.g. jordan.miller@example.com"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-foreground">Phone Number</label>
              <input
                v-model="personalInfo.phone"
                type="text"
                placeholder="e.g. (555) 123-4567"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-foreground">Location</label>
              <input
                v-model="personalInfo.location"
                type="text"
                placeholder="e.g. New York, NY"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          <div class="space-y-3 pt-2 border-t">
            <span class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Online Presence</span>

            <div>
              <label class="text-xs font-medium text-foreground">LinkedIn URL</label>
              <input
                v-model="personalInfo.linkedin_url"
                type="url"
                placeholder="https://linkedin.com/in/username"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-medium text-foreground">GitHub URL</label>
                <input
                  v-model="personalInfo.github_url"
                  type="url"
                  placeholder="https://github.com/username"
                  class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div>
                <label class="text-xs font-medium text-foreground">Portfolio Website</label>
                <input
                  v-model="personalInfo.portfolio_url"
                  type="url"
                  placeholder="https://portfolio.dev"
                  class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- TAB CONTENT: PROFESSIONAL & SKILLS -->
        <div v-show="activeTab === 'professional'" class="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
          <div>
            <h3 class="text-sm font-semibold text-foreground">Factual Qualifications</h3>
            <p class="text-xs text-muted-foreground mt-0.5">
              Strict principle: The AI will strictly reference these facts and never invent unearned experience.
            </p>
          </div>

          <!-- Technical Skills Tag Box -->
          <div>
            <label class="text-xs font-semibold text-foreground">Technical Skills</label>
            <div class="flex items-center gap-2 mt-1">
              <input
                v-model="newSkillInput"
                type="text"
                placeholder="Add a skill (e.g. Python, Docker, Vue 3) and press Enter"
                class="flex-1 rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                @keydown.enter.prevent="addSkill"
              />
              <button
                class="px-3 py-2 text-xs rounded-xl bg-secondary text-foreground hover:bg-secondary/80 font-medium"
                @click="addSkill"
              >
                Add
              </button>
            </div>

            <!-- Skills List Chips -->
            <div class="mt-2.5 flex flex-wrap gap-1.5 min-h-[30px] p-2 rounded-xl bg-muted/30 border border-border/60">
              <span
                v-for="s in professionalInfo.technical_skills"
                :key="s"
                class="inline-flex items-center gap-1 text-[11px] rounded-full bg-primary/10 text-primary px-2.5 py-0.5 font-medium"
              >
                {{ s }}
                <button
                  class="hover:text-destructive p-0.5"
                  @click="removeSkill(s)"
                >
                  <Icon icon="lucide:x" class="h-3 w-3" />
                </button>
              </span>
              <span
                v-if="professionalInfo.technical_skills.length === 0"
                class="text-xs text-muted-foreground italic"
              >
                No skills entered yet. Type above or parse a resume.
              </span>
            </div>
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground">Key Projects (High leverage for graduates & devs)</label>
            <textarea
              v-model="professionalInfo.projects"
              rows="3"
              placeholder="e.g. Full-Stack E-commerce API: Built in FastAPI & Vue 3 with Docker and Stripe integrations..."
              class="mt-1 w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>

          <div>
            <label class="text-xs font-semibold text-foreground">Work History / Relevant Experience</label>
            <textarea
              v-model="professionalInfo.relevant_experience"
              rows="3"
              placeholder="e.g. Software Engineer Intern at Acme Labs (Summer 2024)... (Leave empty if fresher)"
              class="mt-1 w-full rounded-xl border border-input bg-background p-3 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold text-foreground">Education</label>
              <input
                v-model="professionalInfo.education"
                type="text"
                placeholder="e.g. B.S. in Computer Science, 2024"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div>
              <label class="text-xs font-semibold text-foreground">Certifications / Honors</label>
              <input
                v-model="professionalInfo.certifications"
                type="text"
                placeholder="e.g. AWS Certified Developer"
                class="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>
        </div>

        <!-- TAB CONTENT: WRITING STYLE -->
        <div v-show="activeTab === 'style'" class="rounded-2xl border border-border bg-card p-5 space-y-3 shadow-sm">
          <div>
            <h3 class="text-sm font-semibold text-foreground">Writing Tone & Persona</h3>
            <p class="text-xs text-muted-foreground mt-0.5">
              Select the voice calibrated to your seniority and target company culture.
            </p>
          </div>

          <div class="grid grid-cols-1 gap-2 pt-1">
            <div
              v-for="st in writingStyles"
              :key="st.name"
              :class="[
                'flex items-center gap-3 rounded-xl border p-3 cursor-pointer transition-all',
                selectedStyle === st.name
                  ? 'border-primary bg-primary/5 ring-1 ring-primary'
                  : 'border-border bg-card hover:bg-muted/30'
              ]"
              @click="selectedStyle = st.name"
            >
              <div
                :class="[
                  'flex h-8 w-8 items-center justify-center rounded-lg text-sm shrink-0',
                  selectedStyle === st.name ? 'bg-primary text-white' : 'bg-secondary text-muted-foreground'
                ]"
              >
                <Icon :icon="st.icon" class="h-4 w-4" />
              </div>
              <div class="flex-1">
                <div class="text-xs font-bold text-foreground">{{ st.name }}</div>
                <div class="text-[11px] text-muted-foreground">{{ st.description }}</div>
              </div>
              <Icon
                v-if="selectedStyle === st.name"
                icon="lucide:check-circle-2"
                class="h-4 w-4 text-primary shrink-0"
              />
            </div>
          </div>
        </div>

        <!-- Generate Action Button -->
        <div class="pt-2">
          <ShimmerButton
            :disabled="isGenerating"
            class="w-full py-3.5 text-sm font-semibold shadow-md"
            @click="generateLetter"
          >
            <div class="flex items-center justify-center gap-2">
              <LoadingSpinner v-if="isGenerating" size="sm" />
              <Icon v-else icon="lucide:sparkles" class="h-4 w-4" />
              <span>Generate Tailored Cover Letter</span>
            </div>
          </ShimmerButton>
        </div>
      </div>

      <!-- RIGHT SECTION: Live Document Preview & Editor (7 cols) -->
      <div class="lg:col-span-7">
        <LiveDocumentEditor
          :cover-letter="currentCoverLetter"
          :personal-info="personalInfo"
          :job-info="jobInfo"
          :template-id="activeTemplateId"
          :is-generating="isGenerating"
          @update:cover-letter="(val) => currentCoverLetter = val"
          @open-templates="isTemplateModalOpen = true"
          @open-quality="openQualityModal"
          @save-draft="handleSaveDraft"
          @regenerate="generateLetter"
        />
      </div>
    </div>

    <!-- Modals -->
    <QualityCheckerModal
      :is-open="isQualityModalOpen"
      :is-loading="isQualityLoading"
      :report="qualityReport"
      @close="isQualityModalOpen = false"
      @apply-correction="handleApplyCorrection"
    />

    <TemplateSelectorModal
      :is-open="isTemplateModalOpen"
      :active-template-id="activeTemplateId"
      @close="isTemplateModalOpen = false"
      @select="(id) => { activeTemplateId = id; success(`Switched to ${id} template layout.`); }"
    />
  </div>
</template>
