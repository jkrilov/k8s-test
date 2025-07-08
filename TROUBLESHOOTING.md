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

**Error**: `Failed initializing schema` for ServiceMonitor/PrometheusRule or `connection refused` errors

**Solution**: 
- The workflow now validates core Kubernetes resources only using multiple validation layers
- Custom Resource Definitions (CRDs) like ServiceMonitor/PrometheusRule are validated separately
- The validation workflow includes:
  1. YAML syntax validation with `yq`
  2. Kubernetes schema validation with `kubectl --dry-run=client --validate=false`
  3. Optional kubeval validation with `--ignore-missing-schemas`
- For local development, monitoring resources require Prometheus Operator:
  ```bash
  kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/download/v0.68.0/bundle.yaml
  ```

### 3. Docker Build Issues

**Error**: `"/uv.lock": not found` or Docker build fails

**Solutions**:
- Ensure `uv.lock` file exists in the repository root:
  ```bash
  uv lock
  ```
- Make sure all required files are committed to git
- Verify the Dockerfile copies the correct files
- Use Docker layer caching to speed up builds
- The build should complete successfully with the generated lock file

**Error**: `Unable to find image 'k8s-test-app:latest' locally` after build

**Solution**:
- When using `docker/build-push-action` with buildx, add `load: true` to load the image into the local Docker daemon:
  ```yaml
  - name: Build Docker image
    uses: docker/build-push-action@v5
    with:
      context: .
      load: true  # This loads the image locally
      tags: k8s-test-app:latest
  ```

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
