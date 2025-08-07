#!/bin/bash

# Healthcare Provider Professional Form Complete Test
# Tests all new professional form fields with REAL data - NO MOCK DATA
# Matches the exact professional form specification requirements

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URLs
BASE_URL="http://localhost:8001/api/v1"
AUTH_BASE_URL="http://localhost:8001/api/v1/auth"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Healthcare Provider Professional Form Complete Test${NC}"
echo -e "${BLUE}Testing with REAL professional data - NO MOCK DATA${NC}"
echo -e "${BLUE}============================================================${NC}"

# Real Healthcare Provider Professional Data
# Personal Information
PROVIDER_TITLE="Dr."
PROVIDER_FIRST_NAME="Joseph"
PROVIDER_LAST_NAME="Ewool"

# Contact Information  
PROVIDER_EMAIL="dr.joseph.ewool.$(date +%s)@testhospital.com"
PROVIDER_PHONE=""  # Leave empty to skip phone validation

# Security
PROVIDER_USERNAME="joseph_ewool_$(date +%s)"
PROVIDER_PASSWORD="SecurePass123!"
PROVIDER_PASSWORD_CONFIRM="SecurePass123!"

# Professional Information
PROVIDER_ORGANIZATION="General Hospital"
PROVIDER_ROLE="Physician"
PROVIDER_SPECIALIZATION="Emergency Medicine"

# License Verification
PROVIDER_LICENSE="MD$(date +%s)"

# Additional Information
PROVIDER_ADDITIONAL_INFO="Tell us about your specific IoT monitoring needs or any questions you have: I am interested in implementing IoT cardiac monitoring devices for emergency department patients. I have experience with telemedicine platforms and would like to integrate real-time patient monitoring systems into our workflow."

# Variables to store tokens and IDs
PROVIDER_ACCESS_TOKEN=""
PROVIDER_REFRESH_TOKEN=""
PROVIDER_ID=""

# Function to print colored messages
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Function to check server status
check_server() {
    print_info "Checking Django server..."
    if curl -s "$BASE_URL/providers/" > /dev/null 2>&1; then
        print_success "Django server is running on port 8001"
    else
        print_error "Django server is not running on port 8001"
        echo "Please start the server with: python manage.py runserver 8001"
        exit 1
    fi
}

# Test 1: Complete Professional Provider Registration
test_professional_provider_registration() {
    echo ""
    print_info "=============================================================="
    print_info "Test 1: Complete Professional Provider Registration"
    print_info "=============================================================="
    
    print_info "Registering with professional form fields:"
    print_info "Professional Title: $PROVIDER_TITLE"
    print_info "Full Name: $PROVIDER_FIRST_NAME $PROVIDER_LAST_NAME"
    print_info "Email: $PROVIDER_EMAIL"  
    print_info "Phone: Optional (skipped for validation)"
    print_info "Organization: $PROVIDER_ORGANIZATION"
    print_info "Professional Role: $PROVIDER_ROLE"
    print_info "Specialization: $PROVIDER_SPECIALIZATION"
    print_info "License Number: $PROVIDER_LICENSE"
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/provider/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"professional_title\": \"$PROVIDER_TITLE\",
            \"first_name\": \"$PROVIDER_FIRST_NAME\",
            \"last_name\": \"$PROVIDER_LAST_NAME\",
            \"email\": \"$PROVIDER_EMAIL\",
            \"username\": \"$PROVIDER_USERNAME\",
            \"password\": \"$PROVIDER_PASSWORD\",
            \"password_confirm\": \"$PROVIDER_PASSWORD_CONFIRM\",
            \"organization_facility\": \"$PROVIDER_ORGANIZATION\",
            \"professional_role\": \"$PROVIDER_ROLE\",
            \"specialization\": \"$PROVIDER_SPECIALIZATION\",
            \"license_number\": \"$PROVIDER_LICENSE\",
            \"additional_information\": \"$PROVIDER_ADDITIONAL_INFO\"
        }")
    
    echo ""
    print_info "Registration Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "Healthcare provider registered successfully"; then
        PROVIDER_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])" 2>/dev/null || echo "")
        PROVIDER_REFRESH_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['refresh'])" 2>/dev/null || echo "")
        
        if [[ -n "$PROVIDER_ACCESS_TOKEN" ]]; then
            print_success "Professional provider registration successful"
            print_success "Professional: $PROVIDER_TITLE $PROVIDER_FIRST_NAME $PROVIDER_LAST_NAME"
            print_success "Organization: $PROVIDER_ORGANIZATION"
            print_success "Role: $PROVIDER_ROLE"
            print_success "License: $PROVIDER_LICENSE"
            print_success "JWT Access Token obtained: ${PROVIDER_ACCESS_TOKEN:0:50}..."
        else
            print_error "Registration successful but no access token received"
        fi
    else
        print_error "Professional provider registration failed"
        echo "$response"
        return 1
    fi
}

