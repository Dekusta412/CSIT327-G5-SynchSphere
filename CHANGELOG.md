# Changelog

All notable changes to this project are recorded in this file. This project follows a simple, chronological changelog where newer versions appear first.

Format conventions
- Version header: `Version X.Y.Z — YYYY-MM-DD` (date optional)
- Sections: Added / Changed / Fixed / Notes

---

Version 1.1.1 — 2025-10-13

Highlights
- Verified SMTP sending using environment credentials and added guidance for Gmail App Passwords.
- Added a lightweight development SSE endpoint (`/events/`) and client to receive real-time auth events (login/register/logout) while developing.
- Improved password-reset email templates (HTML and subject) and ensured the reset emails are sent from the configured `DEFAULT_FROM_EMAIL`.

Notes
- SSE implementation is in-memory and intended for development only; use Channels + Redis for production-grade real-time messaging.

---

Version 1.1.0 — 2025-10-13

Highlights
- Improved home page UX: removed the prominent "You are successfully logged in" banner; the page now shows a neutral welcome for anonymous visitors and a subtle account indicator for authenticated users.
- Logout now redirects users to the home page.
- Added full password-reset flow ("Forgot password?") including form, confirmation pages and email template.
- Email configuration now reads SMTP credentials from `.env`; defaults to console backend during development.
- Annotated release tag `v1.1.0` created and pushed.

Notes
- If you need real email delivery in production, set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD` in your `.env` and configure `DEBUG=False` (or set `EMAIL_BACKEND`).
- If your remote rejects a push because it contains unrelated commits, fetch and merge or rebase before pushing.

---

Version 1.0.0 — Initial Release

Overview
This is the project's initial public release of SynchSphere — a Django-based time synchronization and notification system designed to help teams coordinate meetings across time zones.

Added
- Project scaffolding: Django project, `env` virtual environment, and a `requirements.txt` for reproducible setup.
- Environment handling with `.env` support.
- Authentication system:
	- `accounts` app with registration and login flows.
	- Registration uses a custom `SignUpForm` (extends Django's `UserCreationForm`) and enforces unique email addresses.
	- Login uses Django's `AuthenticationForm`.
	- Secure password validation via Django's built-in validators.
- Basic UI:
	- Login and Register pages with a modern dark-themed style (Tailwind via CDN), form validation messages and custom widgets via `templatetags/form_tags.py`.
- Project layout:
	- Templates organized under `/templates/accounts/` and project-level template dir configured in `settings.py`.
- Dev tooling and VCS:
	- `.gitignore` configured to exclude `env/`, `.env`, and other local artifacts.
	- Initial push to GitHub: https://github.com/Dekusta412/CSIT327-G5-SynchSphere.git

Notes
- This release establishes the core user flows and project structure. Subsequent releases will focus on polish, security hardening, and additional features.
