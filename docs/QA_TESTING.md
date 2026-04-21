# SDG Assessment Tool - QA Testing Guide

## Overview

This document describes the QA testing workflow for the SDG Assessment Tool, including how to run tests in Docker, interpret coverage reports, and follow manual QA checklists.

## Quick Start

### Running All Tests

```bash
./scripts/run_qa_tests.sh
```

This command will:
1. Clean up old containers
2. Build fresh test containers
3. Start PostgreSQL and Redis test services
4. Run the complete test suite
5. Generate coverage reports
6. Display results

### Running Specific Test Types

```bash
# Unit tests only
./scripts/run_qa_tests.sh unit

# Integration tests only
./scripts/run_qa_tests.sh integration

# E2E tests only
./scripts/run_qa_tests.sh e2e

# Specific test file
./scripts/run_qa_tests.sh tests/test_projects.py
```

### Parallel Test Execution

```bash
# Run with 4 parallel workers
./scripts/run_qa_tests.sh all 4

# Run with auto-detected workers (default)
./scripts/run_qa_tests.sh all auto
```

## Prerequisites

- **Docker Desktop** must be running
- **Git Bash** (Windows) or native terminal (Mac/Linux)
- At least **4GB RAM** available for Docker
- At least **10GB disk space** for images

## Test Environment Architecture

### Services

The Docker QA environment includes:

1. **db-test** - PostgreSQL 15 database
   - Uses tmpfs (memory) for faster tests
   - Port: 5434 (localhost)
   - Credentials: test_user/test_password

2. **web-test** - Flask application with test dependencies
   - Runs pytest with coverage
   - Generates HTML, XML, and terminal reports

3. **selenium** - Chrome headless browser
   - Port 4444: Selenium Grid
   - Port 7900: VNC viewer (for debugging)

4. **redis-test** - Redis cache (optional)
   - Port: 6380 (localhost)
   - Used for caching tests

### Volumes

- `test-reports/` - Coverage and test reports (mounted from host)

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── test_models.py              # Model unit tests
├── test_auth.py                # Authentication tests
├── test_projects.py            # Project CRUD tests
├── test_dashboard.py           # Dashboard tests
├── integration/                # Integration tests
│   ├── test_assessment_workflow.py
│   └── test_scoring_flow.py
└── e2e/                        # End-to-end tests (future)
    └── test_user_registration.py
```

## Coverage Targets

### Phase 1 (Current)
- **Target**: 55-60%
- **Focus**: Critical paths, database performance, dashboard

### Phase 2 (After refactoring)
- **Target**: 70%
- **Focus**: Service layer, repositories, business logic

### Phase 3 (Comprehensive)
- **Target**: 80%+
- **Focus**: Integration tests, E2E tests, edge cases

## Viewing Reports

### HTML Coverage Report

```bash
# Open in browser (Mac)
open test-reports/htmlcov/index.html

# Open in browser (Windows)
start test-reports/htmlcov/index.html

# Open in browser (Linux)
xdg-open test-reports/htmlcov/index.html
```

### Coverage Summary in Terminal

Coverage percentages are displayed at the end of test execution:

```
----------- coverage: platform win32, python 3.10.x -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/__init__.py                      45      5    89%
app/models/project.py                89     12    87%
app/services/scoring_service.py     156     23    85%
...
-----------------------------------------------------
TOTAL                              2568    985    62%
```

### XML Coverage Report

For CI/CD integration:
- Location: `test-reports/coverage.xml`
- Format: Cobertura XML
- Use with: Jenkins, GitHub Actions, GitLab CI, etc.

## Manual QA Checklist

Use this checklist for manual testing before releases:

### User Authentication
- [ ] User can register with valid email
- [ ] User receives confirmation email
- [ ] User can confirm email
- [ ] User can login with correct credentials
- [ ] User cannot login with wrong credentials
- [ ] Password reset flow works
- [ ] User can logout

### Project Management
- [ ] User can create a new project
- [ ] User can view their projects list
- [ ] User can edit project details
- [ ] User can delete a project
- [ ] Deleting project also deletes assessments
- [ ] User cannot see other users' projects

### Assessment Workflow
- [ ] User can start a new assessment
- [ ] User can navigate through questionnaire steps
- [ ] User can save draft and resume later
- [ ] User can submit completed assessment
- [ ] Scores are calculated correctly
- [ ] Results page displays all SDG scores
- [ ] Charts render correctly
- [ ] PDF export works (if implemented)

### Admin Dashboard
- [ ] Admin can access dashboard
- [ ] Non-admin cannot access dashboard
- [ ] Statistics are accurate
- [ ] User list displays correctly
- [ ] Project list displays correctly
- [ ] Admin can edit users
- [ ] SDG management works

### Performance
- [ ] Dashboard loads in < 2 seconds
- [ ] Assessment results load in < 1 second
- [ ] No N+1 queries in SQL logs
- [ ] Caching reduces repeated query time

### Browser Compatibility
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge
- [ ] Mobile responsive (phone)
- [ ] Mobile responsive (tablet)

## Troubleshooting

### Tests Fail to Start

**Problem**: "Docker is not running"
```
Solution: Start Docker Desktop and wait for it to fully start
```

**Problem**: Port 5434 already in use
```
Solution: Stop other PostgreSQL instances or change port in docker-compose.test.yml
```

### Database Connection Errors

**Problem**: "could not connect to server"
```bash
# Check database health
docker-compose -f docker-compose.test.yml ps

