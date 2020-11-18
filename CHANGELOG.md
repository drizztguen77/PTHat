# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]
### Added
- Method to calculate revolutions from pulse count and steps per revolution

##  [0.9.10]
### Added
- MultipleMotors example

### Fixed
- A bug in the other examples in the show_responses() method
- Method parameters and defaults so defaults don't overwrite variables already set

##  [0.9.9]
### Removed
- Removed command_type and command_id parameters from each method and added them to the constructors as they need to be set only once per instance.

##  [0.9.8]
### Changed
- All command_id parameters were defaulted to a string so had to change it to an int

##  [0.9.7]
### Added
- Parameters to methods that needed them

### Changed
- Updated API documentation

##  [0.9.6]
### Removed
- Print statement from the get_response() method

##  [0.9.5]
### Changed
- The get_responses method to get_all_responses and changed it to return all responses
- The CheckFirmwareVersion and SimpleAxis examples to use the new methods

### Added
- New get_response method to return a single response

##  [0.9.1]
### Added
- New API for the PTHat
- version read only property.
- auto_send_command variable
- method to calculate pulse count

##  [0.9.1]
### Added
- new setup files and uploaded project to PyPI


[Unreleased]: https://github.com/drizztguen77/pthat/compare/v0.9.10...HEAD
[0.9.10]: https://github.com/drizztguen77/pthat/compare/v0.9.9...v0.9.10
[0.9.9]: https://github.com/drizztguen77/pthat/compare/v0.9.8...v0.9.9
[0.9.8]: https://github.com/drizztguen77/pthat/compare/v0.9.7...v0.9.8
[0.9.7]: https://github.com/drizztguen77/pthat/compare/v0.9.6...v0.9.7
[0.9.6]: https://github.com/drizztguen77/pthat/compare/v0.9.5...v0.9.6
[0.9.5]: https://github.com/drizztguen77/pthat/compare/v0.9.1...v0.9.5
[0.9.1]: https://github.com/drizztguen77/pthat/compare/v0.0.0...v0.9.1
