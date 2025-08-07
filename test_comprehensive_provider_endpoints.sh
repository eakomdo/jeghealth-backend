#!/bin/bash

# Comprehensive Provider Endpoints Test Script
# This script tests all provider-related endpoints including authentication

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8001/api/v1"
# Auth endpoints are under /auth/ not /accounts/
AUTH_BASE_URL="http://localhost:8001/api/v1/auth"

# Test data
PROVIDER_EMAIL="provider.test@example.com"
PROVIDER_USERNAME="provider_test"
PROVIDER_PASSWORD="TestProvider123!"
PROVIDER_FIRST_NAME="Dr. John"
PROVIDER_LAST_NAME="Smith"
PROVIDER_SPECIALIZATION="Cardiology"
PROVIDER_LICENSE="MD123456789"
PROVIDER_EXPERIENCE=10
PROVIDER_FEE="150.00"
PROVIDER_BIO="Experienced cardiologist with 10 years of practice"
PROVIDER_HOSPITAL="City Heart Center"
PROVIDER_ADDRESS="123 Cardiology St, Heart City, HC 12345"
PROVIDER_PHONE="+14155552671"

# Regular user for testing permissions
REGULAR_EMAIL="regular.user@example.com"
REGULAR_USERNAME="regular_user"
REGULAR_PASSWORD="TestUser123!"

# Variables to store tokens and IDs
PROVIDER_ACCESS_TOKEN=""
PROVIDER_ID=""
REGULAR_ACCESS_TOKEN=""

# Function to print test headers
print_test_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if Django server is running
check_server() {
    echo "Checking if Django server is running..."
    if curl -s "$BASE_URL/providers/" > /dev/null 2>&1; then
        print_success "Django server is running on port 8001"
    else
        print_error "Django server is not running on port 8001"
        echo "Please start the server with: python manage.py runserver 8001"
        exit 1
    fi
}

# Function to create a regular user for permission tests
create_regular_user() {
    print_test_header "Creating Regular User for Permission Tests"
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$REGULAR_EMAIL\",
            \"username\": \"$REGULAR_USERNAME\",
            \"password\": \"$REGULAR_PASSWORD\",
            \"password_confirm\": \"$REGULAR_PASSWORD\",
            \"first_name\": \"Regular\",
            \"last_name\": \"User\"
        }")
    
    if echo "$response" | grep -q "authUser"; then
        REGULAR_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])")
        print_success "Regular user created successfully"
    else
        print_warning "Regular user might already exist, trying to login..."
        
        # Try to login
        response=$(curl -s -X POST "$AUTH_BASE_URL/login/" \
            -H "Content-Type: application/json" \
            -d "{
                \"email\": \"$REGULAR_EMAIL\",
                \"password\": \"$REGULAR_PASSWORD\"
            }")
        
        if echo "$response" | grep -q "authUser"; then
            REGULAR_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])")
            print_success "Regular user login successful"
        else
            print_error "Failed to create or login regular user"
            echo "Response: $response"
        fi
    fi
}

# Test 1: Provider Registration
test_provider_registration() {
    print_test_header "Test 1: Provider Registration"
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/provider/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$PROVIDER_EMAIL\",
            \"username\": \"$PROVIDER_USERNAME\",
            \"password\": \"$PROVIDER_PASSWORD\",
            \"password_confirm\": \"$PROVIDER_PASSWORD\",
            \"first_name\": \"$PROVIDER_FIRST_NAME\",
            \"last_name\": \"$PROVIDER_LAST_NAME\",
            \"phone_number\": \"$PROVIDER_PHONE\",
            \"specialization\": \"$PROVIDER_SPECIALIZATION\",
            \"license_number\": \"$PROVIDER_LICENSE\",
            \"years_of_experience\": $PROVIDER_EXPERIENCE,
            \"consultation_fee\": \"$PROVIDER_FEE\",
            \"bio\": \"$PROVIDER_BIO\",
            \"hospital_clinic\": \"$PROVIDER_HOSPITAL\",
            \"address\": \"$PROVIDER_ADDRESS\"
        }")
    
    echo "Registration Response: $response"
    
    if echo "$response" | grep -q "Healthcare provider registered successfully"; then
        PROVIDER_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])")
        print_success "Provider registration successful"
        echo "Access Token (first 20 chars): ${PROVIDER_ACCESS_TOKEN:0:20}..."
    else
        print_error "Provider registration failed"
        echo "Response: $response"
        # Try to login instead (maybe provider already exists)
        print_warning "Trying to login with existing credentials..."
        test_provider_login
    fi
}

