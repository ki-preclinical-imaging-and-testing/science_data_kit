# Effective Prompts for Working with Science Data Kit Roadmaps

This document provides a collection of prompt templates for working with the Science Data Kit roadmaps. These prompts are designed to help you effectively navigate, analyze, update, and implement tasks from the roadmaps.

## Introduction

The Science Data Kit roadmaps serve as comprehensive project plans that guide development efforts. These prompt templates are designed to facilitate collaboration with AI assistants in various roadmap-related activities, from understanding roadmap structure to implementing tasks and updating roadmaps with progress.

A key feature of these prompts is their support for iterative development cycles, where you can:
1. Analyze roadmaps to identify tasks to be completed
2. Implement those tasks with AI assistance
3. Document progress in updated roadmap versions
4. Continue the cycle until roadmap completion

This approach has proven particularly effective for systematic progress through complex development plans. The prompts are organized by function, allowing you to select the most appropriate template for your current needs in the roadmap lifecycle.

## Understanding Roadmaps

### 1. Understanding the Roadmap Structure

```
I'd like to understand the Science Data Kit roadmap structure. Please analyze the files in docs/roadmaps/, particularly index.md and organization.md, and explain:
1. How the roadmaps are organized
2. The current active roadmaps and their status
3. The naming conventions used
4. How roadmaps progress through their lifecycle
```

### 2. Analyzing a Specific Roadmap

```
I'd like to analyze the [ROADMAP_NAME] roadmap in docs/roadmaps/active/. Please:
1. Summarize the key goals and components
2. Identify the current status of tasks
3. Highlight any dependencies or blockers
4. Suggest potential next steps based on the current status
5. Identify any areas that might need updating or clarification
```

### 3. Tracking Progress Across Roadmaps

```
Please analyze the active roadmaps in docs/roadmaps/active/ and provide:
1. A summary of overall progress across all roadmaps
2. Identification of any dependencies between roadmaps
3. Highlight of any potential bottlenecks or blockers
4. Suggestions for prioritization based on current status
5. A visual representation of progress (e.g., a table showing completion percentages)
```

## Implementing Roadmap Tasks

### 4. Iterative Task Implementation

```
Complete as many tasks as you can from the [ROADMAP_NAME] in docs/roadmaps/active/. For each task:
1. Analyze the requirements and dependencies
2. Implement the necessary changes
3. Test your implementation
4. Update the task status in the roadmap
5. Document any challenges or decisions made

After completing the tasks, create a new version of the roadmap with updated statuses and next steps.
```

### 5. Focused Task Implementation

```
Implement the following specific task(s) from [ROADMAP_NAME] in docs/roadmaps/active/:
- [TASK_DESCRIPTION]

For each task:
1. Analyze the requirements and context
2. Design a solution approach
3. Implement the necessary changes
4. Test your implementation
5. Document your implementation details

After completion, update the task status in the roadmap and create a new version if appropriate.
```

### 6. Development Cycle Execution

```
Complete a full development cycle for [ROADMAP_NAME] in docs/roadmaps/active/:

1. Identify the highest priority tasks that can be completed in this cycle
2. Implement these tasks, making all necessary code changes
3. Test your implementations thoroughly
4. Update the roadmap with completed tasks and any new insights
5. Create a new version of the roadmap (roadmap_[COMPONENT]_[NEXT_VERSION].md) with:
   - Updated task statuses
   - Documentation of implementation details
   - Revised next steps
   - Any new tasks identified during implementation

Reference docs/roadmaps/organization.md and docs/roadmaps/active/roadmap_memo.md for guidance on roadmap updates.
```

## Updating Roadmaps

### 7. Creating a New Roadmap Version

```
Create a new version of the [ROADMAP_NAME] roadmap based on recent progress:

1. Review the current roadmap in docs/roadmaps/active/
2. Create a new file with the next version number (e.g., if current is roadmap_component_01.md, create roadmap_component_02.md)
3. Update all task statuses based on completed work
4. Add implementation details for completed tasks
5. Revise the "Current Status" and "Next Steps" sections
6. Add any new tasks identified during implementation
7. Update docs/roadmaps/index.md to reference the new roadmap version

Follow the guidelines in docs/roadmaps/active/roadmap_memo.md for roadmap updates.
```

### 8. Roadmap Phase Transition

