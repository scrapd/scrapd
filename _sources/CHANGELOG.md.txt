# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [[3.0.4]] - 2020-02-15

### Fixed

- Fix `model.Report` update function. `fatalities` field is now always overridden with the new values. [#234]

## [[3.0.3]] - 2020-01-11

### Fixed

- Fixed parsing of the new page title. [#230]

## [[3.0.2]] - 2019-11-30

### Fixed

- Fix parsing with arrested field. [#227]

## [[3.0.1]] - 2019-10-30

### Fixed

- Fix parsing issues:
  - Fix unidentified deceased. [#220]
  - Fix unknown deceased. [#223]
  - Fix parsing with arrested field. [#224]

## [[3.0.0]] - 2019-10-12

### Added

- Add CLI flag to dump reports with parsing errors on disk. This also adds helper functions and tests to simplify the
  debuging of the dumps. [#214]

### Changed

- The internal format was updated to allow automated data validation, prevent invalid values to injected in the data
  and handle multiple fatalities in one crash. New fields were added such as `middle name` or `generation`. [#199]

### Fixed

- Fixed parsing issues:
  - Fix parsing of `Location` field where its content ws merged with the next field.[#203]
  - Handle reports containing an `Arrested` field.[#204]
  - Handle `born` as a marker to extract the deceased date of birth. [#208]
  - Fix `Date` parsing regex. [#210]

## [[2.1.1]] - 2019-08-22

### Fixed

- Fixed parsing of crashes involving multiple deaths. [#178]

## [[2.1.0]] - 2019-07-17

### Added

- Add CLI flags to parametrize retries at runtime. [#159]
- Add tasks to do some profiling of the application. [#163]
- Improve logging ability by adding more details about a parsing failure. [#167]

### Changed

- Use [nox](https://nox.thea.codes) and [invoke](https://www.pyinvoke.org) for task management execution instead of `make`.

### Fixed

- Fix `Deceased` field parsing:
  - to support date of birth with the following format `August 30, 1966`. [#155]
  - to support describing the age instead of the date of birth (i.e. `19 years of age`).[#172]
- Fix `Location` field parsing to support additional internal formats. [#169]
- Fix `Date` field parsing to support single digit 12 hour format like `8 p.m.`. [#171]
- Fix issues where the notes where either not parsed, or incorrectly parsed. [#166]

## [[2.0.0]] - 2019-06-11

### Added

- Add retries around functions fecthing data from remote sources to increase reliability. [#116]

### Changed

- Refactor the functions parsing the fields to simplify their maintenance and improve the overall quality of the parsing.
- Remove LXML as a dependency. [#117] [#132] [#136] [#138]
- Dates are stored internaly as date objects instead of strings. The formatting is delegated to the `Formatters`
  themselves. [#125]
- Remove GSheet support. [#133]

### Fixed

- Fix parsing of fatalities without date of birth. [#125]
- Fix parsing names with generation suffixes. [#137]
- Skip fields with empty values. [#139]
- Fix parsing short ethnicities in deceased fields. [#140]

## [[1.5.1]] - 2019-04-25

### Fixed

- Fix gender value mix character cases.
- Fix `fetch_text()` by adding retry ability with exponential backoff. [#85]
- Fix incorrect name parsing when a nickname or a middle name was specified. [#84]
- Fix and improve the `Deceased` field parsing. The parser now supports pipe and space delimited fields. [#90]

## [[1.5.0]] - 2019-03-19

### Fixed

- Fix inconsistent date formats. All the new date fields now follow the English format `MM/DD/YYYY`. [#57]
- Build the Docker image with the right version of ScrAPD. [#61]
- Fix the parsing of the `Notes`. [#60], [#64]
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
[1.5.0]: https://github.com/scrapd/scrapd/releases/1.5.0
[1.5.1]: https://github.com/scrapd/scrapd/releases/1.5.1
[2.0.0]: https://github.com/scrapd/scrapd/releases/2.0.0
[2.1.0]: https://github.com/scrapd/scrapd/releases/2.1.0
[2.1.1]: https://github.com/scrapd/scrapd/releases/2.1.1
[3.0.0]: https://github.com/scrapd/scrapd/releases/3.0.0
[3.0.1]: https://github.com/scrapd/scrapd/releases/3.0.1
[3.0.2]: https://github.com/scrapd/scrapd/releases/3.0.2
[3.0.3]: https://github.com/scrapd/scrapd/releases/3.0.3
[3.0.4]: https://github.com/scrapd/scrapd/releases/3.0.4

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
[#66]: https://github.com/scrapd/scrapd/pull/66
[#84]: https://github.com/scrapd/scrapd/pull/84
[#85]: https://github.com/scrapd/scrapd/pull/85
[#90]: https://github.com/scrapd/scrapd/pull/90
[#116]: https://github.com/scrapd/scrapd/pull/116
[#117]: https://github.com/scrapd/scrapd/pull/117
[#125]: https://github.com/scrapd/scrapd/pull/125
[#132]: https://github.com/scrapd/scrapd/pull/132
[#133]: https://github.com/scrapd/scrapd/pull/133
[#136]: https://github.com/scrapd/scrapd/pull/136
[#137]: https://github.com/scrapd/scrapd/pull/137
[#138]: https://github.com/scrapd/scrapd/pull/138
[#139]: https://github.com/scrapd/scrapd/pull/139
[#140]: https://github.com/scrapd/scrapd/pull/140
[#155]: https://github.com/scrapd/scrapd/pull/155
[#159]: https://github.com/scrapd/scrapd/pull/159
[#163]: https://github.com/scrapd/scrapd/pull/163
[#166]: https://github.com/scrapd/scrapd/pull/166
[#167]: https://github.com/scrapd/scrapd/pull/167
[#169]: https://github.com/scrapd/scrapd/pull/169
[#171]: https://github.com/scrapd/scrapd/pull/171
[#172]: https://github.com/scrapd/scrapd/pull/172
[#178]: https://github.com/scrapd/scrapd/pull/178
[#199]: https://github.com/scrapd/scrapd/pull/199
[#203]: https://github.com/scrapd/scrapd/issues/203
[#204]: https://github.com/scrapd/scrapd/issues/204
[#208]: https://github.com/scrapd/scrapd/pull/208
[#210]: https://github.com/scrapd/scrapd/pull/210
[#214]: https://github.com/scrapd/scrapd/pull/214
[#220]: https://github.com/scrapd/scrapd/pull/220
[#223]: https://github.com/scrapd/scrapd/pull/223
[#224]: https://github.com/scrapd/scrapd/pull/224
[#227]: https://github.com/scrapd/scrapd/pull/227
[#230]: https://github.com/scrapd/scrapd/pull/230
[#234]: https://github.com/scrapd/scrapd/pull/234
