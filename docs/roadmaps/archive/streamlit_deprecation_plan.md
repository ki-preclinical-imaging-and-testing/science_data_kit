# Streamlit Deprecation Plan for Science Data Kit

## Overview
This document outlines the plan for deprecating the Streamlit implementation of the Science Data Kit and transitioning users to the Flask implementation. The plan includes a timeline, communication strategy, transition helpers, and technical steps for removing Streamlit dependencies from the codebase.

## Timeline

### Phase 1: Preparation (2 weeks)
- Complete documentation updates for Flask implementation
- Create transition guides for users
- Implement URL redirects from Streamlit routes to Flask routes
- Add deprecation notices to Streamlit UI
- Prepare email templates for user communication

### Phase 2: Soft Deprecation (4 weeks)
- Release dual-mode version with both Streamlit and Flask implementations
- Default to Flask implementation for new installations
- Provide prominent notices in Streamlit UI about upcoming deprecation
- Send email notifications to registered users
- Collect feedback on Flask implementation
- Address any critical issues reported by users

### Phase 3: Hard Deprecation (2 weeks)
- Release version with Streamlit as opt-in only
- Require explicit configuration to enable Streamlit
- Send final deprecation notices to users
- Provide extended support for enterprise users if needed

### Phase 4: Removal (2 weeks)
- Release version without Streamlit implementation
- Remove all Streamlit dependencies from codebase
- Archive Streamlit-specific documentation
- Send confirmation of completion to users

## Communication Strategy

### User Notifications
- In-app notifications in both Streamlit and Flask UIs
- Email notifications to registered users at each phase
- Blog post explaining the transition and benefits
- Social media announcements
- Updates to documentation and website

### Messaging
- Focus on benefits of Flask implementation:
  - Improved performance (30% faster page loads)
  - Enhanced UI capabilities (HTMX, Alpine.js)
  - Better deployment options
  - Improved accessibility (WCAG 2.1 compliance)
  - Responsive design for all screen sizes
- Provide clear timeline for deprecation
- Emphasize continued support during transition
- Highlight feature parity between implementations

### Support Channels
- Dedicated support email for transition issues
- GitHub issues for bug reports
- Community forum for discussion
- Office hours for direct assistance

## Transition Helpers

### Documentation
- Comprehensive migration guide
- Feature mapping between Streamlit and Flask implementations
- Updated installation and configuration guides
- Troubleshooting guide for common issues

### Technical Helpers
- URL redirects from Streamlit routes to Flask routes
- Configuration migration tool
- Data export/import utilities if needed
- Script to check for Streamlit-specific customizations

### User Experience
- Consistent UI elements between implementations
- Similar navigation patterns
- Guided tours of new Flask UI
- Feature flags for gradual transition

## Technical Implementation

### Dependency Removal
1. Identify all Streamlit dependencies in requirements.txt
2. Create separate requirements files for Flask-only installation
3. Update setup.py to make Streamlit optional
4. Create migration script to update user environments

### Code Cleanup
1. Identify all Streamlit-specific code:
   - Import statements
   - Render functions
   - Streamlit-specific UI components
   - Streamlit session state usage
2. Remove or refactor Streamlit-specific code
3. Update tests to remove Streamlit dependencies
4. Update CI/CD pipelines to focus on Flask implementation

### Configuration Changes
1. Update configuration files to remove Streamlit options
2. Create migration path for user configurations
3. Update documentation for configuration changes
4. Provide validation tools for configuration files

## Success Metrics

### User Adoption
- Percentage of users migrated to Flask implementation
- Number of support requests related to transition
- User satisfaction surveys

### Technical Success
- Reduced codebase size after Streamlit removal
- Improved test coverage
- Reduced dependency count
- Improved performance metrics

### Timeline Adherence
- Completion of each phase within planned timeframe
- Minimal delays in overall deprecation process
- Timely resolution of critical issues

## Conclusion
This deprecation plan provides a structured approach to transitioning from Streamlit to Flask as the primary UI framework for the Science Data Kit. By following this plan, we can ensure a smooth transition for users while reducing codebase complexity and improving maintainability.