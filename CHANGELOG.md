# Changelog

All notable changes to DBNT will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial DBNT/DBGT protocol implementation
- Signal detection (positive/negative/neutral)
- Weighted encoding (success 1.5x, failure 1.0x)
- Dissonance calculator
- Claude Code adapter
- Generic file-based adapter
- CLI with detect, success, failure, dissonance commands

## [0.1.0] - 2026-01-06

### Added
- Core signal detection module
- Rule encoding (success/failure categories)
- Dissonance monitoring with 60/40 target
- Claude Code hook integration
- CLI interface (`dbnt` command)
- 17 passing tests

### Philosophy
- Success signals weight 1.5x over failure (inverted from typical)
- Target: 60% success rules, 40% failure rules
- No anger required - mild feedback works
- The Ralph Wiggum Problem: knowing 100 ways to fail doesn't teach you how to succeed
