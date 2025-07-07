# Science Data Kit Roadmap Templates

This directory contains templates for creating various types of documents related to the Science Data Kit roadmaps.

## Available Templates

### 1. Roadmap Template (`roadmap_template.md`)

This template is used for creating new roadmap files. It includes sections for:

- Overview
- Version History
- Completed Tasks
- Current Status
- Next Steps
- Implementation Plan
- Conclusion

**When to use**: When creating a new roadmap for a component or phase of the Science Data Kit project.

**Usage**:
1. Copy the template to the appropriate location in the `docs/roadmaps/active/` directory
2. Rename the file according to the naming conventions in `docs/roadmaps/organization.md`
3. Fill in the template with the relevant information
4. Update `docs/roadmaps/index.md` to include the new roadmap

### 2. Testing Status Template (`testing_status_template.md`)

This template is used for creating testing status reports for roadmaps. It includes sections for:

- Testing Summary
- Testing Results (with subsections for different types of testing)
- Next Steps
- Recommendations

**When to use**: When conducting testing activities for a roadmap, particularly at these strategic points:
- After completing 3-5 implementation tasks in a roadmap
- Before transitioning between roadmap phases
- When preparing features for user testing or feedback collection
- When implementing core architectural components or patterns
- Before considering major components "complete"

**Usage**:
1. Copy the template to the appropriate location (typically alongside the roadmap file it relates to)
2. Rename the file to indicate the roadmap and date (e.g., `testing_status_RepoReorg_2024-07-15.md`)
3. Fill in the template with the testing results
4. Reference the testing status report in the roadmap's "Current Status" section
5. Update the "Testing and Quality Status" section in `docs/roadmaps/index.md`

## Template Maintenance

When updating these templates:

1. Ensure changes are backward compatible or provide migration guidance
2. Update this README.md file to reflect any changes to the templates
3. Consider updating any references to the templates in other files, such as:
   - `docs/roadmaps/organization.md`
   - `docs/roadmaps/active/roadmap_memo.md`
   - `docs/roadmaps/prompts.md`

## Integration with Testing Workflow

The testing status template is designed to work with the testing prompts (#17-24) in `docs/roadmaps/prompts.md`. For guidance on selecting appropriate testing prompts, start with prompt #21 (Pre-Review Code Analysis) to assess the current state and get recommendations for additional validation.