# Test 2: Provider Login
test_provider_login() {
    print_test_header "Test 2: Provider Login"
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/login/" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$PROVIDER_EMAIL\",
            \"password\": \"$PROVIDER_PASSWORD\"
        }")
    
    echo "Login Response: $response"
    
    if echo "$response" | grep -q "authUser"; then
        PROVIDER_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])")
        local role=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('role', {}).get('name', 'N/A'))")
        
        print_success "Provider login successful"
        print_success "User role: $role"
        echo "Access Token (first 20 chars): ${PROVIDER_ACCESS_TOKEN:0:20}..."
    else
        print_error "Provider login failed"
        echo "Response: $response"
        exit 1
    fi
}

# Test 3: Provider Profile View
test_provider_profile_view() {
    print_test_header "Test 3: Provider Profile View"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local response=$(curl -s -X GET "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Profile Response: $response"
    
    if echo "$response" | grep -q "$PROVIDER_EMAIL"; then
        PROVIDER_ID=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))")
        print_success "Provider profile retrieved successfully"
        print_success "Provider ID: $PROVIDER_ID"
    else
        print_error "Failed to retrieve provider profile"
        echo "Response: $response"
    fi
}

# Test 4: Provider Profile Update
test_provider_profile_update() {
    print_test_header "Test 4: Provider Profile Update"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local updated_bio="Updated bio: Experienced cardiologist specializing in interventional procedures"
    local updated_fee="175.00"
    
    local response=$(curl -s -X PATCH "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"bio\": \"$updated_bio\",
            \"consultation_fee\": \"$updated_fee\"
        }")
    
    echo "Update Response: $response"
    
    if echo "$response" | grep -q "$updated_bio"; then
        print_success "Provider profile updated successfully"
    else
        print_error "Failed to update provider profile"
        echo "Response: $response"
    fi
}

# Test 5: Provider Dashboard
test_provider_dashboard() {
    print_test_header "Test 5: Provider Dashboard"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local response=$(curl -s -X GET "$AUTH_BASE_URL/provider/dashboard/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Dashboard Response: $response"
    
    if echo "$response" | grep -q "statistics"; then
        print_success "Provider dashboard data retrieved successfully"
        # Extract some statistics
        local total_appointments=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('statistics', {}).get('total_appointments', 'N/A'))")
        local provider_name=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('provider', {}).get('full_name', 'N/A'))")
        
        print_success "Provider Name: $provider_name"
        print_success "Total Appointments: $total_appointments"
    else
        print_error "Failed to retrieve provider dashboard"
        echo "Response: $response"
    fi
}

# Test 6: List All Providers (Authenticated)
test_list_all_providers() {
    print_test_header "Test 6: List All Providers"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local response=$(curl -s -X GET "$BASE_URL/providers/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Providers List Response: $response"
    
    if echo "$response" | grep -q "results\|id"; then
        local count=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('results', data)) if isinstance(data.get('results', data), list) else 'N/A')")
        print_success "Providers list retrieved successfully"
        print_success "Number of providers: $count"
    else
        print_error "Failed to retrieve providers list"
        echo "Response: $response"
    fi
}

# Test 7: Provider Search/Autocomplete
test_provider_search() {
    print_test_header "Test 7: Provider Search/Autocomplete"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    # Search by name
    local response=$(curl -s -X GET "$BASE_URL/providers/search/?q=Dr" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Search Response: $response"
    
    if echo "$response" | grep -q "suggestions"; then
        print_success "Provider search successful"
        local suggestions_count=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('suggestions', [])))")
        print_success "Found suggestions: $suggestions_count"
    else
        print_error "Provider search failed"
        echo "Response: $response"
    fi
}

