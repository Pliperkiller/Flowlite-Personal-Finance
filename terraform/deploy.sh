#!/bin/bash

# ================================================================
# Flowlite Azure Infrastructure Deployment Script
# ================================================================
# This script automates the deployment of Flowlite infrastructure
# on Azure using Terraform.
#
# Usage:
#   ./deploy.sh [command] [environment]
#
# Commands:
#   init      - Initialize Terraform
#   plan      - Create execution plan
#   apply     - Apply infrastructure changes
#   destroy   - Destroy infrastructure
#   setup     - Initial setup (create vars, SSH keys)
#   full      - Full deployment (init + plan + apply)
#
# Examples:
#   ./deploy.sh setup
#   ./deploy.sh init
#   ./deploy.sh plan
#   ./deploy.sh apply
# ================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARS_FILE="terraform.tfvars"
VARS_EXAMPLE="terraform.tfvars.example"
PLAN_FILE="tfplan"

# ================================================================
# Helper Functions
# ================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Please install: https://www.terraform.io/downloads.html"
        exit 1
    fi
    log_success "Terraform $(terraform version | head -n1 | cut -d' ' -f2) found"

    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    log_success "Azure CLI $(az version | jq -r '.\"azure-cli\"') found"

    # Check Azure login
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Please run: az login"
        exit 1
    fi

    local subscription=$(az account show --query name -o tsv)
    log_success "Logged into Azure subscription: $subscription"
}

check_vars_file() {
    if [ ! -f "$VARS_FILE" ]; then
        log_error "Variables file '$VARS_FILE' not found."
        log_info "Run: ./deploy.sh setup"
        exit 1
    fi
}

generate_ssh_key() {
    log_info "Checking SSH key..."

    if [ ! -f ~/.ssh/id_rsa ]; then
        log_warning "SSH key not found. Generating..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        log_success "SSH key generated at ~/.ssh/id_rsa"
    else
        log_success "SSH key already exists"
    fi
}

# ================================================================
# Command Functions
# ================================================================

cmd_setup() {
    log_info "Setting up Terraform environment..."

    # Create vars file from example
    if [ ! -f "$VARS_FILE" ]; then
        cp "$VARS_EXAMPLE" "$VARS_FILE"
        log_success "Created $VARS_FILE from $VARS_EXAMPLE"
        log_warning "IMPORTANT: Edit $VARS_FILE with your values before deploying!"
    else
        log_warning "$VARS_FILE already exists. Skipping..."
    fi

    # Generate SSH key
    generate_ssh_key

    log_success "Setup complete!"
    log_info "Next steps:"
    echo "  1. Edit $VARS_FILE with your configuration"
    echo "  2. Run: ./deploy.sh init"
    echo "  3. Run: ./deploy.sh plan"
    echo "  4. Run: ./deploy.sh apply"
}

cmd_init() {
    log_info "Initializing Terraform..."
    terraform init -upgrade
    log_success "Terraform initialized!"
}

cmd_validate() {
    log_info "Validating Terraform configuration..."
    terraform validate
    log_success "Configuration is valid!"
}

cmd_fmt() {
    log_info "Formatting Terraform files..."
    terraform fmt -recursive
    log_success "Files formatted!"
}

cmd_plan() {
    check_vars_file

    log_info "Creating Terraform plan..."
    terraform plan -out="$PLAN_FILE"

    log_success "Plan created successfully!"
    log_info "Review the plan above, then run: ./deploy.sh apply"
}

cmd_apply() {
    if [ ! -f "$PLAN_FILE" ]; then
        log_error "Plan file not found. Run: ./deploy.sh plan"
        exit 1
    fi

    log_info "Applying Terraform configuration..."
    log_warning "This will create/modify Azure resources!"

    terraform apply "$PLAN_FILE"
    rm -f "$PLAN_FILE"

    log_success "Infrastructure deployed successfully!"
    log_info "View outputs with: terraform output"

    # Show important outputs
    echo ""
    log_info "Important outputs:"
    echo "  Application Gateway IP: $(terraform output -raw app_gateway_public_ip 2>/dev/null || echo 'N/A')"
    echo "  Resource Group: $(terraform output -raw resource_group_name 2>/dev/null || echo 'N/A')"
    echo "  Container Registry: $(terraform output -raw acr_login_server 2>/dev/null || echo 'N/A')"
}

