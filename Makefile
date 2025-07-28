# Nomadly2 Code Quality Makefile

.PHONY: format check install-hooks test clean

# Auto-format all code
format:
	@echo "🔧 Auto-formatting Python code..."
	black . --line-length 88
	isort . --profile black --line-length 88
	@echo "✅ Code formatting complete!"

# Check code quality without changes
check:
	@echo "🔍 Checking code quality..."
	black . --check --line-length 88
	isort . --profile black --line-length 88 --check-only
	flake8 . --max-line-length 88 --extend-ignore E203,W503
	@echo "✅ Code quality check complete!"

# Type checking (optional)
typecheck:
	@echo "🔍 Running type checker..."
	mypy . --ignore-missing-imports --no-strict-optional || echo "⚠️  Type checking completed with warnings"

# Install pre-commit hooks
install-hooks:
	@echo "🔗 Installing pre-commit hooks..."
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"

# Run pre-commit on all files
precommit:
	@echo "🔍 Running pre-commit on all files..."
	pre-commit run --all-files

# Test the bot (basic syntax check)
test:
	@echo "🧪 Testing bot syntax..."
	python -m py_compile nomadly2_bot.py
	python -m py_compile webhook_server.py
	@echo "✅ Syntax tests passed!"

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned!"

# Setup development environment
setup: install-hooks
	@echo "🚀 Development environment ready!"
	@echo "💡 Use 'make format' to auto-format code"
	@echo "💡 Use 'make check' to check code quality"
	@echo "💡 Use 'make precommit' to run all checks"