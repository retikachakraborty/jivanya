import re
import uuid
from typing import Optional

from app.jiv.context.state import ConversationState
from app.jiv.schemas.chat import UserProfileSchema


class ContextManager:
    """In-memory session manager for Jiv multi-turn conversation state."""

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationState] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> ConversationState:
        sid = session_id or str(uuid.uuid4())
        if sid not in self._sessions:
            self._sessions[sid] = ConversationState(session_id=sid)
        return self._sessions[sid]

    def save(self, state: ConversationState) -> None:
        self._sessions[state.session_id] = state

    def extract_and_update(
        self,
        state: ConversationState,
        message: str,
        profile: Optional[UserProfileSchema] = None,
    ) -> ConversationState:
        text = message.lower().strip()

        # 1. Replace the session's profile-derived state on every request. This
        # prevents a prior profile (or a previously enabled boolean) from
        # leaking into the current authenticated user's request. Conversational
        # modifiers are applied below for the current turn.
        if profile:
            state.active_no_onion = profile.no_onion
            state.active_no_garlic = profile.no_garlic
            state.active_diet = profile.diet_preference if profile.diet_preference != "no preference" else None
            state.active_exclusions = sorted({item.strip().lower() for item in [*profile.allergies, *profile.exclusions] if item.strip()})

        # 2. Extract time modifiers (e.g. "under 20 minutes", "in 15 min", "< 30 mins")
        time_match = re.search(r"(?:under|less than|within|in|max(?:imum)?)\s+(\d+)\s*(?:min|mins|minute|minutes)", text)
        if time_match:
            state.active_max_time = int(time_match.group(1))

        # 3. Extract no-onion / no-garlic modifiers
        if re.search(r"\b(?:no|without|remove|skip)\s+onion\b", text):
            state.active_no_onion = True
        if re.search(r"\b(?:no|without|remove|skip)\s+garlic\b", text):
            state.active_no_garlic = True

        # 4. Extract diet modifiers
        if re.search(r"\b(?:make it|only|strictly)?\s*vegetarian\b", text) or "veg only" in text:
            state.active_diet = "vegetarian"
        elif re.search(r"\b(?:make it|only|strictly)?\s*vegan\b", text):
            state.active_diet = "vegan"

        # 5. Extract pagination requests ("show me another one", "another", "next", "more")
        if re.search(r"\b(?:show me\s+)?(?:another|next|more|different)\b", text):
            state.last_offset += 5
        else:
            # New query or modifier resets offset
            if not any(marker in text for marker in ["under", "without", "no onion", "no garlic", "make it"]):
                state.last_offset = 0

        # 6. Extract mentioned ingredients
        extracted_ingredients = self.extract_ingredients(text)
        if extracted_ingredients:
            state.active_ingredients = extracted_ingredients

        self.save(state)
        return state

    @staticmethod
    def extract_ingredients(text: str) -> list[str]:
        patterns = [
            r"(?:what\s+can\s+i|tell\s+me\s+something\s+i\s+can|how\s+to|suggest\s+something\s+to)?\s*(?:make|cook|prepare|whip\s+up)\s+(?:with|using)?\s+([^?.]+)",
            r"(?:i\s+have|using\s+ingredients?|ingredients?\s+on\s+hand:?)\s+([^?.]+)",
            r"(?:recipes?\s+(?:with|using))\s+([^?.]+)",
            r"(?:dish(?:es)?\s+with)\s+([^?.]+)",
        ]
        stopwords = {
            "a", "an", "the", "some", "something", "anything", "good", "quick", "easy",
            "dinner", "lunch", "breakfast", "snack", "food", "meal", "recipe", "recipes", "for",
            "stuff", "dish", "dishes", "please", "can", "you", "tell", "me"
        }
        found: list[str] = []
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                raw = m.group(1).strip()
                raw = re.sub(r"\b(?:under|less than|within|in)\s+\d+\s*(?:min|mins|minute|minutes)\b.*", "", raw, flags=re.I)
                parts = re.split(r",|\band\b|&|\+", raw, flags=re.I)
                for p in parts:
                    clean = " ".join(w for w in p.strip().lower().split() if w not in stopwords)
                    if clean and len(clean) >= 2 and clean not in found:
                        found.append(clean)
                if found:
                    break
        return found


context_manager = ContextManager()
