# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities to: **dadighat@gmail.com**

Do not file a public issue for security concerns. Email reports will be kept confidential.

## Response Time

- Initial response: within 48 hours
- Updates: every 7 days until resolved

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| < 2.0   | :x:                |

## Security Best Practices

When deploying OneEmployeeOrg:

1. **Change the default SECRET_KEY** - Generate a secure random key
2. **Use HTTPS** - Never run production without TLS
3. **Keep dependencies updated** - Run `pip install -U` regularly
4. **Use environment variables** - Never commit secrets to git
5. **Enable branch protection** - Require PR reviews before merging
