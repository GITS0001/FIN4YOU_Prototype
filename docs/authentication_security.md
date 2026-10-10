# Authentication and Security Architecture

## 1. Overview
FIN4YOU implements a robust authentication and authorization flow designed to protect sensitive financial data. The architecture strictly isolates user data across all APIs and mandates OTP verification before granting any access.

## 2. Authentication Flow
1. **Registration**: A user signs up with their email and password. A secure OTP is generated and sent to the user (mocked in the prototype). The account is created in an unverified state (`is_verified = False`).
2. **OTP Verification**: The user must submit the OTP to verify their account. Upon successful verification, the account's `is_verified` flag is set to `True`, and a JWT access token is issued.
3. **Login**: Users log in with their email and password. If the credentials are correct, the system checks the `is_verified` status. Unverified accounts are blocked from receiving a JWT.
4. **Token Usage**: The JWT is passed as a Bearer token in the `Authorization` header for all subsequent API requests.

## 3. Data Isolation and Scoping
- **`get_current_user` Dependency**: All protected endpoints rely on the `get_current_user` dependency, which:
  - Validates the JWT signature and expiration.
  - Retrieves the user from the database based on the token payload.
  - Enforces the `is_verified` check, rejecting access if the account is unverified (403 Forbidden).
- **Strict User Scoping**:
  - APIs **never** trust user IDs provided by the frontend.
  - All database queries and core engines (e.g., Financial Intelligence, Decision Engine, Copilot) are scoped strictly using the `id` of the authenticated user retrieved from `get_current_user`.
  - For example, the `CopilotOrchestrator` relies exclusively on the injected `current_user.id`, ensuring users cannot access another user's financial profile or transactions.

## 4. Security Principles Enforced
- **Zero Trust**: Client-provided identifiers are ignored for authorization purposes.
- **Deterministic Validation**: The system does not rely on ML or probabilistic models for data access control. Access rules are deterministic and hardcoded.
- **Secure Password Storage**: Passwords and OTPs are hashed using bcrypt before storage. Plain-text passwords and OTPs are never stored or logged.
- **Stateless Authorization**: JWTs ensure stateless and scalable verification of access rights across the application.