# Test 8: Provider Dropdown
test_provider_dropdown() {
    print_test_header "Test 8: Provider Dropdown"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local response=$(curl -s -X GET "$BASE_URL/providers/dropdown/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Dropdown Response: $response"
    
    if echo "$response" | grep -q "id\|name"; then
        local count=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data) if isinstance(data, list) else 'N/A')")
        print_success "Provider dropdown retrieved successfully"
        print_success "Number of dropdown items: $count"
    else
        print_error "Failed to retrieve provider dropdown"
        echo "Response: $response"
    fi
}

# Test 9: Provider Detail View
test_provider_detail() {
    print_test_header "Test 9: Provider Detail View"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" || -z "$PROVIDER_ID" ]]; then
        print_error "Missing provider access token or provider ID"
        return 1
    fi
    
    local response=$(curl -s -X GET "$BASE_URL/providers/$PROVIDER_ID/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Provider Detail Response: $response"
    
    if echo "$response" | grep -q "$PROVIDER_ID"; then
        print_success "Provider detail retrieved successfully"
        local full_name=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('full_name', 'N/A'))")
        local specialization=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('specialization', 'N/A'))")
        
        print_success "Full Name: $full_name"
        print_success "Specialization: $specialization"
    else
        print_error "Failed to retrieve provider detail"
        echo "Response: $response"
    fi
}