```
Prepare for a transition from [CURRENT_PHASE] to [NEXT_PHASE]:

1. Review all remaining tasks in the current phase roadmap
2. Identify which tasks should be completed before phase transition
3. Implement high-priority remaining tasks
4. Create a new roadmap file for the next phase following the naming convention in docs/roadmaps/organization.md
5. Move appropriate remaining tasks to the new phase roadmap
6. Add any low-priority remaining tasks to docs/roadmaps/active/roadmap_later.md
7. Update docs/roadmaps/index.md to reflect the phase transition

Follow the guidelines in docs/roadmaps/active/roadmap_memo.md for phase transitions.
```

### 9. Comprehensive Roadmap Update

```
Complete as many tasks as you can from the latest [ROADMAP_NAME] in docs/roadmaps/active/. You will find more context in docs/roadmaps/index.md.

At the end of this development cycle:
1. Report the status in a new roadmap file with the next version number
2. Update all task statuses and add implementation details
3. Revise the "Current Status" and "Next Steps" sections
4. Add any new tasks identified during implementation
5. Update docs/roadmaps/index.md to reference the new roadmap version

Use docs/roadmaps/active/roadmap_memo.md for guidance on roadmap updates.
```

## Advanced Roadmap Operations

### 10. Roadmap Integration Analysis

```
Please analyze how the active roadmaps in docs/roadmaps/active/ integrate with each other:
1. Identify any overlapping tasks or dependencies between roadmaps
2. Suggest potential consolidations or separations of roadmaps
3. Analyze how the roadmaps align with the overall project goals in index.md
4. Recommend any adjustments to improve integration and coherence
```

### 11. Roadmap Archiving Preparation

```
The [ROADMAP_NAME] is nearing completion. Please help me prepare for archiving by:
1. Implementing any remaining high-priority tasks
2. Reviewing the remaining tasks and suggesting how to handle them
3. Drafting a summary of achievements for the roadmap
4. Identifying any lessons learned that should be documented
5. Moving the roadmap to docs/roadmaps/archive/
6. Adding remaining tasks to docs/roadmaps/active/roadmap_later.md
7. Updating docs/roadmaps/index.md to reflect the archiving

Follow the guidelines in docs/roadmaps/active/roadmap_memo.md for archiving roadmaps.
```

### 12. Knowledge Graph Integration Planning

```
I want to ensure our roadmaps are optimally structured for the Knowledge Graph Documentation System. Please:
1. Analyze the current roadmap structure and format
2. Identify any elements that could be enhanced for better knowledge graph integration
3. Suggest any additional metadata or tagging that could improve AI navigation
4. Recommend any structural changes that would make the roadmaps more machine-readable
5. Draft example enhancements for a sample roadmap section
```

## Testing and Quality Assurance

### 17. Manual Testing Preparation

```
Based on the recent implementations in [ROADMAP_NAME], create a comprehensive manual testing checklist:
1. Identify all new features and functionality implemented
2. Create step-by-step testing procedures for each feature
3. Generate test data or scenarios needed for validation
4. Identify potential edge cases and error conditions to test
5. Create a checklist format that can be used for manual validation
6. Include both functional testing and user experience validation

Output the checklist in a format suitable for manual testing by a human reviewer.
```

### 18. Automated Testing Implementation

```
Review the recent implementations from [ROADMAP_NAME] and create automated tests:
1. Identify components that need unit test coverage
2. Create unit tests for new functionality
3. Implement integration tests for component interactions
4. Add end-to-end tests for complete workflows
5. Update existing tests that may be affected by changes
6. Ensure all tests pass and provide meaningful coverage

Document any testing challenges or areas that require manual validation.
```

### 19. Code Quality Review

```
Perform a comprehensive code quality review of implementations from [ROADMAP_NAME]:
1. Review code for adherence to project standards and patterns
2. Check documentation completeness (docstrings, comments, README updates)
3. Validate error handling and edge case coverage
4. Review performance implications of new code
5. Check for security considerations
6. Validate integration with existing systems
7. Identify any code smells or areas for refactoring

Provide a summary of findings and recommendations for improvements.
```

### 20. Feature Validation Workflow

```
Create a comprehensive validation workflow for features implemented in [ROADMAP_NAME]:
1. Generate realistic test scenarios based on intended use cases
2. Create sample data that exercises new functionality
3. Document expected vs. actual behavior for each test case
4. Identify any usability issues or areas for improvement
5. Test integration points with existing features
6. Validate error messages and handling are user-friendly
7. Check performance under realistic usage conditions

Prepare a validation report suitable for stakeholder review.
```

