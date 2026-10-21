import {
  AVAILABLE_ROLES,
  COMMON_CATEGORIES,
  ROLE_SKILL_GAP_CONFIGS,
  getRoleSkillGapData,
  getCanonicalRoleName
} from '../Frontend/src/data/skillGapData.js';

console.log("=== 1. VERIFYING AVAILABLE ROLES ===");
console.log("Available Roles Count:", AVAILABLE_ROLES.length);
console.log("Roles:", AVAILABLE_ROLES);
if (AVAILABLE_ROLES.length < 8) throw new Error("Expected at least 8 canonical roles");

console.log("\n=== 2. VERIFYING ROLE-SPECIFIC VS COMMON SCOPE IN CONFIGS ===");
for (const role of AVAILABLE_ROLES) {
  const data = getRoleSkillGapData(role);
  const roleCategories = data.categoryCoverage.filter(c => c.scope === "role");
  const commonCategories = data.categoryCoverage.filter(c => c.scope === "common");

  console.log(`\nRole: ${role}`);
  console.log(`  - Overall Coverage: ${data.overallCoverage}%`);
  console.log(`  - Role-Specific Categories (${roleCategories.length}):`, roleCategories.map(c => `${c.category} (${c.coverage}% / Target ${c.benchmarkTarget}%)`));
  console.log(`  - Common Core Categories (${commonCategories.length}):`, commonCategories.map(c => `${c.category} (${c.coverage}% / Target ${c.benchmarkTarget}%)`));
  console.log(`  - Total Gaps (${data.gaps.length}): Role=${data.gaps.filter(g => g.scope === "role").length}, Common=${data.gaps.filter(g => g.scope === "common").length}`);

  if (roleCategories.length === 0) throw new Error(`Role ${role} missing role-specific categories`);
  if (commonCategories.length === 0) throw new Error(`Role ${role} missing common core categories`);
}

console.log("\n=== 3. VERIFYING CATEGORY SCOPE DIVERSITY ===");
const aiml = getRoleSkillGapData("AI/ML Engineer");
const backend = getRoleSkillGapData("Backend Developer");
const frontend = getRoleSkillGapData("Frontend Developer");

console.log("AI/ML Role Categories:", aiml.categoryCoverage.filter(c => c.scope === 'role').map(c => c.category));
console.log("Backend Role Categories:", backend.categoryCoverage.filter(c => c.scope === 'role').map(c => c.category));
console.log("Frontend Role Categories:", frontend.categoryCoverage.filter(c => c.scope === 'role').map(c => c.category));
console.log("Common Core Categories:", aiml.categoryCoverage.filter(c => c.scope === 'common').map(c => c.category));

console.log("\n>>> ALL CHECKS PASSED PERFECTLY! <<<");