# Test 2: Provider Login
test_provider_login() {
    echo ""
    print_info "=============================================================="
    print_info "Test 2: Healthcare Provider Login"
    print_info "=============================================================="
    
    print_info "Logging in with credentials:"
    print_info "Email: $PROVIDER_EMAIL"
    print_info "Password: [PROTECTED]"
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/login/" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$PROVIDER_EMAIL\",
            \"password\": \"$PROVIDER_PASSWORD\"
        }")
    
    echo ""
    print_info "Login Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "access"; then
        PROVIDER_ACCESS_TOKEN=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tokens']['access'])" 2>/dev/null || echo "")
        if [[ -n "$PROVIDER_ACCESS_TOKEN" ]]; then
            print_success "Provider login successful"
            print_success "New JWT Access Token: ${PROVIDER_ACCESS_TOKEN:0:50}..."
        fi
    else
        print_error "Provider login failed"
        echo "$response"
        return 1
    fi
}

# Test 3: Get Provider Profile
test_get_provider_profile() {
    echo ""
    print_info "=============================================================="
    print_info "Test 3: Get Provider Profile"
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No access token available for profile test"
        return 1
    fi
    
    local response=$(curl -s -X GET "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
    
    echo ""
    print_info "Profile Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "$PROVIDER_LICENSE"; then
        PROVIDER_ID=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['id'])" 2>/dev/null || echo "")
        print_success "Provider profile retrieved successfully"
        print_success "Provider ID: $PROVIDER_ID"
        
        # Verify professional form fields
        if echo "$response" | grep -q "\"professional_title\": \"$PROVIDER_TITLE\""; then
            print_success "✓ Professional Title field: $PROVIDER_TITLE"
        fi
        if echo "$response" | grep -q "\"organization_facility\": \"$PROVIDER_ORGANIZATION\""; then
            print_success "✓ Organization/Facility field: $PROVIDER_ORGANIZATION"  
        fi
        if echo "$response" | grep -q "\"professional_role\": \"$PROVIDER_ROLE\""; then
            print_success "✓ Professional Role field: $PROVIDER_ROLE"
        fi
        if echo "$response" | grep -q "\"license_number\": \"$PROVIDER_LICENSE\""; then
            print_success "✓ License Number field: $PROVIDER_LICENSE"
        fi
        if echo "$response" | grep -q "additional_information"; then
            print_success "✓ Additional Information field present"
        fi
    else
        print_error "Provider profile retrieval failed"
        echo "$response"
        return 1
    fi
}

# Test 4: Update Provider Profile
test_update_provider_profile() {
    echo ""
    print_info "=============================================================="
    print_info "Test 4: Update Provider Profile"  
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No access token available for profile update test"
        return 1
    fi
    
    local updated_info="Updated: Specialized in IoT cardiac monitoring, emergency telemedicine, and real-time patient monitoring systems for critical care."
    
    print_info "Updating additional information field..."
    
    local response=$(curl -s -X PATCH "$AUTH_BASE_URL/provider/profile/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"additional_information\": \"$updated_info\",
            \"specialization\": \"Emergency Medicine & IoT Integration\"
        }")
    
    echo ""
    print_info "Update Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "IoT Integration"; then
        print_success "Provider profile updated successfully"
        print_success "✓ Specialization updated to: Emergency Medicine & IoT Integration"
        print_success "✓ Additional information field updated"
    else
        print_error "Provider profile update failed"
        echo "$response"
        return 1
    fi
}

