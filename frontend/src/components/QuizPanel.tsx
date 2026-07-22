import { useState } from "react";
import { useQuiz, useSubmitQuiz } from "../api/assessments";

export default function QuizPanel({ quizId, onDone }: { quizId: string; onDone: () => void }) {
  const { data: quiz, isLoading } = useQuiz(quizId);
  const submitQuiz = useSubmitQuiz();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<{ score: number; passed: boolean } | null>(null);

  if (isLoading || !quiz) return <p className="text-slate text-sm">Loading quiz...</p>;

  if (result) {
    return (
      <div className="card p-6 text-center">
        <p className="text-3xl font-display font-bold text-ink">{result.score}%</p>
        <p className={`mt-1 font-semibold ${result.passed ? "text-plum" : "text-red-500"}`}>
          {result.passed ? "Passed!" : "Not quite - you can try again."}
        </p>
        <button className="btn btn-ghost mt-4" onClick={onDone}>
          Back to quizzes
        </button>
      </div>
    );
  }

  return (
    <div className="card p-5">
      <h3 className="font-display font-semibold text-ink mb-4">{quiz.title}</h3>
      <div className="space-y-5">
        {quiz.questions.map((q, i) => (
          <div key={q.id}>
            <p className="text-sm font-medium text-ink">
              {i + 1}. {q.question_text}
            </p>
            <div className="mt-2 space-y-1.5">
              {(q.question_type === "true_false" ? ["true", "false"] : q.options).map((opt) => (
                <label key={opt} className="flex items-center gap-2 text-sm text-slate">
                  <input
                    type="radio"
                    name={q.id}
                    value={opt}
                    checked={answers[q.id] === opt}
                    onChange={() => setAnswers({ ...answers, [q.id]: opt })}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
      <button
        className="btn btn-primary mt-6"
        onClick={async () => {
          const payload = Object.entries(answers).map(([questionId, answerText]) => ({ questionId, answerText }));
          const res = await submitQuiz.mutateAsync({ quizId, answers: payload });
          setResult({ score: res.score, passed: res.passed });
        }}
        disabled={submitQuiz.isPending}
      >
        {submitQuiz.isPending ? "Submitting..." : "Submit answers"}
      </button>
    </div>
  );
}