# View database logs
docker-compose -f docker-compose.test.yml logs db-test

# Restart database
docker-compose -f docker-compose.test.yml restart db-test
```

### Tests Hang or Timeout

**Problem**: Tests hang indefinitely
```bash
# Stop all containers
docker-compose -f docker-compose.test.yml down -v

# Check for zombie processes
docker ps -a

# Remove all test containers
docker-compose -f docker-compose.test.yml rm -f
```

### Coverage Report Not Generated

**Problem**: No coverage report in test-reports/
```bash
# Ensure directory exists
mkdir -p test-reports/htmlcov

# Run with explicit coverage options
docker-compose -f docker-compose.test.yml run --rm web-test \
  pytest --cov=app --cov-report=html:test-reports/htmlcov

# Check file permissions
ls -la test-reports/
```

### Selenium E2E Tests Fail

**Problem**: Selenium connection refused
```bash
# Start Selenium separately
docker-compose -f docker-compose.test.yml up -d selenium

# Check Selenium status
docker-compose -f docker-compose.test.yml logs selenium

# Access VNC viewer for debugging
# Open http://localhost:7900 in browser (no password)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: QA Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run QA Tests
        run: |
          chmod +x scripts/run_qa_tests.sh
          ./scripts/run_qa_tests.sh all auto
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./test-reports/coverage.xml
          fail_ci_if_error: true
```

### GitLab CI Example

```yaml
test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - chmod +x scripts/run_qa_tests.sh
    - ./scripts/run_qa_tests.sh all auto
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: test-reports/coverage.xml
```

## Performance Benchmarks

### Before Optimization (Baseline)
- Dashboard index: ~800ms
- Assessment calculation: ~500ms
- 8 separate DB queries in dashboard
- N+1 queries in scoring service

### After Phase 1
- Dashboard index: ~250ms (uncached), ~80ms (cached)
- Assessment calculation: ~200ms
- 2-3 optimized queries in dashboard
- N+1 queries eliminated

### Target (Phase 3)
- Dashboard index: < 100ms (cached)
- Assessment calculation: < 150ms
- All queries optimized with indexes
- 80%+ test coverage

## Best Practices

### Writing Tests
1. Use fixtures from `conftest.py`
2. Test one thing per test function
3. Use descriptive test names: `test_user_can_delete_own_project`
4. Clean up in teardown (handled by fixtures)
5. Mock external services (email, APIs)

### Test Data
1. Use `test_user`, `admin_user`, `test_project` fixtures
2. Create additional data with factories
3. Don't rely on specific database state
4. Use unique identifiers (UUIDs) to avoid conflicts

### Performance
1. Run unit tests locally before integration tests
2. Use parallel execution (`-n auto`)
3. Keep E2E tests minimal (slowest)
4. Focus on critical user journeys

## Support

For issues or questions:
1. Check this documentation
2. Review test output and logs
3. Check GitHub Issues
4. Contact development team

## Appendix: Useful Commands

```bash
# Run specific test
docker-compose -f docker-compose.test.yml run --rm web-test \
  pytest tests/test_projects.py::test_create_project -v

# Run with debugging output
docker-compose -f docker-compose.test.yml run --rm web-test \
  pytest -v -s --log-cli-level=DEBUG

# Run with coverage for specific module
docker-compose -f docker-compose.test.yml run --rm web-test \
  pytest --cov=app.services tests/ -v

# Interactive shell in test container
docker-compose -f docker-compose.test.yml run --rm web-test bash

# Access test database directly
docker-compose -f docker-compose.test.yml exec db-test \
  psql -U test_user -d sdg_assessment_test

# Watch test execution in real-time
docker-compose -f docker-compose.test.yml run --rm web-test \
  pytest-watch
```
