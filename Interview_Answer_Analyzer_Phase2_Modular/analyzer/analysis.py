"""Rule-based interview answer analysis, owned by the Answer Analysis team member."""

def analyze_answer(question, answer):
    """Return a simple score, human-readable feedback list, and word count."""
    words = answer.strip().split()
    word_count = len(words)
    score = 0
    feedback = []

    # Longer answers usually give the student more room to explain an example.
    if word_count >= 80:
        score += 30; feedback.append("Good detail: your answer has enough explanation.")
    elif word_count >= 40:
        score += 22; feedback.append("Your answer has a reasonable length. Add detail if useful.")
    elif word_count >= 20:
        score += 14; feedback.append("Try to explain your point in more detail.")
    else:
        score += 5; feedback.append("Your answer is quite short. Add context and an example.")

    stop_words = {"what", "why", "when", "where", "which", "who", "how", "does", "your", "you", "the", "and", "for", "with", "are", "was", "this", "that", "tell", "about", "have", "from"}
    def clean(text):
        return {word.strip(".,?!:;()[]{}\"'").lower() for word in text.split()}
    question_words = {w for w in clean(question) if len(w) > 3 and w not in stop_words}
    answer_words = clean(answer)
    overlap = len(question_words & answer_words) / max(1, len(question_words))
    score += min(30, round(overlap * 30))
    feedback.append("Your answer includes words related to the question." if overlap >= 0.5 else "Connect your answer more clearly to the main words in the question.")

    action_words = {"achieved", "built", "created", "developed", "improved", "learned", "managed", "solved", "responsible", "confident", "team", "result", "successfully", "completed"}
    found = action_words & answer_words
    score += min(20, len(found) * 5)
    feedback.append("You use action-oriented language: " + ", ".join(sorted(found)) + "." if found else "Mention an action you took and the result you achieved.")
    if answer and answer[0].isupper(): score += 10
    else: feedback.append("Start your answer with a capital letter.")
    if answer.rstrip().endswith((".", "!", "?")): score += 10
    else: feedback.append("Finish your answer with suitable punctuation.")
    return max(0, min(100, score)), feedback, word_count
