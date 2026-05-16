# Changelog

## [Unreleased]

### Changed
- Updated Flask from 2.3.0 to 3.1.0
- Updated requests from 2.28.0 to 2.32.3
- Updated gunicorn from 20.1.0 to 22.0.0
- Updated python-dotenv from 0.19.0 to 1.0.1
- Updated Werkzeug from 2.3.0 to 3.1.3

### Fixed
- Flask 3.x deprecation: `app.json_encoder` replaced with `app.json_provider_class`
- Werkzeug 3.x deprecation: `request.json` now raises 415 if content-type is not set
- python-dotenv: renamed `find_dotenv()` behavior change in 1.x
- gunicorn 22.x: `--workers` flag now required for production (no implicit default)

### Breaking Changes
- Minimum Python version now 3.9+ (Flask 3.x requirement)
- `request.get_json()` behavior changed: use `silent=True` for backward compatibility
- Werkzeug security middleware is stricter about header sizes
