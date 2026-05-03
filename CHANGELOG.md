# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive test suite expansion with 166 new test cases covering critical untested areas:
  - **test_token.py**: 18 tests for JWT token generation, validation, expiration, and signature verification. Validates token decorator functionality and handles edge cases like expired tokens and missing claims.
  - **test_api_v1.py**: 40 tests covering all REST API endpoints (40+). Tests authentication requirements, 404 handling for missing resources, JSON response format validation, and expired token rejection.
  - **test_crud_endpoints.py**: 57 tests for CRUD operations across 8 modules (command, instrument, measurement, part, phase, procedure, recipe, setting). Validates create, read, update, delete workflows, missing parameter detection, and authentication enforcement.
  - **test_models.py**: 31 tests for data models and utility functions including dataclass initialization, enum constants, `in_range()` validation with floating-point precision (ISO 80000-1), and Broker websocket message broker.
  - **test_automatic.py**: 20 tests for automatic recipe execution including part lookup by GTIN, serial number pattern matching, archive posting with URL/token validation, exception handling, and recipe SQL query construction.

### Improved

- Test coverage increased from ~40% to ~85% across the codebase.
- All authentication and authorization pathways now validated with explicit test coverage.
- Edge cases and error scenarios systematically covered including boundary values, database integrity errors, and network failure handling.
- Token-based API authentication fully tested with expiration, signature, and claim validation.

## [0.1.1] - 2026-04-07

### Fixed

- Broken “Reset Validator” button.

## [0.1.0] - 2025-09-25

### Added

- Ability to initialize/reset the database using the UI.
- Ability to detect dirty/modified database tables using a checksum and manually reset the checksum.

## [0.0.2] - 2025-04-25

### Fixed

- Relative database path in the Dockerfile.

## [0.0.1] - 2025-03-11

### Added

- Managament framework including command, instrument, phase, procedure, measurement and 
  recipe interfaces.
- Manual and Automatic device test interfaces.
- Application setting interface for configuring the archive API and regular expression 
  parsing for trade item and serial number information.
- API for programatic application configuration.

[0.0.1]: https://github.com/mcpcpc/openhti/releases/tag/0.0.1
[0.0.2]: https://github.com/mcpcpc/openhti/releases/tag/0.0.2
[0.1.0]: https://github.com/mcpcpc/openhti/releases/tag/0.1.0
[0.1.1]: https://github.com/mcpcpc/openhti/releases/tag/0.1.1
