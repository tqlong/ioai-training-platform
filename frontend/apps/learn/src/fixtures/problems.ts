export type LearnProblemCard = {
  id: string;
  title: string;
};

// Phase 7 deliberately ships no fabricated public content. Phase 8 replaces
// this typed empty boundary with the generated published-problem API client.
export const problems: LearnProblemCard[] = [];
