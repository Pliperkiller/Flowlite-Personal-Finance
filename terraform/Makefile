.PHONY: help init plan apply destroy clean validate fmt check

# Variables
TERRAFORM := terraform
TERRAFORM_VARS := terraform.tfvars
PLAN_FILE := tfplan

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Flowlite Azure Infrastructure - Terraform Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

init: ## Initialize Terraform (download providers and modules)
	@echo "🔧 Initializing Terraform..."
	$(TERRAFORM) init -upgrade

validate: ## Validate Terraform configuration
	@echo "✅ Validating Terraform configuration..."
	$(TERRAFORM) validate

fmt: ## Format Terraform files
	@echo "🎨 Formatting Terraform files..."
	$(TERRAFORM) fmt -recursive

check: validate fmt ## Run validation and formatting checks
	@echo "✅ All checks passed!"

plan: ## Create Terraform execution plan
	@echo "📋 Creating Terraform plan..."
	@if [ ! -f $(TERRAFORM_VARS) ]; then \
		echo "❌ Error: $(TERRAFORM_VARS) not found. Copy terraform.tfvars.example and edit it."; \
		exit 1; \
	fi
	$(TERRAFORM) plan -out=$(PLAN_FILE)
	@echo "✅ Plan created: $(PLAN_FILE)"
	@echo "💡 Review the plan with: make show"

show: ## Show the Terraform plan
	@echo "📄 Showing Terraform plan..."
	$(TERRAFORM) show $(PLAN_FILE)

apply: ## Apply Terraform configuration
	@echo "🚀 Applying Terraform configuration..."
	@if [ ! -f $(PLAN_FILE) ]; then \
		echo "❌ Error: Plan file not found. Run 'make plan' first."; \
		exit 1; \
	fi
	$(TERRAFORM) apply $(PLAN_FILE)
	@rm -f $(PLAN_FILE)
	@echo "✅ Infrastructure deployed successfully!"
	@echo "💡 View outputs with: make output"

apply-auto: ## Apply without confirmation (dangerous!)
	@echo "⚠️  WARNING: Auto-applying without plan review..."
	$(TERRAFORM) apply -auto-approve

output: ## Show Terraform outputs
	@echo "📊 Terraform Outputs:"
	$(TERRAFORM) output

output-json: ## Show Terraform outputs in JSON format
	@echo "📊 Terraform Outputs (JSON):"
	$(TERRAFORM) output -json

destroy: ## Destroy all Terraform-managed infrastructure
	@echo "⚠️  WARNING: This will DESTROY all infrastructure!"
	@echo "Press Ctrl+C to cancel, or wait 10 seconds to continue..."
	@sleep 10
	$(TERRAFORM) destroy

destroy-auto: ## Destroy without confirmation (VERY DANGEROUS!)
	@echo "⚠️  WARNING: Auto-destroying infrastructure..."
	$(TERRAFORM) destroy -auto-approve

clean: ## Clean Terraform cache and temporary files
	@echo "🧹 Cleaning Terraform cache..."
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f $(PLAN_FILE)
	rm -f plan.txt
	rm -f *.log
	@echo "✅ Cleaned!"

refresh: ## Refresh Terraform state
	@echo "🔄 Refreshing Terraform state..."
	$(TERRAFORM) refresh

state-list: ## List all resources in Terraform state
	@echo "📋 Listing Terraform state resources..."
	$(TERRAFORM) state list

state-show: ## Show detailed resource state (usage: make state-show RESOURCE=azurerm_resource_group.main)
	@if [ -z "$(RESOURCE)" ]; then \
		echo "❌ Error: RESOURCE not specified. Usage: make state-show RESOURCE=azurerm_resource_group.main"; \
		exit 1; \
	fi
	$(TERRAFORM) state show $(RESOURCE)

graph: ## Generate Terraform dependency graph
	@echo "🔗 Generating dependency graph..."
	$(TERRAFORM) graph | dot -Tpng > graph.png
	@echo "✅ Graph saved to graph.png"

docs: ## Generate documentation from Terraform files
	@echo "📚 Generating documentation..."
	@if command -v terraform-docs >/dev/null 2>&1; then \
		terraform-docs markdown table . > TERRAFORM_DOCS.md; \
		echo "✅ Documentation generated: TERRAFORM_DOCS.md"; \
	else \
		echo "❌ terraform-docs not installed. Install with: brew install terraform-docs"; \
		exit 1; \
	fi

cost: ## Estimate infrastructure costs (requires infracost)
	@echo "💰 Estimating costs..."
	@if command -v infracost >/dev/null 2>&1; then \
		infracost breakdown --path .; \
	else \
		echo "❌ infracost not installed. Install from: https://www.infracost.io/"; \
		exit 1; \
	fi

security: ## Run security checks (requires tfsec)
	@echo "🔒 Running security checks..."
	@if command -v tfsec >/dev/null 2>&1; then \
		tfsec .; \
	else \
		echo "❌ tfsec not installed. Install with: brew install tfsec"; \
		exit 1; \
	fi

lint: ## Run Terraform linter (requires tflint)
	@echo "🔍 Running Terraform linter..."
	@if command -v tflint >/dev/null 2>&1; then \
		tflint --init; \
		tflint; \
	else \
		echo "❌ tflint not installed. Install with: brew install tflint"; \
		exit 1; \
	fi

setup: ## Initial setup (copy example vars, generate SSH key)
	@echo "🔧 Setting up Terraform environment..."
	@if [ ! -f $(TERRAFORM_VARS) ]; then \
		cp terraform.tfvars.example $(TERRAFORM_VARS); \
		echo "✅ Created $(TERRAFORM_VARS) from example"; \
		echo "⚠️  IMPORTANT: Edit $(TERRAFORM_VARS) with your values!"; \
	else \
		echo "⚠️  $(TERRAFORM_VARS) already exists. Skipping..."; \
	fi
	@if [ ! -f ~/.ssh/id_rsa ]; then \
		echo "🔑 Generating SSH key..."; \
		ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""; \
		echo "✅ SSH key generated"; \
	else \
		echo "✅ SSH key already exists"; \
	fi
	@echo "✅ Setup complete! Next steps:"
	@echo "   1. Edit $(TERRAFORM_VARS)"
	@echo "   2. Run: make init"
	@echo "   3. Run: make plan"
	@echo "   4. Run: make apply"

login: ## Login to Azure
	@echo "🔐 Logging into Azure..."
	az login
	@echo "📋 Current subscription:"
	az account show

get-outputs: ## Get all outputs and save to file
	@echo "📊 Exporting outputs..."
	$(TERRAFORM) output > outputs.txt
	$(TERRAFORM) output -json > outputs.json
	@echo "✅ Outputs saved to outputs.txt and outputs.json"

acr-login: ## Login to Azure Container Registry
	@echo "🐳 Logging into Azure Container Registry..."
	@ACR_NAME=$$($(TERRAFORM) output -raw acr_name 2>/dev/null); \
	if [ -z "$$ACR_NAME" ]; then \
		echo "❌ Error: ACR not deployed yet or output not available"; \
		exit 1; \
	fi; \
	az acr login --name $$ACR_NAME
	@echo "✅ Logged into ACR"

full-deploy: init validate plan apply ## Full deployment (init -> validate -> plan -> apply)
	@echo "✅ Full deployment completed!"

all: clean init validate fmt plan apply output ## Complete workflow

.PHONY: all
