# CHANGELOG.md - User Registration

## Version History

### v1.0 - Initial Implementation (2026-04-23)

**Status**: ✅ Shipped

**Features Implemented**:
- POST `/users` endpoint
- User creation with email, password, name, role
- Password hashing via bcrypt
- Email uniqueness enforced (unique constraint + index)
- UUID v4 auto-generation
- Automatic timestamp management (created_at, updated_at)
- Conflict detection (409 on duplicate email)
- Pydantic validation for request/response
- Clean architecture pattern

**Technical Decisions**:
1. **UUID Primary Key**: uuid4 over auto-increment
   - Rationale: No sequential guessing, distributed-system friendly
2. **Role Assignment on Registration**: User specifies role via request
   - ⚠️ Security issue: Should only ADMIN assign non-USER roles
   - TODO: Implement authorization check
3. **Email Validation**: Pydantic EmailStr validator
   - Rationale: RFC-compliant, prevents invalid emails
4. **Error Message on Duplicate**: Descriptive with email
   - Rationale: Helps client understand why creation failed
5. **Password Requirements**: None enforced (future enhancement)
   - Current: Any non-empty string accepted
   - TODO: Add strength requirements (length, complexity)

**Dependencies (unchanged)**:
- Uses existing stack (FastAPI, SQLAlchemy, Pydantic, bcrypt)

**Files Created/Modified**:
- `routes/enroll.py` - user creation endpoint
- `controllers/user_controller.py` - orchestration
- `services/user_service.py` - business logic
- `repositories/user_repository.py` - create() method + error handling
- `models/user.py` - email unique constraint + index
- `schemas/user.py` - UserCreateRequest + UserResponse

**Known Limitations**:
- [ ] No email verification (account active immediately)
- [ ] Anyone can create ADMIN role (authorization needed)
- [ ] No password strength requirements
- [ ] No registration confirmation/validation email
- [ ] No rate limiting on registrations
- [ ] No audit logging of account creation

**Future Enhancements**:
1. **Authorization**: Only ADMIN can assign ADMIN role
2. **Password Policy**: Enforce minimum length, complexity
3. **Email Verification**: Send confirmation link, verify before activation
4. **Rate Limiting**: Max registrations per IP/hour
5. **Audit Trail**: Log all account creation events
6. **Terms & Conditions**: Require acceptance on registration

**Code Review Notes**:
- Security: ⚠️ No authorization check on role assignment
- Security: ✅ Password hashed correctly
- Security: ⏳ No rate limiting (potential spam/DoS)
- Performance: ✅ Email index present for duplicate check
- Testing: ⏳ No automated tests yet
- Documentation: ✅ SPEC.md and TEST_CASES.md created

---

**Last Updated**: 2026-04-23
