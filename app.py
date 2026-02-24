import streamlit as st
import json
from datetime import datetime
import uuid
from test_risk_gate import draft_response, evaluate_risk, rewrite_draft

# --- Page Configuration ---
st.set_page_config(page_title="Wealthsimple CS Risk Gate", layout="wide")

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello. How can I help you today?"}]
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "pending_review" not in st.session_state:
    st.session_state.pending_review = None
if "latest_eval" not in st.session_state:
    st.session_state.latest_eval = None
if "latest_draft" not in st.session_state:
    st.session_state.latest_draft = None

# --- Top Navigation & Toggles ---
col_header, col_toggle = st.columns([3, 1])
with col_header:
    st.title("Support Hub")

st.markdown("---")

# --- Dynamic Layout ---
if demo_mode:
    col1, col2 = st.columns([1, 1], gap="large")
else:
    col1, col2 = st.columns([1, 0.01])

# --- PANEL A: Customer Experience (Left Column) ---
with col1:
    st.subheader("Customer Chat")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input Blocked if pending review
    if st.session_state.pending_review:
        st.warning("A support specialist is currently reviewing your request.")
        st.chat_input("Input disabled during review...", disabled=True)
    
    # Standard Input
    elif prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Processing & State UI
        with st.status("System processing...", expanded=True) as status:
            
            # Pass 1
            draft = draft_response(prompt)
            eval_data = json.loads(evaluate_risk(draft))
            
            # Autonomous Self-Correction Loop for Medium Risk
            if eval_data.get("risk_classification") == "MEDIUM":
                st.write("Medium risk detected. Attempting autonomous rewrite...")
                draft = rewrite_draft(draft, eval_data.get("explanation"))
                eval_data = json.loads(evaluate_risk(draft)) # Re-evaluate
                eval_data["explanation"] = f"[Rewritten] {eval_data.get('explanation')}"
            
            # Save for Control Plane visibility
            st.session_state.latest_draft = draft
            st.session_state.latest_eval = eval_data
            
            status.update(label="Routing Complete", state="complete", expanded=False)

        decision = eval_data.get("routing_decision")
        risk_level = eval_data.get("risk_classification")
        log_id = str(uuid.uuid4())[:8]
        
        # Log to Audit — full provenance captured at routing time
        st.session_state.audit_log.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "ID": log_id,
            "Risk": risk_level,
            "Decision": decision,
            "FlaggedVector": eval_data.get("flagged_vector"),
            "Explanation": eval_data.get("explanation"),
            "HighlightedText": eval_data.get("highlighted_text"),
            "AIDraft": draft,
            "FinalResponse": draft if decision == "auto_send" else None,
            "HumanAction": None,
            "FullEval": json.dumps(eval_data),
        })
        
        # UX Routing
        if decision == "auto_send":
            st.session_state.messages.append({"role": "assistant", "content": draft})
            st.rerun()
                
        elif decision == "human_review":
            intercept_msg = "Your request has been routed to a specialist to ensure accuracy. Please hold."
            st.session_state.messages.append({"role": "assistant", "content": intercept_msg})
            
            st.session_state.pending_review = {
                "draft": draft,
                "eval_data": eval_data,
                "id": log_id
            }
            st.rerun()
                
        elif decision == "escalate_block":
            intercept_msg = "Your request requires specialized assistance and has been escalated to our advisory team."
            st.session_state.messages.append({"role": "assistant", "content": intercept_msg})
            st.rerun()

# --- PANEL B: Risk Gate Control Plane (Right Column) ---
if demo_mode:
    with col2:
        st.subheader("Risk Gate Control Plane")
        
        # MODULE 1: Real-Time Evaluation
        if st.session_state.latest_eval:
            eval_data = st.session_state.latest_eval
            risk_level = eval_data.get("risk_classification", "UNKNOWN")
            
            # Human Readable Vector Mapping
            vector_map = {
                "Regulatory Boundary": "Regulatory Risk – Potential Outcome Guidance",
                "Demographic Assumption": "Demographic Risk – Unwarranted Assumption",
                "Urgency/Harm": "Urgency – Potential Harm or Fraud",
                "None": "None"
            }
            clean_vector = vector_map.get(eval_data.get('flagged_vector'), eval_data.get('flagged_vector'))

            # Status Banner
            if risk_level == "LOW":
                st.success(f"**Latest Routing: {risk_level}** - Auto-Sent")
            elif risk_level == "MEDIUM":
                st.warning(f"**Latest Routing: {risk_level}** - Intercepted")
            elif risk_level == "HIGH":
                st.error(f"**Latest Routing: {risk_level}** - Blocked & Escalated")
            
            # Explanation Data
            st.markdown(f"**Flagged Vector:** `{clean_vector}`")
            st.markdown(f"**Explanation:** {eval_data.get('explanation')}")
            if eval_data.get('highlighted_text') != "None":
                st.info(f"*Flagged Text: {eval_data.get('highlighted_text')}*")
            
            with st.expander("View Raw Output JSON"):
                st.json(eval_data)
        else:
            st.info("Awaiting customer input...")

        st.markdown("---")

        # MODULE 2: Active Human Review Queue
        if st.session_state.pending_review:
            st.warning("⚠️ **ACTION REQUIRED: Draft Pending Review**")
            pending_data = st.session_state.pending_review
            
            # Functional Edit/Approve Loop
            edited_draft = st.text_area("Review and Edit Draft:", pending_data["draft"], height=150)
            
            if st.button("Approve & Send to User", use_container_width=True, type="primary"):
                st.session_state.messages.append({"role": "assistant", "content": edited_draft})
                
                # Determine human action: did they edit the draft or approve as-is?
                was_edited = edited_draft.strip() != pending_data["draft"].strip()
                human_action = "human_edited_and_approved" if was_edited else "human_approved_as_is"

                # Update Audit Log with full response provenance
                for log in reversed(st.session_state.audit_log):
                    if log["ID"] == pending_data["id"]:
                        log["Decision"] = human_action
                        log["HumanAction"] = human_action
                        log["FinalResponse"] = edited_draft
                        break
                        
                st.session_state.pending_review = None
                st.rerun()
        
        # MODULE 3: Immutable Audit Log
        st.subheader("System Audit Log")
        if st.session_state.audit_log:
            display_cols = ["Time", "ID", "Risk", "Decision", "FlaggedVector", "Explanation", "HighlightedText"]
            st.dataframe(
                [{k: entry.get(k) for k in display_cols} for entry in st.session_state.audit_log],
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                label="⬇ Export Full Audit Trail (JSON)",
                data=json.dumps(st.session_state.audit_log, indent=2),
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )