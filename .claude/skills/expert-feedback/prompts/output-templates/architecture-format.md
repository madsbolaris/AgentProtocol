# Architecture & Implementation Plan Format

Use this structure for architecture documents:

```markdown
# Architecture & Implementation Plan: {Title}

**Created:** {date}
**Status:** Ready for Implementation
**Estimated Total Time:** {X-Y weeks/months}
**Type:** Greenfield Architecture

## Executive Summary

{2-3 paragraphs: system purpose, key decisions, high-level approach}

### Goals
- Goal 1
- Goal 2
- Goal 3

### Key Architectural Decisions
1. Decision 1 - {Rationale from expert consensus}
2. Decision 2 - {Rationale from expert consensus}

## Critical Files

**Files to be created:**

- `path/to/component1/main.ext` - {Description}
- `path/to/component2/api.ext` - {Description}
- `path/to/config/settings.ext` - {Description}

---

## System Architecture

### Overview

{Architectural diagram description and component breakdown}

**Architecture Pattern:** {e.g., Microservices, Monolith, Event-driven}

**Key Principles:**
- Principle 1
- Principle 2

### Components

#### {Component Name}

- **Purpose:** {What it does}
- **Technology:** {Stack based on expert recommendations}
  - Language: {e.g., TypeScript, Python}
  - Framework: {e.g., Express, FastAPI}
  - Libraries: {Key dependencies}
- **Responsibilities:** {Bullet list}
- **Interfaces:**
  - Input: {API/data contracts}
  - Output: {API/data contracts}
- **Dependencies:** {Other components}

{Repeat for each component}

---

## Data Architecture

### Data Model

**Entities:**
1. **{Entity}** - {Description}
   - Fields: {List}
   - Relations: {List}

### Storage

- **Type:** {Database type from expert recommendations}
- **Rationale:** {Why this choice}
- **Key Considerations:** {Performance, scaling, consistency}

### Data Flow

1. {Source} → {Process} → {Destination}
2. {Source} → {Process} → {Destination}

---

## API Design

### Endpoints

**Base URL:** `{base-url}`

#### {Endpoint Group}

- `GET /resource` - {Description}
- `POST /resource` - {Description}
- `PUT /resource/:id` - {Description}
- `DELETE /resource/:id` - {Description}

### Authentication

**Method:** {e.g., JWT, OAuth2, API Keys}
**Rationale:** {From security expert recommendations}

---

## Technology Stack

### Core Technologies

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | {tech} | {Expert justification} |
| Backend | {tech} | {Expert justification} |
| Database | {tech} | {Expert justification} |
| Caching | {tech} | {Expert justification} |

### Infrastructure

- **Hosting:** {Platform}
- **CI/CD:** {Tools}
- **Monitoring:** {Tools}

---

## Implementation Plan

### Phase 1: {Name} ({time estimate})

**Goal:** {What this phase achieves}

**Deliverables:**
- Item 1 - {Description}
  - **Complexity:** {Low/Medium/High}
  - **Acceptance Criteria:** {Bullet list}
  - **Dependencies:** {What must be done first}
  - **Risks:** {List with mitigations}

{Repeat for each deliverable}

### Phase 2: {Name} ({time estimate})

{Same structure}

### Phase 3: {Name} ({time estimate})

{Same structure}

---

## Critical Path

Items blocking other work:
1. {Item} (blocks: {dependencies})
2. {Item} (blocks: {dependencies})

## Parallel Work Streams

Can be developed simultaneously:
- **Stream 1:** {Components}
- **Stream 2:** {Components}

---

## Testing Strategy

### Unit Testing
- **Framework:** {Tool}
- **Coverage Target:** {Percentage}
- **Approach:** {Strategy}

### Integration Testing
- **Approach:** {Strategy}
- **Key Points:** {Component interactions to test}

### E2E Testing
- **Framework:** {Tool}
- **Critical Flows:** {List}

### Performance Testing
- **Tools:** {Load testing tools}
- **SLAs:** Response time, throughput, concurrent users
- **Scenarios:** {List}

---

## Deployment Strategy

### Environments
- **Development:** {Setup}
- **Staging:** {Setup}
- **Production:** {Setup}

### Deployment Process
1. {Step}
2. {Step}
3. {Step}

### Rollback Plan
{Strategy for reverting deployments}

---

## Security Considerations

Based on security expert recommendations:
1. {Concern} - {Mitigation}
2. {Concern} - {Mitigation}

---

## Operational Considerations

### Monitoring
- **Metrics:** {List}
- **Alerting:** {Thresholds and notifications}

### Logging
- **Strategy:** {Centralized/distributed}
- **Retention:** {Policy}

### Backup & Recovery
- **Backup Schedule:** {Frequency}
- **Recovery Time:** {RTO}
- **Recovery Point:** {RPO}

---

## Success Metrics

- **Metric 1:** {Target}
- **Metric 2:** {Target}
- **Metric 3:** {Target}

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| {Risk} | {H/M/L} | {H/M/L} | {Strategy} |

---

## Next Steps

1. {Immediate action}
2. {Follow-up action}
3. {Long-term action}
```

## Output Requirements

Return as JSON:
```json
{
  "architecture_markdown": "# Architecture & Implementation Plan...",
  "artifact_type": "architecture",
  "total_phases": 3,
  "estimated_time": "8-12 weeks",
  "critical_path_items": 5,
  "parallel_streams": 3
}
```
