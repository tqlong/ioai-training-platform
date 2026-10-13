import type { AuthorVocabularyRecord } from '@ioai/api-client';
import { fireEvent, render, screen } from '@testing-library/react';

import {
  CurriculumEditor,
  emptyCurriculumDraft,
} from '../src/components/curriculum-editor';

const record = (
  vocabularyType: string,
  code: string,
  label: string,
  breadcrumbs: string[] = [],
): AuthorVocabularyRecord => ({
  identity: { vocabulary_type: vocabularyType, code },
  labels: { en: label, vi: `VI ${label}` },
  aliases: [],
  status: 'ACTIVE',
  parent_identity: null,
  breadcrumbs: breadcrumbs.map((item) => ({ vocabulary_type: 'TOPIC', code: item })),
  availability: { is_available: true, reason_code: 'AVAILABLE', message: 'Available' },
});

const vocabulary = [
  record('PATHWAY_STAGE', 'AI_1_FOUNDATIONS', 'AI Foundations'),
  record('DIFFICULTY', 'EASY', 'Easy'),
  record('TASK_TYPE', 'QUIZ_SINGLE', 'Single-choice quiz'),
  record('COMPETENCY', 'EVAL_METRICS', 'Metrics'),
  record('COMPETENCY', 'MATH_STATISTICS', 'Statistics'),
  record('COMPETENCY', 'ML_CLASSIFICATION', 'Classification competency'),
  record('COMPETENCY', 'PROG_PYTHON', 'Python'),
  record(
    'TOPIC',
    'ML_CONFUSION_MATRIX',
    'Confusion Matrix',
    ['TOPIC_MACHINE_LEARNING', 'ML_EVALUATION', 'ML_CONFUSION_MATRIX'],
  ),
];

describe('canonical curriculum editor', () => {
  it('persists composite identities and shows topic breadcrumbs', () => {
    let value = emptyCurriculumDraft();
    const { rerender } = render(
      <CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />,
    );

    fireEvent.change(screen.getByRole('combobox', { name: 'Pathway stage' }), {
      target: { value: 'AI_1_FOUNDATIONS' },
    });
    rerender(<CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    fireEvent.click(screen.getByRole('checkbox', { name: /Confusion Matrix/ }));

    expect(value.stage).toEqual(['PATHWAY_STAGE', 'AI_1_FOUNDATIONS']);
    expect(value.topics).toEqual([['TOPIC', 'ML_CONFUSION_MATRIX']]);
    expect(screen.getByText(/TOPIC_MACHINE_LEARNING.*ML_EVALUATION/)).toBeTruthy();
  });

  it('limits secondary competencies to three and keeps types visible', () => {
    let value = emptyCurriculumDraft();
    const { rerender } = render(
      <CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />,
    );

    for (const name of ['Statistics', 'Classification competency', 'Python']) {
      fireEvent.click(screen.getByRole('checkbox', { name: new RegExp(name) }));
      rerender(<CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    }

    expect(value.secondary_competencies).toHaveLength(3);
    expect(screen.getAllByText('COMPETENCY', { exact: false }).length).toBeGreaterThan(0);
    expect(screen.getByText('Maximum three secondary competencies selected.')).toBeTruthy();
  });

  it('preserves relationship, evidence, and stable IDs for task prerequisites', () => {
    let value = emptyCurriculumDraft();
    const { rerender } = render(
      <CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />,
    );
    fireEvent.change(screen.getByRole('combobox', { name: 'Prerequisite relationship' }), { target: { value: 'REQUIRED' } });
    fireEvent.change(screen.getByRole('combobox', { name: 'Prerequisite target type' }), { target: { value: 'TASK' } });
    rerender(<CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    fireEvent.change(screen.getByRole('textbox', { name: 'Prerequisite target ID' }), { target: { value: 'problem-123' } });
    fireEvent.change(screen.getByRole('combobox', { name: 'Minimum learning evidence' }), { target: { value: 'PRACTICED' } });
    fireEvent.click(screen.getByRole('button', { name: 'Add prerequisite' }));
    expect(value.prerequisites[0]).toMatchObject({
      relationship: 'REQUIRED', target_type: 'TASK', target_id: 'problem-123', minimum_evidence: 'PRACTICED',
    });
  });

  it('adds typed prerequisites rather than free-form tags', () => {
    let value = emptyCurriculumDraft();
    const { rerender } = render(
      <CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />,
    );

    fireEvent.change(screen.getByRole('combobox', { name: 'Prerequisite target type' }), {
      target: { value: 'TOPIC' },
    });
    rerender(<CurriculumEditor onChange={(next) => { value = next; }} value={value} vocabulary={vocabulary} />);
    fireEvent.change(screen.getByRole('combobox', { name: 'Prerequisite target' }), {
      target: { value: 'ML_CONFUSION_MATRIX' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Add prerequisite' }));

    expect(value.prerequisites[0]).toMatchObject({
      relationship: 'RECOMMENDED',
      target_type: 'TOPIC',
      target_identity: ['TOPIC', 'ML_CONFUSION_MATRIX'],
    });
  });

  it('shows an actionable blocker for a selected unavailable canonical value', () => {
    const unavailable = {
      ...record('PATHWAY_STAGE', 'AI_3_NATIONAL', 'National selection'),
      availability: { is_available: false, reason_code: 'UNAVAILABLE_IN_RELEASE_0', message: 'AI_3_NATIONAL is canonical but unavailable in Release 0.' },
    };
    const value = { ...emptyCurriculumDraft(), stage: ['PATHWAY_STAGE', 'AI_3_NATIONAL'] as [string, string] };
    render(<CurriculumEditor onChange={() => undefined} value={value} vocabulary={[...vocabulary, unavailable]} />);
    expect(screen.getByRole('alert').textContent).toContain('Select an available Release 0 pathway stage');
  });

  it('displays Vietnamese translation alongside English label for topics', () => {
    const value = emptyCurriculumDraft();
    render(<CurriculumEditor onChange={() => undefined} value={value} vocabulary={vocabulary} />);
    expect(screen.getByText(/Confusion Matrix · VI Confusion Matrix/)).toBeTruthy();
  });
});
