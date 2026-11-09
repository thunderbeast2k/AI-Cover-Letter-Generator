import type { TemplateDefinition } from "@/types";

export const TEMPLATES: TemplateDefinition[] = [
  {
    id: "classic",
    name: "Classic Professional",
    badge: "Popular",
    description: "Traditional corporate alignment, elegant horizontal rule, clean typography suitable for finance, enterprise, and corporate roles.",
    suitableFor: "General corporate, enterprise, consulting, and management positions"
  },
  {
    id: "minimal",
    name: "Modern Minimal",
    badge: "Clean",
    description: "Centered header, generous whitespace, refined modern hierarchy favored by high-growth startups and tech hubs.",
    suitableFor: "Tech startups, design agencies, remote-first companies"
  },
  {
    id: "technical",
    name: "Technical Developer",
    badge: "Engineering",
    description: "Accent color divider, clean high-density layout designed specifically for software engineers, devops, and data specialists.",
    suitableFor: "Software engineers, systems architects, data scientists"
  },
  {
    id: "graduate",
    name: "Fresh Graduate",
    badge: "Early Career",
    description: "Structure calibrated to give prominence to academic milestones, capstone repositories, and foundational readiness.",
    suitableFor: "Recent college graduates, entry-level engineering applicants"
  },
  {
    id: "internship",
    name: "Internship Application",
    badge: "Students",
    description: "Concise, focused format emphasizing genuine enthusiasm, quick absorption, and practical hands-on labs.",
    suitableFor: "Summer internships, co-op programs, student apprenticeships"
  }
];
