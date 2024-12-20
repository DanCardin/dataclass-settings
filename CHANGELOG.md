# Changelog

## 0.7

### 0.7.0
* feat: Abstract Loader "state" from the loader. This enables supplying state
  once at load-time in order to customize load-wide settings.

## 0.6

### 0.6.1
* fix: Bad field reference for pydantic inspection.

### 0.6.0

* feat: Adopt type-lens library to better handle 3.12-style annotations which
  were incorrectly identified by typing_inspect
- fix: Ignore `ClassVar` annotated fields

## 0.5

### 0.5.2

* fix: Mapping error for loaders that return types other than strings.

### 0.5.1

* fix: Closure error in nested msgspec implementation.
