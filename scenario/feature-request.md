# Feature request: engineering change impact check

## Request

Engineering leaders want a faster way to understand whether a proposed software change may affect other components or planned releases. Today a lead reads the change request, searches the issue tracker manually, asks several teams, and produces a short review note.

## Desired experience

When a change request is submitted, the team should receive:

- A concise interpretation of the requested change
- Related issues and known dependencies
- Potential release or safety impact
- Questions that must be answered before implementation
- A proposed owner and next action

## Constraints

- The first pass must not modify any issue.
- Any issue creation or update requires human approval.
- The output must cite the issue keys and source documents used.
- Sensitive program details must stay within approved systems.

## Open details

The requester has not defined the project key, risk taxonomy, release naming convention, or approval owner.
