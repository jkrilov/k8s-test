# Troubleshooting GitHub Actions CI/CD

This document provides solutions for common issues encountered with the GitHub Actions workflows.

## Common Issues and Solutions

### 1. Codecov Upload Failures

**Error**: `Token required - not valid tokenless upload`

**Solution**: 
- The Codecov upload is optional and won't fail the CI pipeline
- To enable it properly:
  1. Sign up at [codecov.io](https://codecov.io)
  2. Connect your GitHub repository
  3. Add `CODECOV_TOKEN` to your GitHub repository secrets
  4. Update the workflow to use the token:
  ```yaml
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
  ```

### 2. Kubernetes Validation Errors

**Error**: `Failed initializing schema` for ServiceMonitor/PrometheusRule

**Solution**: 
- These are Custom Resource Definitions (CRDs) from Prometheus Operator
- The workflow now validates core Kubernetes resources only
- Monitoring resources require Prometheus Operator to be installed:
  ```bash
  kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/download/v0.68.0/bundle.yaml
  ```

### 3. Docker Build Issues

**Error**: Docker build fails or times out

**Solutions**:
- Ensure the `Dockerfile` is in the repository root
- Check that all required files are copied in the Dockerfile
- Verify the base image is accessible
- Use Docker layer caching to speed up builds

### 4. Test Failures

**Error**: Tests fail in CI but pass locally

**Common causes**:
- Missing dependencies in CI environment
- Environment variable differences
- Timezone issues
- File path differences (Windows vs Linux)

**Solutions**:
- Check that all dependencies are in `pyproject.toml`
- Use environment variables with defaults
- Use UTC timezone for tests
- Use `pathlib` for cross-platform paths

### 5. Security Scan Issues

**Error**: Bandit security scan fails

**Solutions**:
- Review the security findings
- Add exceptions to `.bandit` configuration if needed
- Use `# nosec` comments for false positives
- Update the skip list in the workflow

### 6. Import/Formatting Issues

**Error**: Black or isort formatting failures

**Solutions**:
- Run formatting locally:
  ```bash
  uv run black src/ tests/
  uv run isort src/ tests/
  ```
- Check the configuration in `pyproject.toml`
- Ensure all imports are properly organized

### 7. Permission Issues

**Error**: Permission denied on scripts

**Solutions**:
- For Linux/macOS: `chmod +x scripts/*.sh`
- For Windows: Use PowerShell execution policy
- Check that git maintains executable permissions

## Local Testing

Before pushing changes, run the local CI script:

```bash
# Linux/macOS
./scripts/ci-local.sh

# Windows PowerShell
./scripts/ci-local.ps1
```

This will catch most issues before they reach the CI pipeline.

## Getting Help

1. Check the GitHub Actions logs for detailed error messages
2. Review this troubleshooting guide
3. Test locally using the provided scripts
4. Check the project's issue tracker for known problems
5. Create a new issue with detailed error logs if needed

## Useful Commands

```bash
# Check workflow status
gh workflow list

# View workflow run details
gh run view

# Re-run failed workflow
gh run rerun

# Check repository secrets
gh secret list

# Validate Kubernetes manifests locally
kubectl apply --dry-run=client -f k8s/
```
