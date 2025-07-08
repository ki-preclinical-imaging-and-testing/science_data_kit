#!/bin/bash

# Helper functions for GitHub issue management in SciDK development

# Create issue for roadmap task
create_roadmap_issue() {
    local title="$1"
    local roadmap_file="$2"
    local description="$3"
    local component="$4"
    
    gh issue create \
        --title "Roadmap Task: $title" \
        --body "**Roadmap**: $roadmap_file
**Component**: $component

**Description**: $description

**Checklist**:
- [ ] Analyze requirements
- [ ] Implement solution
- [ ] Test implementation
- [ ] Update roadmap status
- [ ] Update documentation

*Created from roadmap-driven development workflow*" \
        --label "roadmap" \
        --label "roadmap-$component" \
        --assignee @me
}

# Create debugging issue
create_debug_issue() {
    local title="$1"
    local component="$2"
    local error_description="$3"
    
    gh issue create \
        --title "Debug: $title" \
        --body "**Component**: $component

**Error Description**: 
$error_description

**Debugging Checklist**:
- [ ] Reproduce the issue
- [ ] Identify root cause
- [ ] Implement fix
- [ ] Test fix
- [ ] Update documentation if needed

**Testing Requirements**:
- [ ] Use prompt #19 (Code Quality Review)
- [ ] Use prompt #24 (Integration Testing with Real Data)
- [ ] Manual testing if UI-related

*Created for debugging cycle*" \
        --label "bug" \
        --label "debugging" \
        --label "$component" \
        --assignee @me
}

# Create testing issue
create_testing_issue() {
    local component="$1"
    local testing_type="$2"
    local prompt_number="$3"
    
    gh issue create \
        --title "Testing: $component - $testing_type" \
        --body "**Component**: $component
**Testing Type**: $testing_type
**Prompt Reference**: #$prompt_number from docs/roadmaps/prompts.md

**Testing Checklist**:
- [ ] Generate testing checklist using prompt #$prompt_number
- [ ] Execute testing procedures
- [ ] Document results
- [ ] Create follow-up issues for any problems found
- [ ] Update roadmap with testing status

*Created for systematic testing cycle*" \
        --label "testing" \
        --label "$testing_type" \
        --label "$component" \
        --assignee @me
}

# Update issue with roadmap progress
update_issue_progress() {
    local issue_number="$1"
    local roadmap_file="$2"
    local progress_description="$3"
    
    gh issue comment "$issue_number" --body "📋 **Roadmap Progress Update**

**Roadmap File**: $roadmap_file
**Progress**: $progress_description
**Timestamp**: $(date -Iseconds)

**Recent Changes**:
- Updated roadmap status
- Implementation progress documented
- Ready for next development cycle

*This update reflects progress in the systematic roadmap development workflow.*"
}

# Close issue with completion summary
close_issue_complete() {
    local issue_number="$1"
    local roadmap_file="$2"
    local completion_summary="$3"
    
    gh issue comment "$issue_number" --body "✅ **Task Completed**

**Final Status**: Complete
**Roadmap**: $roadmap_file
**Summary**: $completion_summary
**Completed**: $(date -Iseconds)

This issue has been resolved and the roadmap has been updated accordingly."
    
    gh issue close "$issue_number"
}

# List roadmap-related issues
list_roadmap_issues() {
    echo "🗂️  Active Roadmap Issues:"
    gh issue list --label "roadmap" --state open
    
    echo ""
    echo "🐛 Active Debugging Issues:"
    gh issue list --label "debugging" --state open
    
    echo ""
    echo "🧪 Active Testing Issues:"
    gh issue list --label "testing" --state open
}

# Export functions for use in terminal
export -f create_roadmap_issue
export -f create_debug_issue
export -f create_testing_issue
export -f update_issue_progress
export -f close_issue_complete
export -f list_roadmap_issues