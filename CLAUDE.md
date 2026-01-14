# Starward Project Instructions

## Git Commits
- Commit contextually and atomically (group related changes)
- Use short, human-readable commit messages
- Do not add Co-Authored-By attribution

## Workflow
- Continue with tasks without asking questions unless truly blocked
- Build and restart servers after making changes
- Deploy website after committing documentation changes

## Code Style
- Use color values instead of opacity for muted/dimmed text
- Remove unused DOM elements from layout entirely (not just display: none)
- Professional, clean styling without unnecessary embellishments

## Documentation
- This is an educational astronomy toolkit - content should teach
- Test suite serves dual purpose: validation and education
- Use professional docstrings explaining astronomical concepts
- Blog posts should document releases with examples

## Project Structure
- All documentation in `docs/` folder (no separate dev folders)
- Development docs in `docs/development/`
- Website/Docusaurus config in `website/`

## Testing
- Use Allure for test reporting with step annotations
- Educational comments in test files explaining astronomical concepts
- Run full test suite after changes: `pytest`
- Generate reports with: `make report`

## Deployment
- PyPI: `python -m twine upload dist/*`
- Website: `cd website && USE_SSH=true npm run deploy`
- Tag releases: `git tag -a vX.Y.Z -m "message"`