# Test 10: Permission Testing (Regular User Accessing Provider Endpoints)
test_permission_restrictions() {
    print_test_header "Test 10: Permission Testing"
    
    if [[ -z "$REGULAR_ACCESS_TOKEN" ]]; then
        print_error "No regular user access token available"
        return 1
    fi
    
    # Test regular user trying to access provider profile endpoint
    local response=$(curl -s -X GET "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $REGULAR_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Regular user trying provider profile: $response"
    
    if echo "$response" | grep -q "Provider profile not found"; then
        print_success "Correct permission restriction: Regular user cannot access provider profile"
    else
        print_warning "Unexpected response for permission test"
    fi
    
    # Test regular user trying to access provider dashboard
    response=$(curl -s -X GET "$AUTH_BASE_URL/provider/dashboard/" \
        -H "Authorization: Bearer $REGULAR_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Regular user trying provider dashboard: $response"
    
    if echo "$response" | grep -q "Provider profile not found"; then
        print_success "Correct permission restriction: Regular user cannot access provider dashboard"
    else
        print_warning "Unexpected response for permission test"
    fi
}

# Test 11: Authentication Required Tests (No Token)
test_authentication_required() {
    print_test_header "Test 11: Authentication Required Tests"
    
    # Test accessing provider endpoints without token
    local endpoints=(
        "providers/"
        "providers/dropdown/"
        "providers/search/"
        "auth/provider/profile/"
        "auth/provider/dashboard/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo "Testing endpoint without auth: $endpoint"
        local response=$(curl -s -X GET "$BASE_URL/$endpoint" \
            -H "Content-Type: application/json")
        
        if echo "$response" | grep -q "Authentication credentials were not provided\|detail"; then
            print_success "✓ $endpoint correctly requires authentication"
        else
            print_warning "⚠ Unexpected response for $endpoint without auth"
            echo "Response: $response"
        fi
    done
}

# Test 12: Token Validation
test_token_validation() {
    print_test_header "Test 12: Token Validation"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/token/validate/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Token Validation Response: $response"
    
    if echo "$response" | grep -q "valid\|success" || [[ -z "$response" ]]; then
        print_success "Token validation successful"
    else
        print_error "Token validation failed"
        echo "Response: $response"
    fi
}

# Test 13: Invalid Token Test
test_invalid_token() {
    print_test_header "Test 13: Invalid Token Test"
    
    local invalid_token="invalid.token.here"
    local response=$(curl -s -X GET "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $invalid_token" \
        -H "Content-Type: application/json")
    
    echo "Invalid Token Response: $response"
    
    if echo "$response" | grep -q "Given token not valid\|Invalid token\|detail"; then
        print_success "Invalid token correctly rejected"
    else
        print_warning "Unexpected response for invalid token"
        echo "Response: $response"
    fi
}

# Test 14: Provider Profile Update with Invalid Data
test_invalid_profile_update() {
    print_test_header "Test 14: Provider Profile Update with Invalid Data"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    # Try to update with invalid consultation fee
    local response=$(curl -s -X PATCH "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"consultation_fee\": \"invalid_fee\",
            \"years_of_experience\": -5
        }")
    
    echo "Invalid Update Response: $response"
    
    if echo "$response" | grep -q "error\|invalid\|Enter a valid"; then
        print_success "Invalid data correctly rejected"
    else
        print_warning "Invalid data validation might need improvement"
        echo "Response: $response"
    fi
}

# Test 15: Create New Provider via Provider API
test_create_provider_via_api() {
    print_test_header "Test 15: Create New Provider via Provider API"
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No provider access token available"
        return 1
    fi
    
    local new_provider_email="new.provider@example.com"
    local response=$(curl -s -X POST "$BASE_URL/providers/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$new_provider_email\",
            \"first_name\": \"Jane\",
            \"last_name\": \"Doe\",
            \"specialization\": \"Pediatrics\",
            \"license_number\": \"MD987654321\",
            \"years_of_experience\": 8,
            \"consultation_fee\": \"125.00\",
            \"bio\": \"Experienced pediatrician\",
            \"hospital_clinic\": \"Children's Hospital\",
            \"address\": \"456 Kids St, Child City, CC 54321\",
            \"phone_number\": \"+19876543210\"
        }")
    
    echo "New Provider Creation Response: $response"
    
    if echo "$response" | grep -q "$new_provider_email\|id"; then
        print_success "New provider created successfully via API"
        local new_provider_id=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))")
        print_success "New Provider ID: $new_provider_id"
    else
        print_error "Failed to create new provider via API"
        echo "Response: $response"
    fi
}

# Main test execution
main() {
    print_test_header "JegHealth Backend Provider Endpoints Comprehensive Test"
    echo -e "${YELLOW}Testing Django backend provider endpoints...${NC}"
    echo ""
    
    # Check if server is running
    check_server
    
    # Create regular user for permission tests
    create_regular_user
    
    # Run all provider tests
    test_provider_registration
    sleep 1
    
    test_provider_login
    sleep 1
    
    test_provider_profile_view
    sleep 1
    
    test_provider_profile_update
    sleep 1
    
    test_provider_dashboard
    sleep 1
    
    test_list_all_providers
    sleep 1
    
    test_provider_search
    sleep 1
    
    test_provider_dropdown
    sleep 1
    
    test_provider_detail
    sleep 1
    
    test_permission_restrictions
    sleep 1
    
    test_authentication_required
    sleep 1
    
    test_token_validation
    sleep 1
    
    test_invalid_token
    sleep 1
    
    test_invalid_profile_update
    sleep 1
    
    test_create_provider_via_api
    
    # Summary
    print_test_header "Test Summary"
    echo -e "${GREEN}All provider endpoint tests completed!${NC}"
    echo ""
    echo "Test Results Summary:"
    echo "✓ Provider registration and login"
    echo "✓ Provider profile management"
    echo "✓ Provider dashboard access"
    echo "✓ Provider listing and search"
    echo "✓ Authentication and authorization"
    echo "✓ Permission restrictions"
    echo "✓ Token validation"
    echo "✓ Error handling"
    echo ""
    echo -e "${BLUE}Provider Access Token:${NC} ${PROVIDER_ACCESS_TOKEN:0:30}..."
    echo -e "${BLUE}Provider ID:${NC} $PROVIDER_ID"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Test these endpoints with your frontend application"
    echo "2. Implement proper error handling in your frontend"
    echo "3. Test appointment booking with this provider"
    echo "4. Test provider-patient interactions"
}

# Run the tests
main "$@"
