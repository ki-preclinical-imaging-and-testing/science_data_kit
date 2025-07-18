# Documentation Maintenance Plan

This document outlines the process for maintaining documentation in the Science Data Kit project.

## Documentation Lifecycle

1. **Creation**: New documentation is created in the appropriate directory
2. **Updates**: Documentation is updated as features change or improve
3. **Deprecation**: Outdated documentation is marked as deprecated
4. **Archiving**: Deprecated documentation is eventually archived or removed

## Maintenance Responsibilities

- **Roadmaps**: Updated as part of the development process following guidelines in [roadmaps/organization.md](roadmaps/organization.md)
- **User Documentation**: Updated when user-facing features change
- **Developer Documentation**: Updated when internal APIs or architecture changes
- **Documentation Index**: Updated when new documentation is added or existing documentation is reorganized

## Minimizing Redundancy

To minimize redundancy and maintenance overhead:

1. **Single Source of Truth**: Each piece of information should exist in only one place
2. **Cross-References**: Use links to reference information in other documents rather than duplicating it
3. **Templating**: Use templates from [roadmaps/templates/](roadmaps/templates/) for consistent documentation
4. **Deprecation Process**: Follow the deprecation process for outdated documentation

## Documentation Review Process

1. **Regular Reviews**: Documentation should be reviewed quarterly
2. **Pre-Release Reviews**: Documentation should be reviewed before each release
3. **User Feedback**: Documentation should be updated based on user feedback

## Documentation Tools

- **Markdown Linting**: Use markdown linting tools to ensure consistent formatting
- **Link Checking**: Regularly check for broken links
- **Automated Testing**: Include documentation checks in CI/CD pipelines

## Deprecation Process

When documentation becomes outdated or superseded by newer documentation:

1. **Mark as Deprecated**: Add a prominent deprecation notice at the top of the document:
   ```markdown
   > **DEPRECATED**: This document is maintained for historical reference only and is no longer actively updated. Please refer to the [new document](path/to/new/document.md) for current information.
   ```

2. **Update References**: Update any references to the deprecated document to point to the new document

3. **Archive Decision**: Decide whether to:
   - Keep the document with the deprecation notice for historical reference
   - Move the document to an archive directory
   - Remove the document entirely (only if its content is completely irrelevant or misleading)

## Documentation Directory Structure

The documentation is organized into the following directories:

- **[roadmaps/](roadmaps/)** - Project roadmaps and development plans
  - **[active/](roadmaps/active/)** - Currently active roadmaps
  - **[future/](roadmaps/future/)** - Planned future roadmaps
  - **[archive/](roadmaps/archive/)** - Completed roadmaps
  - **[templates/](roadmaps/templates/)** - Templates for creating new roadmaps
- **[architecture/](architecture/)** - System architecture documentation
- **[guides/](guides/)** - User and developer guides
- **[api/](api/)** - API documentation
- **[tutorials/](tutorials/)** - Step-by-step tutorials
- **[troubleshooting/](troubleshooting/)** - Common issues and solutions
- **[workshop/](workshop/)** - Workshop materials

## Documentation Standards

All documentation should follow these standards:

1. **Use Markdown**: All documentation should be written in Markdown format
2. **Clear Headings**: Use descriptive headings with proper hierarchy (# for title, ## for sections, etc.)
3. **Code Formatting**: Use code blocks with language specification for code examples
4. **Links**: Use relative links to reference other documents within the repository
5. **Images**: Store images in an `images/` directory within the relevant documentation directory
6. **Versioning**: Include version information when appropriate
7. **Dates**: Include last updated dates for time-sensitive information

## Implementation Plan

The documentation maintenance plan is being implemented in three phases:

### Phase 1: Immediate Updates (Completed)
- Update `docs/README.md` with the new structure
- Add deprecation notices to legacy files
- Update the "Current Development Status" section in the main README.md

### Phase 2: Documentation Organization (In Progress)
- Create the comprehensive documentation index (`docs/index.md`)
- Implement the documentation maintenance plan (`docs/maintenance.md`)
- Ensure all documentation directories have appropriate README.md files

### Phase 3: Long-term Strategy
- Gradually migrate any remaining valuable content from legacy files to the appropriate location in the new structure
- Eventually archive the legacy files in a `docs/legacy/` directory
- Implement automated documentation checks in CI/CD pipelines