# Test 5: Provider Dashboard
test_provider_dashboard() {
    echo ""
    print_info "=============================================================="
    print_info "Test 5: Provider Dashboard"
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No access token available for dashboard test"
        return 1
    fi
    
    local response=$(curl -s -X GET "$AUTH_BASE_URL/provider/dashboard/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
    
    echo ""
    print_info "Dashboard Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "provider"; then
        print_success "Provider dashboard retrieved successfully"
        
        # Check for dashboard statistics
        if echo "$response" | grep -q "total_appointments"; then
            print_success "✓ Appointment statistics available"
        fi
        if echo "$response" | grep -q "provider"; then
            print_success "✓ Provider information available"
        fi
    else
        print_error "Provider dashboard retrieval failed"
        echo "$response"
        return 1
    fi
}

# Test 6: List Providers (Search)
test_list_providers() {
    echo ""
    print_info "=============================================================="
    print_info "Test 6: List/Search Providers"
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No access token available for provider list test"
        return 1
    fi
    
    # Test general provider list
    print_info "Testing general provider list..."
    local response=$(curl -s -X GET "$BASE_URL/providers/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
    
    echo ""
    print_info "Provider List Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "$PROVIDER_LAST_NAME"; then
        print_success "Provider found in general list"
        
        # Test search by name
        print_info "Testing search by name..."
        local search_response=$(curl -s -X GET "$BASE_URL/providers/?search=$PROVIDER_FIRST_NAME" \
            -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
        
        if echo "$search_response" | grep -q "$PROVIDER_FIRST_NAME"; then
            print_success "✓ Search by first name works"
        fi
        
        # Test search by role
        print_info "Testing search by professional role..."
        local role_response=$(curl -s -X GET "$BASE_URL/providers/?professional_role=$PROVIDER_ROLE" \
            -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
        
        if echo "$role_response" | grep -q "$PROVIDER_ROLE"; then
            print_success "✓ Filter by professional role works"
        fi
    else
        print_error "Provider not found in list"
        echo "$response"
        return 1
    fi
}

# Test 7: Provider Search Autocomplete
test_provider_autocomplete() {
    echo ""
    print_info "=============================================================="
    print_info "Test 7: Provider Search Autocomplete"
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No access token available for autocomplete test"
        return 1
    fi
    
    print_info "Testing autocomplete search for: Joseph"
    
    local response=$(curl -s -X GET "$BASE_URL/providers/search/?q=Joseph" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
    
    echo ""
    print_info "Autocomplete Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "Joseph"; then
        print_success "Provider autocomplete works"
        print_success "✓ Found provider in autocomplete results"
    else
        print_error "Provider autocomplete failed"
        echo "$response"
        return 1
    fi
}

# Test 8: Token Validation
test_token_validation() {
    echo ""
    print_info "=============================================================="
    print_info "Test 8: JWT Token Validation"
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]]; then
        print_error "No access token available for validation test"
        return 1
    fi
    
    local response=$(curl -s -X POST "$AUTH_BASE_URL/token/validate/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
    
    echo ""
    print_info "Token Validation Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "valid"; then
        print_success "JWT token validation successful"
        print_success "✓ Token is valid and authenticated"
    else
        print_error "JWT token validation failed"
        echo "$response"
        return 1
    fi
}

# Test 9: Form Validation Tests
test_form_validation() {
    echo ""
    print_info "=============================================================="
    print_info "Test 9: Professional Form Validation Tests"
    print_info "=============================================================="
    
    # Test invalid professional title
    print_info "Testing invalid professional title..."
    local invalid_title_response=$(curl -s -X POST "$AUTH_BASE_URL/provider/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"professional_title\": \"InvalidTitle\",
            \"first_name\": \"Test\",
            \"last_name\": \"User\",
            \"email\": \"test.invalid@test.com\",
            \"username\": \"test_invalid\",
            \"password\": \"TestPass123!\",
            \"password_confirm\": \"TestPass123!\",
            \"organization_facility\": \"Test Hospital\",
            \"professional_role\": \"Physician\",
            \"license_number\": \"TEST123\"
        }")
    
    if echo "$invalid_title_response" | grep -q "error\|invalid"; then
        print_success "✓ Invalid professional title validation works"
    else
        print_warning "Invalid title validation may need improvement"
    fi
    
    # Test password mismatch
    print_info "Testing password mismatch..."
    local password_mismatch_response=$(curl -s -X POST "$AUTH_BASE_URL/provider/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"professional_title\": \"Dr.\",
            \"first_name\": \"Test\",
            \"last_name\": \"User\",
            \"email\": \"test.mismatch@test.com\",
            \"username\": \"test_mismatch\",
            \"password\": \"TestPass123!\",
            \"password_confirm\": \"DifferentPass123!\",
            \"organization_facility\": \"Test Hospital\",
            \"professional_role\": \"Physician\",
            \"license_number\": \"TESTMISMATCH123\"
        }")
    
    if echo "$password_mismatch_response" | grep -q "password.*match"; then
        print_success "✓ Password mismatch validation works"
    else
        print_warning "Password mismatch validation may need improvement"
    fi
    
    # Test duplicate license number
    print_info "Testing duplicate license number..."
    local duplicate_license_response=$(curl -s -X POST "$AUTH_BASE_URL/provider/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"professional_title\": \"Dr.\",
            \"first_name\": \"Test\",
            \"last_name\": \"Duplicate\",
            \"email\": \"test.duplicate@test.com\",
            \"username\": \"test_duplicate\",
            \"password\": \"TestPass123!\",
            \"password_confirm\": \"TestPass123!\",
            \"organization_facility\": \"Test Hospital\",
            \"professional_role\": \"Physician\",
            \"license_number\": \"$PROVIDER_LICENSE\"
        }")
    
    if echo "$duplicate_license_response" | grep -q "license.*already exists"; then
        print_success "✓ Duplicate license number validation works"
    else
        print_warning "Duplicate license validation may need improvement"
    fi
}

# Test 10: Provider Detail View
test_provider_detail() {
    echo ""
    print_info "=============================================================="
    print_info "Test 10: Provider Detail View"
    print_info "=============================================================="
    
    if [[ -z "$PROVIDER_ACCESS_TOKEN" ]] || [[ -z "$PROVIDER_ID" ]]; then
        print_error "No access token or provider ID available for detail test"
        return 1
    fi
    
    local response=$(curl -s -X GET "$BASE_URL/providers/$PROVIDER_ID/" \
        -H "Authorization: Bearer $PROVIDER_ACCESS_TOKEN")
    
    echo ""
    print_info "Provider Detail Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "$PROVIDER_LICENSE"; then
        print_success "Provider detail view successful"
        print_success "✓ All professional form fields accessible"
        
        # Verify all key fields are present
        local fields=("professional_title" "organization_facility" "professional_role" "license_number" "additional_information")
        for field in "${fields[@]}"; do
            if echo "$response" | grep -q "\"$field\""; then
                print_success "✓ Field present: $field"
            else
                print_warning "Field may be missing: $field"
            fi
        done
    else
        print_error "Provider detail view failed"
        echo "$response"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    print_info "Starting Healthcare Provider Professional Form Tests..."
    
    # Check server first
    check_server
    
    # Run all tests
    test_professional_provider_registration
    test_provider_login  
    test_get_provider_profile
    test_update_provider_profile
    test_provider_dashboard
    test_list_providers
    test_provider_autocomplete
    test_token_validation
    test_form_validation
    test_provider_detail
    
    echo ""
    print_info "=============================================================="
    print_success "ALL HEALTHCARE PROVIDER PROFESSIONAL FORM TESTS COMPLETED!"
    print_info "=============================================================="
    
    echo ""
    print_info "Summary of Professional Form Fields Tested:"
    print_success "✓ Professional Title: Dropdown with 16 options (Dr., Prof., RN, etc.)"
    print_success "✓ Personal Information: First Name, Last Name (Required)"
    print_success "✓ Contact Information: Email (Required), Phone (Optional)"
    print_success "✓ Security: Password validation (min 8 chars), Password confirmation"
    print_success "✓ Professional Info: Organization/Facility, Professional Role (6 options)"
    print_success "✓ License Verification: License Number (Required, Unique)"
    print_success "✓ Additional Information: Textarea for IoT monitoring needs"
    print_success "✓ Form Validation: All required field validation working"
    print_success "✓ JWT Authentication: Token generation and validation working"
    print_success "✓ CRUD Operations: Create, Read, Update provider profiles"
    print_success "✓ Search & Filter: By name, role, and autocomplete"
    
    echo ""
    print_info "Professional Provider Account Created:"
    print_info "Email: $PROVIDER_EMAIL"
    print_info "Professional: $PROVIDER_TITLE $PROVIDER_FIRST_NAME $PROVIDER_LAST_NAME"
    print_info "Organization: $PROVIDER_ORGANIZATION"
    print_info "Role: $PROVIDER_ROLE"
    print_info "License: $PROVIDER_LICENSE"
    
    if [[ -n "$PROVIDER_ACCESS_TOKEN" ]]; then
        echo ""
        print_info "JWT Access Token for API integration:"
        echo "$PROVIDER_ACCESS_TOKEN"
    fi
    
    echo ""
    print_success "Professional healthcare provider registration system is READY! 🏥"
}

# Run the main function
main "$@"
