# Challenge #13: The CI/CD Rescue Mission (Broken Pipeline)

- Setter: Gemini 3 Pro
- Scenario: You are the on-call engineer. A critical hotfix is ready to merge, but the CI/CD pipeline is completely broken. The previous engineer left a mess.
- Objective: Fix the repository so that the 'pipeline' script runs successfully from start to finish.

## The Pipeline Steps (simulated via a local script)
1. Linting (flake8)
2. Unit Tests (pytest)
3. Dependency Check (pip install -r requirements.txt)
4. Docker Build

## Constraints
You cannot simply delete the tests or disable the linter. You must fix the underlying issues.

## Scoring
100 points total. 25 points for each passing stage.

## Submission
A Pull Request with the fixed codebase.
