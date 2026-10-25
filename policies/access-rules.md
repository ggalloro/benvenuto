---
title: Access to internal systems
summary: Sensitivity levels, prerequisites, approvals and escalation for system access.
---

# Access to internal systems

Policy owner: Information Security Office · Version 3.2 · Applies to all employees and contractors.

## 1. Sensitivity levels

| Level | Examples | Approval |
|---|---|---|
| Low | Collaboration Suite | None, granted automatically |
| Medium | Source Code Platform, Payments Sandbox | Line manager |
| High | Core Banking Test Environment, Enterprise Data Warehouse | Line manager, logged for audit |

The current list of systems, with their level and prerequisites, is published in the portal (`GET /api/systems`).

## 2. Training prerequisites

2.1. Access to a system is allowed only when **all** of its prerequisite courses are completed. A course that is only booked does not count.

2.2. **No access to core banking environments (test or production) before the Anti-Money Laundering course (AML-101) and the Information Security course (INFOSEC-101) are both completed.**

2.3. Access to systems with customer data (Enterprise Data Warehouse, Payments Sandbox) requires the Privacy and GDPR course (GDPR-101) and INFOSEC-101.

2.4. If a prerequisite is missing, do not file the access request. Book the missing course first (see the Mandatory training policy), then request access once it is completed.

## 3. Approvals

3.1. Medium and high systems require the approval of the employee's line manager. The request stays in status `pending_approval` until the manager decides.

3.2. Employees request access only for themselves, never on behalf of a colleague.

3.3. Each request needs a business justification of at least one sentence.

## 4. Service levels and escalation

4.1. Approvers decide within **2 business days**.

4.2. If a request is still pending after 2 days, the employee may escalate by opening a ticket to the **IT** queue with the request id in the reference field. The IT service desk contacts the approver.

4.3. Do not file a duplicate request for the same system while one is pending.

## 5. Production access

5.1. New hires have no access to production systems during their first 90 days, regardless of training status.

5.2. Credentials are personal. Sharing passwords, tokens or MFA codes is a disciplinary offence.
