# Security Audit – Recipe API

1. Password storage
   - Check: inspect users table.
   - Expected: no plaintext passwords.
   - Observed: scrypt:... hashes only.
   - Conclusion: safe password storage.

2. PATCH /recipes/:id
   - Anonymous: 401, "missing or invalid authorization header"
   - Fake token: 401, "invalid token"
   - Admin (userA) editing recipe 4: 200, recipe updated
   - Owner (userB) editing recipe 4: 200, recipe updated

3. DELETE /recipes/:id
   - Anonymous: 401
   - Owner (userB) deleting recipe 4: 200, "recipe deleted"

Overall: previous auth/access exploits are blocked by proper identity checks and owner/admin rules.
