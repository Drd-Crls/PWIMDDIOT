# CHANGELOG.md - User Authentication (Login)

## Version History

### v1.0 - Initial Implementation (2026-04-23)

**Status**: ✅ Shipped

**Features Implemented**:
- POST `/auth/login` endpoint
- JWT token generation with HS256
- Password verification via bcrypt
- Token claims: `sub` (user_id), `role` (role enum value)
- Pydantic validation for request
- 401 response for invalid credentials
- Clean architecture (route → controller → service → repository)

**Technical Decisions**:
1. **JWT Algorithm**: HS256 (symmetric, suitable for monolithic arch)
   - Future: Consider RS256 if microservices scale
2. **Token Claims**: Minimal (`sub`, `role`) - stateless JWT
   - Rationale: No database lookup needed on each request verification
3. **Error Message**: Generic "Invalid email or password"
   - Rationale: Security best practice (no user enumeration)
4. **Password Hashing**: bcrypt with passlib
   - Rationale: Industry-standard, automatic salt handling, configurable cost factor

**Dependencies Added**:
- `python-jose[cryptography]` - JWT signing/verification
- `passlib[bcrypt]` - password hashing
- `dependency-injector` - DI container

**Files Created**:
- `routes/auth.py` - endpoint definitions
- `controllers/auth_controller.py` - orchestration
- `services/auth_service.py` - business logic
- `services/token_service.py` - JWT operations
- `repositories/user_repository.py` - data access

**Known Limitations**:
- [ ] No token refresh mechanism (fixed 30-min expiry)
- [ ] No logout endpoint (tokens not invalidated server-side)
- [ ] No rate limiting on login attempts
- [ ] No audit logging of login events
- [ ] No support for password reset workflow

**Future Enhancements**:
1. Token refresh mechanism (refresh token rotation)
2. Login audit trail (successful/failed attempts)
3. Rate limiting (e.g., max 5 attempts per 15 min)
4. Password reset flow (email-based token)
5. Two-factor authentication
6. OAuth2 third-party login

**Code Review Notes**:
- Security: ✅ No timing attack vulnerabilities
- Performance: ⏳ Monitor bcrypt timing in production (typically 100-200ms)
- Testing: ⏳ Automated tests not yet written
- Documentation: ✅ SPEC.md and TEST_CASES.md created

---

**Last Updated**: 2026-04-23
