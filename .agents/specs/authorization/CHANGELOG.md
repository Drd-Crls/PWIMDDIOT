# CHANGELOG.md - Authorization & Role-Based Access Control

## Version History

### v0.1 - Infrastructure Only (2026-04-23)

**Status**: 🟡 Planning Phase

**Current State**:
- ✅ Role enum defined (ADMIN, USER)
- ✅ Role claim in JWT tokens
- ✅ User.role persisted in database
- ❌ No authorization checks on routes
- ❌ No admin-only endpoints

**What Exists**:
- `User.role: Enum(Role)` in model
- `Token payload: {"sub": user_id, "role": role_value}`
- Role available in `current_user.role` after token validation

**Known Decisions Needed**:
1. **Scope**: Which endpoints should require ADMIN?
2. **Implementation**: Decorator vs Middleware vs OpenAPI Security?
3. **Permissions Model**: Stay with ADMIN/USER or evolve to granular permissions?
4. **Error Handling**: Generic 403 or detailed permission messages?

**Next Steps**:
1. Define admin-only endpoints list
2. Choose authorization implementation pattern
3. Create `ForbiddenError` exception (if not exists)
4. Implement authorization decorator/middleware
5. Update routes with role requirements
6. Implement tests

**Future Enhancements**:
1. Granular permissions (not just ADMIN/USER)
2. Permission hierarchy
3. User groups with shared permissions
4. Permission audit trail
5. Dynamic permission assignment (not hardcoded)

---

**Last Updated**: 2026-04-23
