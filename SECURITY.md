# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Security Considerations

### API Keys

- **Never commit API keys** to the repository
- Store API keys in `.env` file (already in `.gitignore`)
- Use environment variables for sensitive configuration
- Rotate API keys regularly

### Data Privacy

- ScopeSignal processes construction project text locally
- No data is sent to external services except the configured LLM API
- Cache files are stored locally in `.scopesignal_cache/`
- Export files may contain sensitive project information - handle appropriately

### Dependencies

We regularly monitor dependencies for security vulnerabilities:

- Core dependencies are minimal and well-maintained
- Run `pip list --outdated` to check for updates
- Review `requirements.txt` for current versions

### LLM API Security

When using LLM APIs (DeepSeek, Claude, OpenAI):

- Use API keys with appropriate scopes and rate limits
- Monitor API usage at provider dashboard
- Be aware that project update text is sent to the API provider
- Review provider's data retention and privacy policies

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **Do NOT open a public issue**
2. Email the maintainers directly (check GitHub profile for contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Fix timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Next release
  - Low: Next major version

## Security Best Practices

### For Users

1. **Keep dependencies updated**: `pip install -r requirements.txt --upgrade`
2. **Protect API keys**: Never share or commit `.env` file
3. **Review exports**: Check exported files before sharing
4. **Validate inputs**: Don't process untrusted or malicious text
5. **Secure cache**: Protect `.scopesignal_cache/` directory permissions

### For Contributors

1. **No secrets in code**: Use environment variables
2. **Input validation**: Sanitize user inputs
3. **Secure defaults**: Prefer secure configurations
4. **Dependency review**: Vet new dependencies carefully
5. **Code review**: Security-focused review for all PRs

## Known Limitations

### Not Security Features

ScopeSignal is a classification tool, not a security system:

- Does not authenticate users
- Does not encrypt cached data
- Does not sanitize inputs beyond basic validation
- Does not rate-limit API calls (depends on provider)

### Intended Use

- Local development and analysis
- Trusted input data
- Single-user scenarios
- Non-production environments

For production deployments with sensitive data, additional security measures are recommended.

## Security Updates

Security fixes are released as patch versions (e.g., 2.0.1) and documented in:
- [CHANGELOG.md](CHANGELOG.md)
- GitHub Security Advisories
- Release notes

## Acknowledgments

We appreciate responsible disclosure of security issues. Contributors who report valid security vulnerabilities will be acknowledged in release notes (with permission).

---

**Last updated**: January 2026
