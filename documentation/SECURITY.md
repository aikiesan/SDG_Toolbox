# Security Policy

**Version:** 1.0.0  
**Last Updated:** 2025-04-25

## Prerequisites
- All contributors and users should review this security policy and the related Privacy Policy before handling sensitive data.

## Data Security and Privacy
- User data is stored securely and never shared for commercial purposes.
- All data handling is designed to comply with GDPR and other relevant privacy regulations.
- Users have the right to request data deletion (right to erasure) and access their personal data.
- Passwords are hashed using industry-standard algorithms (e.g., bcrypt or Argon2).
- User authentication is required for any access to personal project data.
- Project and assessment deletion is implemented, including cascading deletion of related data.
- Data retention: User data is retained only as long as necessary for service provision or as required by law.
- Users may request a copy of their data or its deletion by contacting the maintainer (see below).

## Security Protocols
- All passwords are hashed and never stored in plain text.
- Secure authentication and session management are enforced.
- Access control: Only authenticated users can access their own projects and assessments.
- Regular backups are performed for data integrity and recovery.
- Monitoring and logging are in place for suspicious activity.
- Dependency management: All third-party libraries are regularly reviewed and updated for security.
- Incident response: Security incidents will be investigated and affected users notified promptly.
- Encryption in transit (HTTPS) is required for all production deployments.
- Encryption at rest is planned for future releases.

## Responsible Disclosure
If you discover a security vulnerability, please report it privately to the maintainer at [lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com). Do not disclose it publicly until a fix is released. We aim to acknowledge all reports within 3 business days and provide a resolution or mitigation plan within 14 days.

## Current Limitations & Planned Improvements
- Encryption at rest is planned but not yet fully implemented.
- Multilingual privacy policy and terms are planned.
- Regular security audits and updates are planned.

## Missing Security Considerations?
If you believe any security aspect is missing or unclear, or if you have specific requirements (e.g., additional compliance standards), please contact the maintainer directly.

---
**Maintained by Lucas Nakamura** ([lucassnakamura@gmail.com](mailto:lucassnakamura@gmail.com))
