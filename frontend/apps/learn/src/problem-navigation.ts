export const safeReturnUrl = (candidate: string | undefined): string =>
  candidate === '/problems' || candidate?.startsWith('/problems?')
    ? candidate
    : '/problems';
