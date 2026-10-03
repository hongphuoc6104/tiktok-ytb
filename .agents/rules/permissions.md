---
trigger: always_on
---

# Workflow authority

| Role | Autonomous work within the assigned task | Outside its authority |
|---|---|---|
| setup | Inventory, machine/account configuration, remote preset setup and login handoff | Production or changes to policy/engine |
| production | Create/continue/repair assigned old or new videos; add/edit/replace/delete job content and artifacts through workflow | System code, schemas, configuration, Rules, Skills and guides |
| development | Change project files covered by the upgrade, tests, compatibility/migration/rollback | Product goals, services/costs or accounts outside the assignment |
| maintenance | Inventory/reproducible cleanup/archive; commit/push authorized paths and branch | Delete history/evidence/secrets/pending requests or change logic |

One active role per task. Grants record scope, actual authorization source and status; chat changes do not expire them. Auto mode does not grant system-edit authority. If more authority is needed, prepare the micro-plan/diff/impact first. Do not ask again for valid existing authority.

System files include AGENTS/INDEX/README/GEMINI, Rules/Skills/operational docs, engine/renderer/scripts/schemas/lock/config and canonical mascot/voice resources. Content includes the assigned job's brief/draft/scenes/narration/images/beats/props/media and vocabulary data. Vocabulary code is system code; its assigned data is content.

DB, revision snapshots, decisions, requests, usage and grants are history: official tools update them; never forge decisions or edit state directly. Current content remains repairable with version/impact and minimum provenance. Delete reproducible temporary files only when no owner/request/evidence still depends on them.

Workers may write only assigned targets/files/sessions. Skills cannot expand authority or authorize new agents. Separate write scope, execution compatibility and history integrity; a guide change does not invalidate all artifacts.

These are operational/provenance checks, not an OS sandbox against agents with full filesystem access.