cmd_destroy() {
    log_warning "This will DESTROY all infrastructure managed by Terraform!"
    log_warning "This action is IRREVERSIBLE!"
    echo ""
    read -p "Are you sure? Type 'yes' to continue: " confirmation

    if [ "$confirmation" != "yes" ]; then
        log_info "Destroy cancelled."
        exit 0
    fi

    log_info "Destroying infrastructure..."
    terraform destroy

    log_success "Infrastructure destroyed."
}

cmd_output() {
    log_info "Terraform outputs:"
    terraform output
}

cmd_full() {
    log_info "Starting full deployment..."

    cmd_init
    cmd_validate
    cmd_fmt
    cmd_plan

    echo ""
    log_warning "Review the plan above."
    read -p "Continue with apply? (yes/no): " confirmation

    if [ "$confirmation" != "yes" ]; then
        log_info "Deployment cancelled."
        exit 0
    fi

    cmd_apply

    log_success "Full deployment completed!"
}

cmd_acr_login() {
    log_info "Logging into Azure Container Registry..."

    ACR_NAME=$(terraform output -raw acr_name 2>/dev/null)

    if [ -z "$ACR_NAME" ]; then
        log_error "ACR not deployed yet or output not available"
        exit 1
    fi

    az acr login --name "$ACR_NAME"
    log_success "Logged into ACR: $ACR_NAME"
}

cmd_build_images() {
    log_info "Building and pushing Docker images..."

    ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server 2>/dev/null)

    if [ -z "$ACR_LOGIN_SERVER" ]; then
        log_error "ACR not deployed yet"
        exit 1
    fi

    cd ..

    # Identity Service
    log_info "Building Identity Service..."
    docker build -t "$ACR_LOGIN_SERVER/flowlite-identity:latest" ./identifyservice
    docker push "$ACR_LOGIN_SERVER/flowlite-identity:latest"

    # Upload Service
    log_info "Building Upload Service..."
    docker build -t "$ACR_LOGIN_SERVER/flowlite-upload:latest" ./uploadservice
    docker push "$ACR_LOGIN_SERVER/flowlite-upload:latest"

    # Data Service
    log_info "Building Data Service..."
    docker build -t "$ACR_LOGIN_SERVER/flowlite-data:latest" ./dataservice
    docker push "$ACR_LOGIN_SERVER/flowlite-data:latest"

    # Insight Service
    log_info "Building Insight Service..."
    docker build -t "$ACR_LOGIN_SERVER/flowlite-insight:latest" ./InsightService
    docker push "$ACR_LOGIN_SERVER/flowlite-insight:latest"

    cd "$SCRIPT_DIR"

    log_success "All images built and pushed!"
}

show_help() {
    cat << EOF
Flowlite Azure Infrastructure Deployment Script

Usage: $0 [command]

Commands:
  setup         Initial setup (create vars file, SSH keys)
  init          Initialize Terraform
  validate      Validate Terraform configuration
  fmt           Format Terraform files
  plan          Create Terraform execution plan
  apply         Apply Terraform configuration
  destroy       Destroy all infrastructure
  output        Show Terraform outputs
  full          Full deployment (init + validate + plan + apply)
  acr-login     Login to Azure Container Registry
  build-images  Build and push Docker images to ACR
  help          Show this help message

Examples:
  $0 setup
  $0 init
  $0 plan
  $0 apply
  $0 full

For more information, see README.md
EOF
}

# ================================================================
# Main Script
# ================================================================

main() {
    cd "$SCRIPT_DIR"

    local command=${1:-help}

    case "$command" in
        setup)
            cmd_setup
            ;;
        init)
            check_prerequisites
            cmd_init
            ;;
        validate)
            check_prerequisites
            cmd_validate
            ;;
        fmt)
            cmd_fmt
            ;;
        plan)
            check_prerequisites
            cmd_plan
            ;;
        apply)
            check_prerequisites
            cmd_apply
            ;;
        destroy)
            check_prerequisites
            cmd_destroy
            ;;
        output)
            cmd_output
            ;;
        full)
            check_prerequisites
            cmd_full
            ;;
        acr-login)
            cmd_acr_login
            ;;
        build-images)
            cmd_acr_login
            cmd_build_images
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
