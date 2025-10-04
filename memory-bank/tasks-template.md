# Task Breakdown Template

**Task ID**: [TASK-XXX]  
**Plan**: [PLAN-XXX]  
**Feature**: [FEATURE-XXX]  
**Created**: [DATE]  
**Status**: Draft/Review/Approved

## Task Overview
**Objective**: [Clear, specific objective]  
**Estimated Effort**: [X hours/days]  
**Priority**: [High/Medium/Low]  
**Complexity**: [Level 1/2/3/4]

## Prerequisites
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]
- [ ] [Prerequisite 3]

## Task Categories

### Setup Tasks
- [ ] [Setup task 1]
- [ ] [Setup task 2]
- [ ] [Setup task 3]

### Test Tasks (TDD - Test First)
- [ ] [Test task 1]
- [ ] [Test task 2]
- [ ] [Test task 3]

### Core Implementation Tasks
- [ ] [Core task 1]
- [ ] [Core task 2]
- [ ] [Core task 3]

### Integration Tasks
- [ ] [Integration task 1]
- [ ] [Integration task 2]
- [ ] [Integration task 3]

### Polish Tasks
- [ ] [Polish task 1]
- [ ] [Polish task 2]
- [ ] [Polish task 3]

## Parallelizable Tasks
Tasks that can be worked on simultaneously:

### Group A (Independent)
- [ ] [Task A1]
- [ ] [Task A2]

### Group B (Independent)
- [ ] [Task B1]
- [ ] [Task B2]

### Group C (Sequential)
- [ ] [Task C1] → [Task C2] → [Task C3]

## Implementation Sequence

### Step 1: Environment Setup
1. [ ] [Setup step 1]
2. [ ] [Setup step 2]
3. [ ] [Setup step 3]

**Validation**: [How to verify setup is complete]

### Step 2: Test Development (TDD)
1. [ ] [Test step 1]
2. [ ] [Test step 2]
3. [ ] [Test step 3]

**Validation**: [How to verify tests are complete]

### Step 3: Core Implementation
1. [ ] [Implementation step 1]
2. [ ] [Implementation step 2]
3. [ ] [Implementation step 3]

**Validation**: [How to verify implementation is complete]

### Step 4: Integration
1. [ ] [Integration step 1]
2. [ ] [Integration step 2]
3. [ ] [Integration step 3]

**Validation**: [How to verify integration is complete]

### Step 5: Testing & Validation
1. [ ] [Testing step 1]
2. [ ] [Testing step 2]
3. [ ] [Testing step 3]

**Validation**: [How to verify testing is complete]

### Step 6: Polish & Documentation
1. [ ] [Polish step 1]
2. [ ] [Polish step 2]
3. [ ] [Polish step 3]

**Validation**: [How to verify polish is complete]

## Definition of Done

### Code Quality
- [ ] All code follows project standards
- [ ] Code is properly commented
- [ ] No linting errors
- [ ] Code review completed

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Contract tests written and passing (if applicable)
- [ ] Test coverage meets requirements

### Documentation
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Memory Bank files updated
- [ ] README updated (if applicable)

### Integration
- [ ] Feature works with existing system
- [ ] No breaking changes introduced
- [ ] Performance requirements met
- [ ] Security requirements met

## Dependencies
**Internal Dependencies**:
- [Dependency 1]
- [Dependency 2]

**External Dependencies**:
- [External dependency 1]
- [External dependency 2]

## Risks & Mitigations
- **Risk 1**: [Description] → **Mitigation**: [Strategy]
- **Risk 2**: [Description] → **Mitigation**: [Strategy]

## Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## Testing Strategy

### Unit Tests
```typescript
// Example test structure
describe('[Component Name]', () => {
  it('should [expected behavior]', () => {
    // Test implementation
  });
});
```

### Integration Tests
```typescript
// Example integration test
describe('[Integration Name]', () => {
  it('should [expected integration behavior]', () => {
    // Integration test implementation
  });
});
```

### Contract Tests
```typescript
// Example contract test
describe('[API Contract]', () => {
  it('should [expected contract behavior]', () => {
    // Contract test implementation
  });
});
```

## Performance Considerations
- [Performance consideration 1]
- [Performance consideration 2]

## Security Considerations
- [Security consideration 1]
- [Security consideration 2]

## Memory Bank Integration

### Files to Update
- [ ] `memory-bank/tasks.md`
- [ ] `memory-bank/activeContext.md`
- [ ] `memory-bank/progress.md`
- [ ] `memory-bank/creative/[feature-name].md` (if creative phase required)

### Context Preservation
- [ ] Task state preserved
- [ ] Decision history captured
- [ ] Learning documented

## Review Checklist
- [ ] Task breakdown is complete
- [ ] Implementation sequence is logical
- [ ] Dependencies are identified
- [ ] Risks are assessed and mitigated
- [ ] Testing strategy is comprehensive
- [ ] Definition of done is clear
- [ ] Memory Bank integration planned

---

**Next Steps**:
- [ ] Begin implementation following TDD approach
- [ ] Update Memory Bank files as work progresses
- [ ] Document decisions and learnings
