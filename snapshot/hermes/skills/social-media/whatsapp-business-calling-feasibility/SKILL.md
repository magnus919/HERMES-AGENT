---
name: whatsapp-business-calling-feasibility
description: Verify whether a requested WhatsApp real-time voice/call workflow is technically possible, what Meta supports today, and how to explain the practical constraints and implementation path.
---

# When to use
Use this when a user asks whether they can talk to an AI over WhatsApp Call, receive or place WhatsApp calls programmatically, or convert an existing chat-based assistant into a WhatsApp voice/calling agent.

# Goal
Quickly determine:
1. Whether WhatsApp real-time calling is supported at all.
2. Whether the current chat/session itself can do the calling (usually no).
3. What architecture is required to make it real.
4. What the most realistic next decision is for the user.

# Procedure
1. Open Meta's WhatsApp Business Platform docs.
   - Start at the WhatsApp overview page.
   - Verify whether a Calling section exists.
2. Open the Calling overview page.
   - Confirm that WhatsApp Business Calling / Cloud API Calling exists.
   - Capture the high-level capability: businesses can initiate and receive WhatsApp calls using VoIP.
3. Open at least one implementation-detail page, preferably:
   - Integration patterns
   - SIP guide
   This confirms the feature is not just marketing copy and reveals practical integration requirements.
4. Extract the practical constraints that matter to the user:
   - This requires WhatsApp Business infrastructure, not a personal WhatsApp account.
   - The current text-chat assistant cannot simply start taking WhatsApp calls by itself.
   - A dedicated business number / WABA setup is typically needed.
   - Real-time media handling/backend infrastructure is required.
   - SIP or call-related Graph API/webhook flows may be involved depending on architecture.
5. Translate the docs into user-facing truth in plain language:
   - "Yes, technically possible via WhatsApp Business Calling API."
   - "No, this current chat does not automatically become callable."
   - "You need a separate business calling system/backend."
6. Recommend the simplest practical rollout path:
   - Start with inbound calls to an AI business number.
   - Then add production hardening / outbound if needed.
7. End with one concrete fork-in-the-road question for the user, usually:
   - Use a new business number, or reuse an existing business number?

# Good answer shape
- First sentence: direct yes/no feasibility.
- Second: clear limitation of the current chat/session.
- Then a short architecture summary.
- Then the most practical next step.

# Important nuances
- Do not promise that ordinary WhatsApp consumer calling is open for arbitrary bot automation.
- Distinguish clearly between:
  - WhatsApp messages
  - voice notes
  - WhatsApp Business Calling API
- If the user says "I want to call you on WhatsApp," explain that the built system would be a dedicated AI business number, not literally this chat identity becoming a phone contact.

# Evidence pages worth checking
- WhatsApp Business Platform overview
- /documentation/business-messaging/whatsapp/calling
- /documentation/business-messaging/whatsapp/calling/integration-patterns
- /documentation/business-messaging/whatsapp/calling/sip

# Pitfalls
- The top-level docs may show Calling in navigation before the user realizes it is a business/API feature.
- Users often mean "WhatsApp call like normal personal chat"; clarify that the supported route is business/API-based.
- Avoid overstating immediacy: even when supported, deployment requires setup, review, and backend work.
