# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Fix inconsistent date formats. All the new date fields now follow the English format `MM/DD/YYYY`. [#57]
- Build the Docker image with the right version of ScrAPD. [#61]
- Fix the parsing of the `Notes`. [#60]
- Further improvements to `Notes` parsing. [#64]
- Remove duplicate fatality entries. [#66]

## [[1.4.2]] - 2019-03-03

### Changed

- Improve fatality page detection. [#47]

## [[1.4.1]] - 2019-02-23

### Fixed

- Fix Changelog and documentation. [#46]

## [[1.4.0]] - 2019-02-23

### Added

- Improved date parsing and date manipulation operations. [#45]

### Changed

- Simplify the tool by removing the `retrieve` subcommand. ScrAPD is a tool to do exactly that, there is no need for
  subcommands.

### Fixed

- Fix incorrect date filtering condition. [#44]
- Improve regex to detect fatality links. [#44]
- Improve twitter description parsing. [#44]

## [[1.3.0]] - 2019-02-16

### Added

- Add a Docker image to run ScrAPD from a container. [#38]

## [[1.2.0]] - 2019-02-09

### Added

- Add flag to only count the results. [#31]
- Add Google Sheet support. [#35]

### Fixed

- Fix issue where scrapd was retrieving unnecessary data. [#28]

## [[1.1.0]] - 2019-01-25

### Added

- Add the `Notes` column to the csv output. [#13]
- Add feature tests to be able to validate scenarios in a manner that reflects the user interaction with the software. [#14]
- Add CircleCI jobs to automatically publish a new release on PyPI. [#23]

### Fixed

- Fix incorrect package metadata. [#20]

## [[1.0.0]] - 2019-01-21

Initial release.

This first version allows a user to retrieve traffic fatality repports for a certain period of time and export the results as csv, json or python.

[//]: # (Release links)
[1.0.0]: https://github.com/scrapd/scrapd/releases/1.0.0
[1.1.0]: https://github.com/scrapd/scrapd/releases/1.1.0
[1.2.0]: https://github.com/scrapd/scrapd/releases/1.2.0
[1.3.0]: https://github.com/scrapd/scrapd/releases/1.3.0
[1.4.0]: https://github.com/scrapd/scrapd/releases/1.4.0
[1.4.1]: https://github.com/scrapd/scrapd/releases/1.4.1
[1.4.2]: https://github.com/scrapd/scrapd/releases/1.4.2

[//]: # (Issue/PR links)
[#13]: https://github.com/scrapd/scrapd/issues/13
[#14]: https://github.com/scrapd/scrapd/issues/14
[#20]: https://github.com/scrapd/scrapd/issues/20
[#23]: https://github.com/scrapd/scrapd/issues/23
[#28]: https://github.com/scrapd/scrapd/issues/28
[#31]: https://github.com/scrapd/scrapd/issues/31
[#35]: https://github.com/scrapd/scrapd/issues/35
[#38]: https://github.com/scrapd/scrapd/issues/38
[#44]: https://github.com/scrapd/scrapd/pull/44
[#45]: https://github.com/scrapd/scrapd/pull/45
[#46]: https://github.com/scrapd/scrapd/pull/46
[#47]: https://github.com/scrapd/scrapd/pull/47
[#57]: https://github.com/scrapd/scrapd/pull/57
[#60]: https://github.com/scrapd/scrapd/pull/60
[#61]: https://github.com/scrapd/scrapd/pull/61
[#64]: https://github.com/scrapd/scrapd/pull/64
