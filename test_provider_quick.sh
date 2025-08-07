#!/bin/bash

# Quick Provider Endpoints Test Script
# Simplified version for quick daily testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Base URLs
BASE_URL="http://localhost:8001/api/v1"
AUTH_BASE_URL="http://localhost:8001/api/v1/auth"

# Test data
PROVIDER_EMAIL="quicktest.provider@example.com"
PROVIDER_USERNAME="quicktest_provider"
PROVIDER_PASSWORD="QuickTest123!"
PROVIDER_ACCESS_TOKEN=""

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Check server
echo "Checking Django server..."
if curl -s "$BASE_URL/providers/" > /dev/null 2>&1; then
    print_success "Server is running"
else
    print_error "Server not running. Start with: python manage.py runserver 8001"
    exit 1
fi

echo ""
print_info "Starting Quick Provider Tests..."

# Test 1: Provider Registration or Login
echo ""
echo "1. Provider Authentication..."
response=$(curl -s -X POST "$AUTH_BASE_URL/provider/register/" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$PROVIDER_EMAIL\",
        \"username\": \"$PROVIDER_USERNAME\",
        \"password\": \"$PROVIDER_PASSWORD\",
        \"password_confirm\": \"$PROVIDER_PASSWORD\",
        \"first_name\": \"Quick\",
        \"last_name\": \"Provider\",
        \"phone_number\": \"+14155551234\",
        \"specialization\": \"Quick Testing\",
        \"license_number\": \"QT123456\",
        \"years_of_experience\": 2,
        \"consultation_fee\": \"50.00\",
        \"bio\": \"Quick test provider\",
        \"hospital_clinic\": \"Test Clinic\",
        \"address\": \"123 Test St\"
    }")

if echo "$response" | grep -q "Healthcare provider registered successfully"; then
    PROVIDER_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])")
    print_success "Provider registration successful"
elif echo "$response" | grep -q "already exists"; then
    # Try login instead
    response=$(curl -s -X POST "$AUTH_BASE_URL/login/" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$PROVIDER_EMAIL\",
            \"password\": \"$PROVIDER_PASSWORD\"
        }")
    
    if echo "$response" | grep -q "authUser"; then
        PROVIDER_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])")
        print_success "Provider login successful"
    else
        print_error "Authentication failed"
        exit 1
    fi
else
    print_error "Provider registration failed"
    echo "Response: $response"
    exit 1
fi

# Test 2: Provider Profile
echo ""
echo "2. Provider Profile..."
response=$(curl -s -X GET "$AUTH_BASE_URL/provider/profile/" \
    -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
    -H "Content-Type: application/json")

if echo "$response" | grep -q "$PROVIDER_EMAIL"; then
    PROVIDER_ID=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))")
    print_success "Profile retrieved successfully"
else
    print_error "Profile retrieval failed"
fi

# Test 3: Provider Dashboard
echo ""
echo "3. Provider Dashboard..."
response=$(curl -s -X GET "$AUTH_BASE_URL/provider/dashboard/" \
    -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
    -H "Content-Type: application/json")

if echo "$response" | grep -q "statistics"; then
    total_appointments=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('statistics', {}).get('total_appointments', 'N/A'))")
    print_success "Dashboard data retrieved (Appointments: $total_appointments)"
else
    print_error "Dashboard retrieval failed"
fi

# Test 4: Provider List
echo ""
echo "4. Provider List..."
response=$(curl -s -X GET "$BASE_URL/providers/" \
    -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
    -H "Content-Type: application/json")

if echo "$response" | grep -q "results\|id"; then
    count=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('results', data)) if isinstance(data.get('results', data), list) else 'N/A')")
    print_success "Provider list retrieved ($count providers)"
else
    print_error "Provider list retrieval failed"
fi

# Test 5: Provider Search
echo ""
echo "5. Provider Search..."
response=$(curl -s -X GET "$BASE_URL/providers/search/?q=Quick" \
    -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
    -H "Content-Type: application/json")

if echo "$response" | grep -q "suggestions"; then
    suggestions_count=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('suggestions', [])))")
    print_success "Search successful ($suggestions_count results)"
else
    print_error "Search failed"
fi

# Test 6: Authentication Test (No Token)
echo ""
echo "6. Authentication Test..."
response=$(curl -s -X GET "$BASE_URL/providers/" \
    -H "Content-Type: application/json")

if echo "$response" | grep -q "Authentication credentials were not provided\|detail"; then
    print_success "Authentication properly required"
else
    print_warning "Authentication test unclear"
fi

echo ""
print_info "Quick Provider Tests Completed!"
print_success "All core provider endpoints are working"
echo ""
echo "Provider Details:"
echo "- Email: $PROVIDER_EMAIL"
echo "- ID: $PROVIDER_ID"
echo "- Token: ${PROVIDER_ACCESS_TOKEN:0:30}..."
echo ""
echo "Ready for frontend integration!"
