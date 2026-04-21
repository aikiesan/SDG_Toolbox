# SDG Assessment Tool - Testing Guide

This document provides comprehensive testing procedures for the SDG Assessment Tool, covering functional testing, security validation, and performance checks.

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Testing Checklist](#pre-deployment-testing-checklist)
3. [Critical Feature Tests](#critical-feature-tests)
4. [Security Testing](#security-testing)
5. [Performance Testing](#performance-testing)
6. [Browser Compatibility](#browser-compatibility)
7. [Automated Testing](#automated-testing)
8. [Regression Testing](#regression-testing)

---

## Overview

### Testing Levels

1. **Unit Tests**: Test individual functions/methods (automated)
2. **Integration Tests**: Test component interactions (automated)
3. **Functional Tests**: Test user-facing features (manual + automated)
4. **Security Tests**: Validate security measures (manual)
5. **Performance Tests**: Check speed and resource usage (manual)
6. **Acceptance Tests**: End-to-end user workflows (manual)

### Testing Environments

- **Development**: Local Docker environment (`docker-compose.yml`)
- **Staging**: Production-like environment (`docker-compose.prod.yml` on test VPS)
- **Production**: Live VPS deployment

---

## Pre-Deployment Testing Checklist

### Before Every Production Deployment

Run this checklist to ensure quality:

- [ ] All automated tests pass (`pytest`)
- [ ] Critical user flows tested manually (see below)
- [ ] No JavaScript console errors
- [ ] Mobile responsive design verified
- [ ] Security headers present (see Security Testing)
- [ ] Performance acceptable (page load < 3s)
- [ ] Database migrations run successfully
- [ ] Backup created before deployment
- [ ] Rollback plan documented

---

## Critical Feature Tests

### 1. Navigation Validation (CRITICAL)

**Test Case**: Questionnaire navigation enforces field validation

**Steps**:

1. Navigate to `/projects` and create a new project
2. Click "Start Standard Assessment"
3. On Section 1, **leave all fields blank**
4. Click the **"Next" button**

**Expected Results**:
- ❌ Navigation is blocked
- ❌ Red validation error appears: "Please select one option"
- ❌ Browser console shows **no errors** about "FormValidation object not found"
- ❌ User remains on Section 1

5. **Fill all required fields** in Section 1
6. Click "Next"

**Expected Results**:
- ✅ Navigate to Section 2
- ✅ Progress bar updates to 2/7
- ✅ No console errors

**Why This Is Critical**: Previous bug allowed users to bypass validation if external script didn't load, resulting in incomplete assessments.

---

### 2. User Registration & Authentication

**Test Case**: New user can register and login

**Steps**:

1. Navigate to `/auth/register`
2. Enter valid registration details:
   - Username: `testuser123`
   - Email: `testuser123@example.com`
   - Password: `SecurePass123!`
   - Confirm Password: `SecurePass123!`
3. Click "Register"

**Expected Results**:
- ✅ Redirect to login page or dashboard
- ✅ Flash message: "Registration successful"
- ✅ User receives welcome email (check logs or inbox)

4. Logout (if auto-logged in)
5. Navigate to `/auth/login`
6. Enter credentials
7. Click "Login"

**Expected Results**:
- ✅ Redirect to dashboard
- ✅ Username displayed in navbar
- ✅ Access to "My Projects"

**Test Invalid Inputs**:

- Existing email → "Email already registered"
- Weak password → "Password must be at least 8 characters"
- Mismatched passwords → "Passwords must match"

---

### 3. Project Creation & Management

**Test Case**: User can create, view, edit, and delete projects

**Steps**:

1. Login as registered user
2. Navigate to `/projects`
3. Click "New Project"
4. Fill form:
   - Name: `Test Residential Building`
   - Location: `Barcelona, Spain`
   - Size: `5000` sqm
   - Type: `Residential`
   - Description: `Test project for validation`
5. Click "Create Project"

**Expected Results**:
- ✅ Redirect to project detail page
- ✅ Flash message: "Project created successfully"
- ✅ Project appears in "My Projects" list

6. Click "Edit Project"
7. Change name to `Updated Residential Building`
8. Save changes

**Expected Results**:
- ✅ Project name updated
- ✅ Flash message: "Project updated successfully"

9. Click "Delete Project"
10. Confirm deletion

**Expected Results**:
- ✅ Project removed from list
- ✅ Redirect to `/projects`

---

### 4. Assessment Workflow (Standard)

**Test Case**: Complete standard assessment from start to finish

**Steps**:

1. Create a new project
2. Click "Start Standard Assessment"
3. **Section 1 (Project Scope)**:
   - Answer all questions (select radio/checkbox options)
   - Click "Next"
4. **Section 2 (Environmental Impact)**:
   - Answer all questions
   - Click "Save Progress" (test auto-save)
   - Click "Next"
5. **Sections 3-6**: Complete all sections
6. **Section 7 (Transformation)**:
   - Complete final questions
   - Click "Submit Assessment"

**Expected Results**:
- ✅ Redirect to `/assessments/projects/{id}/results/{assessment_id}`
- ✅ Results page displays:
   - Overall sustainability score
   - SDG breakdown chart
   - Individual section scores
   - Recommendations
- ✅ "Download PDF" button works (if implemented)

**Test Auto-Save**:

7. Go back to assessment (browser back button)
8. Navigate to different section

**Expected Results**:
- ✅ Previously entered answers are still selected
- ✅ Progress is restored

---

### 5. Assessment Workflow (Expert)

**Test Case**: Complete expert assessment with weighted scoring

**Steps**:

1. Create a new project
2. Click "Start Expert Assessment"
3. Complete all sections with varied answers
4. Submit assessment

**Expected Results**:
- ✅ Results page shows expert-level scoring
- ✅ More detailed analysis than standard assessment
- ✅ Expert recommendations displayed

---

### 6. Dashboard & Analytics

**Test Case**: Dashboard displays correct project statistics

**Steps**:

1. Create 3 projects with different types (Residential, Commercial, Mixed-Use)
2. Complete assessments for 2 projects
3. Navigate to `/dashboard`

**Expected Results**:
- ✅ Total projects count: 3
- ✅ Completed assessments count: 2
- ✅ Average score calculated correctly
- ✅ SDG breakdown chart displays
- ✅ Recent projects list shows latest 5

---

### 7. Email Notifications

**Test Case**: Email notifications are sent correctly

**Steps**:

1. Register new user
2. Complete an assessment

**Expected Results** (check email or logs):
- ✅ Welcome email sent on registration
- ✅ Assessment completion email sent with summary

**Check Email Content**:
- ✅ Correct recipient address
- ✅ Links work (absolute URLs, not relative)
- ✅ Proper formatting (HTML + plain text fallback)

---

### 8. Visual Identity Consistency

**Test Case**: UIA branding is consistent across all pages

**Steps**:

1. Open browser DevTools (F12)
2. Navigate to various pages (landing, login, dashboard, assessment)
3. Inspect elements with UIA colors

**Expected Results**:
- ✅ All UIA red elements use `#AF201C` (not `#e30613`)
- ✅ Progress bars use official UIA red
- ✅ Buttons use UIA red for primary actions
- ✅ Headers and footers use consistent black (`#000`)
- ✅ Typography is "Karla" font family

**DevTools Check**:

```javascript
// In browser console
getComputedStyle(document.querySelector('.progress-bar')).backgroundColor
// Should return: rgb(175, 32, 28) which is #AF201C
```

---

## Security Testing

### 1. Authentication & Authorization

**Test Case**: Unauthenticated users cannot access protected pages

**Steps**:

1. **Logout** if logged in
2. Try to access:
   - `/projects` (should redirect to login)
   - `/dashboard` (should redirect to login)
   - `/projects/1/edit` (should redirect to login or 403)

**Expected Results**:
- ❌ Access denied
- ✅ Redirect to `/auth/login`
- ✅ Flash message: "Please log in to access this page"

---

### 2. CSRF Protection

**Test Case**: Forms include CSRF tokens

**Steps**:

1. Open any form (login, register, project creation)
2. View page source (Ctrl+U)
3. Search for `csrf_token`

**Expected Results**:
- ✅ Hidden input field with name `csrf_token` exists
- ✅ Token value is non-empty and unique per session

**Test CSRF Validation**:

4. Open browser DevTools → Network tab
5. Submit form and inspect POST request

**Expected Results**:
- ✅ `X-CSRFToken` header present in AJAX requests
- ✅ `csrf_token` field in form POST data

---

### 3. SQL Injection Prevention

**Test Case**: Input fields sanitized against SQL injection

**Steps**:

1. Try SQL injection in login form:
   - Username: `admin' OR '1'='1`
   - Password: `anything`
2. Try in project search: `test'; DROP TABLE projects;--`

**Expected Results**:
- ❌ Injection fails (no authentication bypass)
- ❌ No database error messages shown to user
- ✅ Input treated as literal string

---

### 4. XSS Prevention

**Test Case**: User input is escaped to prevent XSS

**Steps**:

1. Create project with malicious name:
   - Name: `<script>alert('XSS')</script>`
2. View project list

**Expected Results**:
- ❌ No JavaScript alert popup
- ✅ Script tags displayed as text (escaped)

**Check HTML Source**:
```html
<!-- Should be escaped as: -->
&lt;script&gt;alert('XSS')&lt;/script&gt;
```

---

### 5. Security Headers (Production Only)

**Test Case**: Security headers are present in HTTP responses

**Steps** (on production/staging):

```bash
curl -I https://yourdomain.com
```

**Expected Headers**:

```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains  # HTTPS only
```

**DevTools Check**:

1. Open DevTools → Network tab
2. Refresh page
3. Click on main document request
4. Check "Response Headers"

---

### 6. Password Security

**Test Case**: Passwords are hashed and validated

**Steps**:

1. Register new user with password `Test1234!`
2. Access database:

```bash
docker-compose exec db psql -U sdg_user -d sdg_assessment
SELECT username, password_hash FROM users WHERE username = 'testuser';
```

**Expected Results**:
- ✅ Password is hashed (starts with `pbkdf2:sha256:` or similar)
- ❌ Plain text password NOT stored

3. Try weak passwords:
   - `123` → Rejected (too short)
   - `password` → Rejected (too common)

---

## Performance Testing

### 1. Page Load Speed

**Test Case**: Pages load within acceptable timeframe

**Steps**:

1. Open DevTools → Network tab
2. **Disable cache** (checkbox in Network tab)
3. Navigate to each major page
4. Check "Load" time at bottom of Network tab

**Expected Results**:
- ✅ Landing page: < 2 seconds
- ✅ Dashboard: < 3 seconds
- ✅ Assessment form: < 3 seconds
- ✅ Results page: < 4 seconds (chart rendering)

**Lighthouse Test** (Chrome DevTools):

1. DevTools → Lighthouse tab
2. Select "Performance" + "Desktop"
3. Click "Analyze page load"

**Expected Scores**:
- Performance: > 70
- Accessibility: > 90
- Best Practices: > 80
- SEO: > 80

---

### 2. Database Query Performance

**Test Case**: No N+1 query problems

**Steps** (with Flask-SQLAlchemy logging enabled):

1. Check logs while loading project list with 10+ projects
2. Count number of database queries

**Expected Results**:
- ✅ Project list: 1-2 queries (not N queries for N projects)
- ✅ Dashboard: < 10 queries total
- ✅ Results page: < 15 queries

**Enable Query Logging** (in development):

```python
# In app/__init__.py
app.config['SQLALCHEMY_ECHO'] = True
```

---

### 3. Resource Usage (Production)

**Test Case**: Application fits within VPS-1 resources

**Steps** (on production VPS):

```bash
# Check Docker resource usage
docker stats

# Check system resources
free -h
df -h
```

**Expected Results** (VPS-1: 2 vCPU, 4GB RAM):
- ✅ Gunicorn (web): < 1GB RAM
- ✅ PostgreSQL (db): < 800MB RAM
- ✅ Nginx: < 50MB RAM
- ✅ Total usage: < 2.5GB RAM (leaves 1.5GB headroom)
- ✅ CPU usage: < 50% during normal operation

---

### 4. Concurrent Users

**Test Case**: System handles expected concurrent load

**Steps** (using Apache Bench or similar):

```bash
# Install ab (Apache Bench)
apt install apache2-utils

# Test 100 requests, 10 concurrent
ab -n 100 -c 10 http://your-domain.com/

# Test authenticated page (with cookie)
ab -n 100 -c 10 -C "session=your_session_cookie" http://your-domain.com/projects
```

**Expected Results** (VPS-1):
- ✅ Handle 50-100 concurrent users without errors
- ✅ Response times < 1 second for most requests
- ✅ No 500 errors under normal load

---

## Browser Compatibility

### Supported Browsers

Test on the following browsers:

- ✅ **Chrome** (latest 2 versions)
- ✅ **Firefox** (latest 2 versions)
- ✅ **Safari** (latest 2 versions) - macOS/iOS
- ✅ **Edge** (latest 2 versions)

### Test Matrix

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Registration | ✅ | ✅ | ✅ | ✅ |
| Login | ✅ | ✅ | ✅ | ✅ |
| Assessment Form | ✅ | ✅ | ✅ | ✅ |
| Form Validation | ✅ | ✅ | ✅ | ✅ |
| Charts (Chart.js) | ✅ | ✅ | ✅ | ✅ |
| Mobile Responsive | ✅ | ✅ | ✅ | ✅ |

### Mobile Testing

Test on:

- **iOS Safari** (iPhone)
- **Chrome** (Android)

**Viewport Sizes**:
- Mobile: 375x667 (iPhone SE)
- Tablet: 768x1024 (iPad)
- Desktop: 1920x1080

**Responsive Design Checks**:

1. DevTools → Toggle device toolbar (Ctrl+Shift+M)
2. Test each viewport size

**Expected Results**:
- ✅ Navigation collapses to hamburger menu on mobile
- ✅ Forms stack vertically on mobile
- ✅ Tables scroll horizontally if needed
- ✅ Buttons are thumb-sized (min 44x44px)
- ✅ Text is readable without zooming (min 16px)

---

## Automated Testing

### Running Tests

```bash
# Run all tests
docker-compose exec web pytest

# Run specific test file
docker-compose exec web pytest tests/test_auth.py

# Run with coverage report
docker-compose exec web pytest --cov=app --cov-report=html

# Run with verbose output
docker-compose exec web pytest -v

# Run only failed tests from last run
docker-compose exec web pytest --lf
```

### Writing Tests

**Example: Test User Registration**

```python
# tests/test_auth.py
def test_user_registration(client):
    """Test user can register successfully"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration successful' in response.data

    # Verify user created in database
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'
```

### Test Coverage Goals

- **Overall coverage**: > 80%
- **Critical paths** (auth, assessment): > 90%
- **Models**: 100% (test all CRUD operations)

---

## Regression Testing

### After Bug Fixes

When fixing a bug:

1. **Add regression test** that reproduces the bug
2. **Verify test fails** before fix
3. **Apply fix**
4. **Verify test passes** after fix
5. **Run full test suite** to ensure no side effects

**Example: Navigation Validation Bug**

```python
def test_assessment_validation_enforced(client, auth):
    """Regression test for navigation validation bug

    Ensures users cannot skip sections without filling required fields.
    Bug: External script loading race condition allowed bypassing validation.
    Fix: Consolidated validation function into inline script.
    """
    auth.login()

    # Create project and start assessment
    project = create_test_project(client)
    response = client.get(f'/projects/{project.id}/questionnaire/1/step/1')

    # Try to navigate without filling fields
    response = client.post(f'/projects/{project.id}/questionnaire/1/save', data={
        'section': 1,
        # Intentionally empty - no answers provided
    })

    # Should remain on section 1, not advance
    assert response.status_code == 200  # Not 302 redirect
    assert b'Please select one option' in response.data
```

---

## Testing Before Each Release

### Pre-Production Checklist

Before deploying to production:

1. **Run automated test suite**: `pytest`
2. **Manual critical path tests**: Registration → Project → Assessment → Results
3. **Security scan**: Check OWASP Top 10
4. **Performance test**: Load testing with expected concurrent users
5. **Browser compatibility**: Test on Chrome, Firefox, Safari, Edge
6. **Mobile testing**: Test on iOS and Android devices
7. **Database backup**: Create backup before deployment
8. **Smoke test production**: After deployment, test critical flows on live site

---

## Continuous Integration (Future)

### Recommended CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build containers
        run: docker-compose build
      - name: Run tests
        run: docker-compose exec -T web pytest --cov=app
      - name: Check code style
        run: docker-compose exec -T web flake8 app/
```

---

## Bug Reporting

### Bug Report Template

When reporting bugs, include:

1. **Description**: What happened vs. what should happen
2. **Steps to Reproduce**: Numbered list
3. **Expected Result**: What should happen
4. **Actual Result**: What actually happened
5. **Screenshots**: If applicable
6. **Environment**: Browser, OS, device
7. **Logs**: Console errors, server logs

**Example**:

```markdown
## Bug: Validation bypassed on assessment form

**Description**: Users can skip sections without filling required fields.

**Steps to Reproduce**:
1. Go to `/projects/1/questionnaire/1/step/1`
2. Leave all fields blank
3. Click "Next" button

**Expected**: Validation error appears, navigation blocked
**Actual**: User advances to Section 2 without validation

**Browser**: Chrome 119, Windows 11
**Console Error**: "FormValidation object or validateAssessmentSection function not found"
```

---

**Last Updated**: 2026-02-20
**Version**: 1.0
