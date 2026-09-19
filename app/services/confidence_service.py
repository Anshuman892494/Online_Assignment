from typing import List, Dict, Any, Tuple

class ConfidenceScorer:
    """
    Evaluates extraction certainty and flags items requiring human review.
    Enforces rules from Assignment Sections 4, 5, & 6.
    """

    @staticmethod
    def evaluate_question(
        question_number: str,
        question_text: str,
        question_type: str,
        options: List[Dict[str, str]] | None,
        answer: str | None,
        source_pages: List[int],
        initial_confidence: float = 1.0
    ) -> Tuple[float, bool, List[str]]:
        """
        Calculates confidence score and review flags.
        Returns: (confidence_score, review_required, review_reasons)
        """
        score = initial_confidence
        reasons: List[str] = []

        # 1. Option Completeness check for Multiple Choice
        if question_type == "multiple_choice":
            if not options or len(options) == 0:
                score -= 0.35
                reasons.append("MISSING_ALL_OPTIONS")
            elif len(options) < 4:
                # E.g. only A, B, C found or D missing
                score -= 0.20
                labels = [opt.get("label", "").upper() for opt in options]
                expected = ["A", "B", "C", "D"]
                missing = [lbl for lbl in expected[:len(options)+1] if lbl not in labels]
                if missing:
                    reasons.append(f"MISSING_OPTION_{missing[0]}")
                else:
                    reasons.append("FEWER_THAN_4_OPTIONS")

        # 2. Answer key check
        if not answer:
            score -= 0.15
            reasons.append("UNMATCHED_ANSWER")
        else:
            # Check if answer corresponds to an existing option
            if options:
                valid_labels = [opt.get("label", "").upper() for opt in options]
                if answer.upper() not in valid_labels:
                    score -= 0.25
                    reasons.append("UNCERTAIN_ANSWER_MISMATCH")

        # 3. Cross-page boundary check
        if len(source_pages) > 1:
            score -= 0.05
            reasons.append("CROSS_PAGE_CONTINUATION")

        # 4. Question Text Quality / Truncation check
        if len(question_text.strip()) < 15:
            score -= 0.20
            reasons.append("SUSPICIOUSLY_SHORT_QUESTION_TEXT")

        # Normalize score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, round(score, 2)))
        review_required = len(reasons) > 0 or final_score < 0.85

        return final_score, review_required, reasons

confidence_scorer = ConfidenceScorer()
