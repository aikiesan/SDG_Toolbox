#!/bin/bash
# SDG Assessment Tool - QA Test Runner Script
# This script runs the full test suite in Docker containers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_msg "==================================" "$BLUE"
print_msg "SDG Assessment Tool - QA Testing" "$BLUE"
print_msg "==================================" "$BLUE"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_msg "ERROR: Docker is not running!" "$RED"
    print_msg "Please start Docker Desktop and try again." "$YELLOW"
    exit 1
fi

print_msg "✓ Docker is running" "$GREEN"
echo ""

# Parse command line arguments
TEST_TYPE=${1:-all}  # all, unit, integration, e2e, or specific test file
PARALLEL=${2:-auto}  # Number of parallel workers (default: auto)

# Set pytest options based on test type
case $TEST_TYPE in
    unit)
        PYTEST_ARGS="tests/ -k 'not integration and not e2e'"
        print_msg "Running: Unit Tests Only" "$BLUE"
        ;;
    integration)
        PYTEST_ARGS="tests/integration/"
        print_msg "Running: Integration Tests Only" "$BLUE"
        ;;
    e2e)
        PYTEST_ARGS="tests/e2e/"
        print_msg "Running: E2E Tests Only" "$BLUE"
        ;;
    all)
        PYTEST_ARGS="tests/"
        print_msg "Running: All Tests" "$BLUE"
        ;;
    *)
        PYTEST_ARGS="$TEST_TYPE"
        print_msg "Running: Custom Test Path ($TEST_TYPE)" "$BLUE"
        ;;
esac

# Add parallel execution if specified
if [ "$PARALLEL" != "1" ]; then
    PYTEST_ARGS="$PYTEST_ARGS -n $PARALLEL"
    print_msg "Parallel execution: $PARALLEL workers" "$BLUE"
fi

echo ""
print_msg "Step 1: Cleaning up old containers..." "$YELLOW"
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true
print_msg "✓ Cleanup complete" "$GREEN"
echo ""

print_msg "Step 2: Building test containers..." "$YELLOW"
docker-compose -f docker-compose.test.yml build web-test
if [ $? -eq 0 ]; then
    print_msg "✓ Build successful" "$GREEN"
else
    print_msg "✗ Build failed" "$RED"
    exit 1
fi
echo ""

print_msg "Step 3: Starting database and services..." "$YELLOW"
docker-compose -f docker-compose.test.yml up -d db-test redis-test
if [ $? -eq 0 ]; then
    print_msg "✓ Services started" "$GREEN"
else
    print_msg "✗ Failed to start services" "$RED"
    exit 1
fi

# Wait for database to be ready
print_msg "Waiting for database to be ready..." "$YELLOW"
sleep 5
docker-compose -f docker-compose.test.yml exec -T db-test pg_isready -U test_user -d sdg_assessment_test
if [ $? -eq 0 ]; then
    print_msg "✓ Database is ready" "$GREEN"
else
    print_msg "✗ Database not ready" "$RED"
    docker-compose -f docker-compose.test.yml logs db-test
    exit 1
fi
echo ""

# Start Selenium if running E2E tests
if [ "$TEST_TYPE" == "e2e" ] || [ "$TEST_TYPE" == "all" ]; then
    print_msg "Step 4: Starting Selenium..." "$YELLOW"
    docker-compose -f docker-compose.test.yml up -d selenium
    sleep 5
    print_msg "✓ Selenium started (VNC available at http://localhost:7900)" "$GREEN"
    echo ""
fi

print_msg "Step 5: Running tests..." "$YELLOW"
echo ""

# Run tests with coverage
docker-compose -f docker-compose.test.yml run --rm web-test \
    pytest $PYTEST_ARGS \
    --cov=app \
    --cov-report=html:/app/test-reports/htmlcov \
    --cov-report=xml:/app/test-reports/coverage.xml \
    --cov-report=term \
    --html=/app/test-reports/report.html \
    --self-contained-html \
    -v

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_msg "✓ All tests passed!" "$GREEN"
else
    print_msg "✗ Some tests failed (exit code: $TEST_EXIT_CODE)" "$RED"
fi

echo ""
print_msg "Step 6: Generating reports..." "$YELLOW"
# Coverage report location
print_msg "✓ HTML Coverage Report: test-reports/htmlcov/index.html" "$GREEN"
print_msg "✓ XML Coverage Report: test-reports/coverage.xml" "$GREEN"
print_msg "✓ HTML Test Report: test-reports/report.html" "$GREEN"
echo ""

# Display coverage summary
if [ -f "test-reports/coverage.xml" ]; then
    print_msg "Coverage Summary:" "$BLUE"
    grep -oP 'line-rate="\K[0-9.]+' test-reports/coverage.xml | head -1 | awk '{printf "  Overall Coverage: %.2f%%\n", $1 * 100}'
fi

echo ""
print_msg "Step 7: Cleanup..." "$YELLOW"

# Ask user if they want to keep containers running
read -p "Keep test containers running? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.test.yml down -v
    print_msg "✓ Containers stopped and removed" "$GREEN"
else
    print_msg "✓ Containers still running" "$YELLOW"
    print_msg "  Database: localhost:5434" "$YELLOW"
    print_msg "  Selenium VNC: http://localhost:7900" "$YELLOW"
    print_msg "  Stop with: docker-compose -f docker-compose.test.yml down -v" "$YELLOW"
fi

echo ""
print_msg "==================================" "$BLUE"
print_msg "QA Testing Complete!" "$BLUE"
print_msg "==================================" "$BLUE"

exit $TEST_EXIT_CODE
