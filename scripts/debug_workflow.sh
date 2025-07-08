#!/bin/bash

# SciDK Debugging Workflow with GitHub Issues Integration
# Usage: ./scripts/debug_workflow.sh "component" "issue description"

COMPONENT="$1"
ISSUE_DESCRIPTION="$2"

if [ -z "$COMPONENT" ] || [ -z "$ISSUE_DESCRIPTION" ]; then
    echo "Usage: $0 <component> <issue_description>"
    echo "Example: $0 'chat-interface' 'Users report chat history not saving'"
    exit 1
fi

echo "🐛 Starting debugging workflow for: $COMPONENT"

# Source the helper functions
source scripts/issue_helpers.sh

# Create debugging issue
echo "📝 Creating debugging issue..."
create_debug_issue "$ISSUE_DESCRIPTION" "$COMPONENT" "$ISSUE_DESCRIPTION"

# Get the issue number from the last created issue
ISSUE_NUMBER=$(gh issue list --author @me --limit 1 --json number --jq '.[0].number')

echo "✅ Created debugging issue #$ISSUE_NUMBER"

# Provide next steps
echo ""
echo "🔧 Next steps:"
echo "1. Start working on the issue: gh issue view $ISSUE_NUMBER"
echo "2. Reference the issue in commits: git commit -m 'Fix chat history bug - progress on #$ISSUE_NUMBER'"
echo "3. Use testing prompts from docs/roadmaps/prompts.md"
echo "4. Close when complete: gh issue close $ISSUE_NUMBER"
echo ""
echo "💡 Debugging prompts to consider:"
echo "   - Prompt #19: Code Quality Review"
echo "   - Prompt #21: Pre-Review Code Analysis"
echo "   - Prompt #24: Integration Testing with Real Data"