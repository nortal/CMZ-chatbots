# Requirements

This document outlines the functional and non-functional requirements for the CMZ Chatbots platform.

---

## 1. User Roles

### 1.1 Admin
- Full system access, including managing all user accounts and settings.
- Can add, update, or remove Admins and Zookeepers.
- Can directly update animal chatbot configurations without approval.
- Reviews and approves Zookeeper-submitted knowledge base updates before publishing.

### 1.2 Zookeeper
- Can monitor and review conversations for assigned animals.
- Can submit updates to animal chatbot content and configuration, which require Admin approval before going live.
- Can flag inappropriate or incorrect chatbot responses for review.

### 1.3 Parent
- Can view, filter, and delete all or portions of their child’s conversation history.
- Can download chat histories.
- Can set parental controls such as time limits or blocked topics.

### 1.4 Student
- Can initiate conversations with animal chatbots using their name or nickname.
- Can ask questions, receive responses, and participate in educational follow-ups.
- Can access chat history if parental controls allow.

---

## 2. Authentication & Access Control

- All roles must log in through a secure authentication mechanism.
- Role-based access control (RBAC) must be enforced at the API and UI level.
- QR code login must be available for Students on-site, assigning temporary session tokens.
- All session tokens must expire after a configurable time period.

---

## 3. Conversation Management

- The system must store conversation histories with timestamps and associated user IDs (or nicknames for students).
- All records must include created, modified, deleted timestamps and `softDelete=true/false`.
- Parents must be able to delete entire or partial conversation histories for their children.
- Admins and Zookeepers can review conversation transcripts for quality assurance.
- Parents can add guardrails to conversations. These can only be more restrictive than the zoo guardrails, not less.

---

## 4. Animal Chatbot Configuration

- Admins can directly modify animal chatbot configurations (knowledge base, tone, and behavior).
- Zookeepers can propose changes to chatbot configurations and content.
- All Zookeeper-proposed changes must be routed to an Admin for approval before publishing.
- Each configuration change must be version-controlled and logged with the author and approver.

---

## 5. Content Management

- Zookeepers can add, edit, or delete knowledge base entries in a draft state.
- Admins can approve, reject, or request changes to Zookeeper submissions.
- The system must support rich text, images, and external reference links in the knowledge base.
- Knowledge base entries must be searchable and filterable by animal, date, and keyword.

---

## 6. Reporting & Metrics

- Admins can view platform usage metrics (e.g., number of chats per animal, average response time).
- Reports must be exportable in CSV or PDF format.
- Admins can review flagged responses and conversation trends.

---

## 7. Notifications

- Zookeepers must be notified when their submissions are approved or rejected.
- Admins must be notified when new content changes await approval.
- Parents can optionally receive alerts for flagged or concerning content in their child’s chat.

---

## 8. Compliance & Privacy

- All stored data must comply with applicable privacy regulations (e.g., COPPA for children’s data).
- Personally identifiable information (PII) for children must be protected and stored securely.
- Parents must be able to request complete deletion of their child’s account and all associated data.