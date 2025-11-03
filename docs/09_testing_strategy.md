# 09_testing_strategy.md

# Testing Strategy for Smart HR Bot

## Overview

Currently, the Smart HR Bot project does not have automated unit tests or integration tests implemented. Testing is performed manually by designated testers based on test cases.

## Testers

The following testers are responsible for creating and executing test cases:

- **Ssanket Shinde** – sanket.shinde@bee-logical.com
- **Vaibhavee Prajapat** – vaibhavee.prajapat@bee-logical.com

## Testing Approach

1. **Manual Testing:**
   - Testers will manually verify each feature and functionality.
   - Testing will follow the test cases documented by the testers.
   - Test cases will include expected inputs, outputs, and behavior.

2. **Feature-Based Testing:**
   - Each new feature or update must be tested manually before merging.
   - Testers will validate user flows, APIs, frontend components, and backend logic.

3. **Bug Reporting and Tracking:**
   - Any defects found during testing must be reported in the issue tracker.
   - Each bug report should include steps to reproduce, expected behavior, actual behavior, screenshots (if applicable), and severity level.

4. **Regression Testing:**
   - Before a major release, testers will manually verify all existing functionalities to ensure that new changes do not break existing behavior.

5. **Environment:**
   - Testing should be done in the **development or staging environment**.
   - Ensure that environment variables and test data are configured properly for testing.

## Future Plans

- Implementation of **automated unit tests, integration tests, and end-to-end tests** is planned for future development cycles.
- Once automated testing is in place, this strategy will be updated accordingly.

---

**All contributions must be tested manually according to the above strategy before merging.**

