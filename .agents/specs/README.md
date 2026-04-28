# Specs Index

> **Spec-Driven Development** - Feature specifications guide implementation, review, and quality assurance.

## Status Overview

| Feature | Status | Spec File | Notes |
|---------|--------|-----------|-------|
| Authentication (Login/JWT) | ✅ Implemented | [auth](./auth/) | Needs retroactive spec |
| User Registration | ✅ Implemented | [user-registration](./user-registration/) | Needs retroactive spec |
| Get Current User Info | ✅ Implemented | [user-info](./user-info/) | Needs retroactive spec |
| Authorization (Role-based) | 🟡 Partial | [authorization](./authorization/) | Infrastructure in place, no routes using it yet |
| Contexts (IoT grouping) | ✅ Implemented | [contexts](./contexts/) | Added feature on 2026-04-28 |

## Spec Structure

Each feature gets a folder with:

```
{feature}/
├── SPEC.md          # Feature specification (requirements, behavior, API contract)
├── TEST_CASES.md    # Manual & automated test scenarios
└── CHANGELOG.md     # Implementation milestones & decisions
```

## Next Steps

1. **Retroactive Specs** - Create specs for the 3 implemented features
2. **New Features** - Use SDD before implementation (spec → tests → code)
3. **Breaking Changes** - Update specs before changing behavior

## SDD Workflow

**Before coding**:
```
1. Create {feature}/SPEC.md (requirements & API contract)
2. Create {feature}/TEST_CASES.md (acceptance criteria)
3. Get approval
4. Implement
5. Update TEST_CASES.md with results
```

**For changes to existing features**:
```
1. Update relevant SPEC.md
2. Update TEST_CASES.md
3. Implement
4. Add decision to CHANGELOG.md
```

---

**Last Updated**: 2026-04-23
