# Startup Incubator System Requirements Traceability

This document converts F1-F17 into implementable database scope.

## Core assumptions

- Registration in F1 covers at least `STARTUP_REP` and `INVESTOR` users.
- Login validation and the `Invalid Credentials` message in F2-F3 are application-layer behaviors backed by `users.password_hash` and `roles`.
- Mentors and administrators are provisioned by the organization, not self-registered.
- Search in F16 is implemented at query level across indexed entity tables.

## Requirement mapping

| ID | Requirement summary | Primary tables / objects |
| --- | --- | --- |
| F1 | Register startup representatives and investors | `users`, `user_profiles`, `roles` |
| F2 | Login with role-based access | `users`, `roles`, `permissions`, `role_permissions` |
| F3 | Reject invalid login attempts | `users` plus application auth flow |
| F4 | Add startup with full details | `startups`, `startup_members` |
| F5 | Update profile, milestones, funding status, team | `startups`, `milestones`, `startup_members`, `funding_rounds` |
| F6 | Remove graduated/exited startup | `startups` or soft-delete via `incubator_status` |
| F7 | Investor browsing and filtering | `startups`, index `idx_startups_domain_stage` |
| F8 | Express interest and start pipeline | `investor_interests` |
| F9 | Manage funding rounds and MOU | `funding_rounds`, `funding_round_investors` |
| F10 | Assign mentors by expertise | `mentors`, `mentor_assignments` |
| F11 | Mentor views startups and logs guidance | `mentor_assignments`, `mentor_sessions` |
| F12 | Startup views mentor, funding, milestones | `mentor_assignments`, `funding_rounds`, `milestones` |
| F13 | Generate startup or cohort reports | `reports` |
| F14 | View activity log / audit trail | `activity_logs` |
| F15 | Investor portfolio and returns | `funding_round_investors`, `investor_portfolio_summary` |
| F16 | Search all entities | `startups`, `users`, `mentors` plus supporting indexes |
| F17 | Enforce RBAC | `roles`, `permissions`, `role_permissions` |

## Notes for implementation

- `activity_logs` should be populated by triggers or service-layer audit logging on every insert, update, and delete for regulated entities.
- `updated_at` columns should be maintained by triggers or by the application service layer.
- F6 can be implemented either as hard delete or as a controlled status change. In incubator systems, status-based archival is usually safer for audit retention.
- `investor_portfolio_summary` is a reporting view and can be extended with realized returns once exit events are modeled.
- Full text search can be added later if simple indexed filtering is not enough.
