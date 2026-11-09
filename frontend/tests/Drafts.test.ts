import { describe, it, expect, beforeEach } from "vitest";
import { useDrafts } from "../src/composables/useDrafts";

describe("useDrafts composable", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("saves, lists, and retrieves drafts in local storage", () => {
    const { saveDraft, getDrafts, getDraft } = useDrafts();

    expect(getDrafts().length).toBe(0);

    const saved = saveDraft({
      title: "Frontend Engineer at Acme",
      cover_letter: "Dear Hiring Team, I am excited to apply...",
      writing_style: "Professional",
      template_id: "classic",
      personal_info: { full_name: "Alex Vance", email: "alex@example.com" },
      job_info: { job_title: "Frontend Engineer", company_name: "Acme", job_description: "Build UIs", application_type: "Full-time" },
      professional_info: { technical_skills: ["Vue", "TypeScript"] }
    });

    expect(saved.id).toBeDefined();
    expect(getDrafts().length).toBe(1);

    const fetched = getDraft(saved.id);
    expect(fetched).toBeDefined();
    expect(fetched?.title).toBe("Frontend Engineer at Acme");
  });

  it("duplicates and renames drafts properly", () => {
    const { saveDraft, duplicateDraft, renameDraft, getDraft } = useDrafts();

    const original = saveDraft({
      title: "Original Draft",
      cover_letter: "Sample text",
      writing_style: "Concise",
      template_id: "minimal",
      personal_info: { full_name: "John", email: "john@example.com" },
      job_info: { job_title: "Dev", company_name: "Tech", job_description: "Code", application_type: "Full-time" },
      professional_info: { technical_skills: ["Python"] }
    });

    const copy = duplicateDraft(original.id);
    expect(copy).toBeDefined();
    expect(copy?.title).toBe("Original Draft (Copy)");

    renameDraft(original.id, "Renamed Draft");
    const updated = getDraft(original.id);
    expect(updated?.title).toBe("Renamed Draft");
  });

  it("deletes drafts correctly", () => {
    const { saveDraft, deleteDraft, getDrafts } = useDrafts();

    const draft = saveDraft({
      title: "Draft to Delete",
      cover_letter: "Sample",
      writing_style: "Technical",
      template_id: "technical",
      personal_info: { full_name: "Jane", email: "jane@example.com" },
      job_info: { job_title: "SRE", company_name: "Cloud", job_description: "Infra", application_type: "Full-time" },
      professional_info: { technical_skills: [] }
    });

    expect(getDrafts().length).toBe(1);
    deleteDraft(draft.id);
    expect(getDrafts().length).toBe(0);
  });
});