### 21. Pre-Review Code Analysis

```
Prepare for human code review by analyzing recent implementations from [ROADMAP_NAME]:
1. Summarize all changes made during the implementation cycle
2. Highlight any significant architectural decisions or trade-offs
3. Identify areas that may benefit from human review or input
4. Flag any experimental or uncertain implementations
5. Document any assumptions made during implementation
6. Create a focused review agenda with specific questions for human reviewer

This analysis should help focus the human review on the most important aspects.
```

### 22. Workshop Feature Testing

```
Prepare the recent implementations from [ROADMAP_NAME] for workshop/user testing:
1. Create user-friendly documentation for new features
2. Generate realistic usage scenarios for workshop participants
3. Identify potential user confusion points or UI/UX issues
4. Create a feedback collection framework for user input
5. Prepare troubleshooting guides for common issues
6. Design exercises that showcase new functionality effectively

Focus on making the features accessible to non-technical users for feedback.
```

### 23. Performance and Scalability Review

```
Conduct a performance review of implementations from [ROADMAP_NAME]:
1. Identify performance-critical components in new implementations
2. Test with larger datasets or more complex scenarios
3. Profile memory usage and execution time for key operations
4. Check for potential bottlenecks or scalability issues
5. Validate that performance optimizations are working as expected
6. Compare performance before and after implementations
7. Recommend any performance improvements or monitoring

Document findings and provide specific metrics where possible.
```

### 24. Integration Testing with Real Data

```
Test recent implementations from [ROADMAP_NAME] with realistic scientific data:
1. Identify appropriate real-world datasets for testing
2. Test data ingestion and processing workflows end-to-end
3. Validate that new features work with actual scientific data formats
4. Check for any data quality or format issues not caught in unit tests
5. Test performance with realistic data volumes
6. Validate output quality and scientific accuracy
7. Document any issues or limitations discovered

Focus on ensuring the implementations work in real scientific contexts.
```

## Complete Development Cycle

### 25. Full Roadmap Implementation Cycle

```
Complete a full implementation cycle for the latest [ROADMAP_NAME] in docs/roadmaps/active/:

1. Analyze the current roadmap to identify high-priority tasks
2. Implement as many tasks as possible, focusing on high-priority items
3. Test all implementations thoroughly
4. Document implementation details, challenges, and decisions
5. Create a new version of the roadmap with:
   - Updated task statuses
   - Implementation details for completed tasks
   - Revised "Current Status" and "Next Steps" sections
   - Any new tasks identified during implementation
6. Update docs/roadmaps/index.md to reference the new roadmap version
7. If appropriate, prepare for phase transition or archiving

Follow all guidelines in docs/roadmaps/organization.md and docs/roadmaps/active/roadmap_memo.md.
```

### 26. Continuous Roadmap Development

```
Continue the development of [ROADMAP_NAME] from where we left off:

1. Review our previous work and the current status of the roadmap
2. Identify the next set of tasks to implement based on priority
3. Implement these tasks, making all necessary code changes
4. Test your implementations thoroughly
5. Update the roadmap with completed tasks and create a new version
6. Plan the next development cycle

This is an ongoing process - we'll continue to iterate through development cycles until the roadmap is complete.
```

### 27. Roadmap-Driven Project Development

```
Let's use the roadmap as our guide for project development. Starting with [ROADMAP_NAME]:

1. Analyze the roadmap to understand the overall goals and components
2. Identify the current highest priority tasks
3. Implement these tasks, making all necessary code changes
4. Test your implementations thoroughly
5. Update the roadmap with completed tasks
6. Create a new version of the roadmap with updated statuses and next steps
7. Repeat this process in subsequent sessions until the roadmap is complete

This approach ensures we're systematically working through the project plan as defined in the roadmap.
```

### 28. Phase-Specific Roadmap Implementation

```
Complete as many tasks as you can from the latest docs/roadmaps/active/roadmap_[COMPONENT]Phase[N]_??.md. You will find more context in docs/roadmaps/index.md.

At the end of this development cycle, report the status in a new docs/roadmaps/active/roadmap_[COMPONENT]Phase[N]_[NEXT_VERSION].md. Use docs/roadmaps/active/roadmap_memo.md for guidance, and update docs/roadmaps/index.md accordingly.

Finally, commit and push all updates.
```

These prompts are designed to help you work through different aspects of roadmap development, management, and implementation. You can customize them further based on your specific needs for each development cycle.
