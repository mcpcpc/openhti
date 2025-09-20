# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2025-04-29

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
[0.0.3]: https://github.com/mcpcpc/openhti/releases/tag/0.0.3
