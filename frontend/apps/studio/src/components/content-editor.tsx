'use client';

import { useState } from 'react';

export type TranslationState = 'COMPLETE' | 'PENDING';
export type LocalizedDraft = {
  en: string;
  vi: string;
  en_state: TranslationState;
  vi_state: TranslationState;
};
export type ContentDraft = {
  title: LocalizedDraft;
  summary: LocalizedDraft;
  objectives: LocalizedDraft[];
  blocks: Array<{
    kind: string;
    content: LocalizedDraft;
    order: number;
    reveal_order: number | null;
  }>;
};

const blankLocalized = (): LocalizedDraft => ({
  en: '', vi: '', en_state: 'PENDING', vi_state: 'PENDING',
});

export const emptyContentDraft = (): ContentDraft => ({
  title: blankLocalized(),
  summary: blankLocalized(),
  objectives: [blankLocalized()],
  blocks: [
    { kind: 'STATEMENT', content: blankLocalized(), order: 1, reveal_order: null },
    { kind: 'PROVIDED_INFORMATION', content: blankLocalized(), order: 2, reveal_order: null },
    { kind: 'EXAMPLE', content: blankLocalized(), order: 3, reveal_order: null },
    { kind: 'CONSTRAINT', content: blankLocalized(), order: 4, reveal_order: null },
    { kind: 'HINT', content: blankLocalized(), order: 5, reveal_order: 1 },
    { kind: 'EXPLANATION', content: blankLocalized(), order: 6, reveal_order: null },
    { kind: 'FEEDBACK', content: blankLocalized(), order: 7, reveal_order: null },
  ],
});

export function ContentEditor({
  value,
  onChange,
}: {
  value: ContentDraft;
  onChange: (value: ContentDraft) => void;
}) {
  const [language, setLanguage] = useState<'en' | 'vi'>('en');
  const languageName = language === 'en' ? 'English' : 'Vietnamese';

  const updateLocalized = (
    target: LocalizedDraft,
    nextText: string,
  ): LocalizedDraft => ({
    ...target,
    [language]: nextText,
    [`${language}_state`]: nextText.trim() ? 'COMPLETE' : 'PENDING',
  });
  const setPending = (pending: boolean) => {
    onChange({
      ...value,
      title: { ...value.title, [`${language}_state`]: pending ? 'PENDING' : 'COMPLETE' },
    });
  };
  const field = (
    label: string,
    target: LocalizedDraft,
    update: (next: LocalizedDraft) => void,
    multiline = true,
  ) => (
    <label>
      <span>{languageName} {label}</span>
      {multiline ? (
        <textarea
          aria-label={`${languageName} ${label}`}
          id={`field-content-${label.replaceAll(' ', '-')}-${language}`}
          onChange={(event) => update(updateLocalized(target, event.target.value))}
          rows={label === 'title' ? 2 : 5}
          value={target[language]}
        />
      ) : (
        <input
          aria-label={`${languageName} ${label}`}
          id={`field-content-${label.replaceAll(' ', '-')}-${language}`}
          onChange={(event) => update(updateLocalized(target, event.target.value))}
          value={target[language]}
        />
      )}
    </label>
  );

  return (
    <section aria-labelledby="content-heading" className="editor-section" id="content">
      <div className="section-heading">
        <div>
          <h2 id="content-heading">Bilingual learner content</h2>
          <p>Edit one language at a time. Both translations remain in this draft.</p>
        </div>
        <div aria-label="Editing language" className="language-toggle" role="group">
          <button aria-pressed={language === 'en'} onClick={() => setLanguage('en')} type="button">Edit English</button>
          <button aria-pressed={language === 'vi'} onClick={() => setLanguage('vi')} type="button">Edit Vietnamese</button>
        </div>
      </div>

      {language === 'vi' && (
        <aside className="input-method-note">
          <strong>Use your system Vietnamese keyboard</strong>
          <span> Native UniKey, Simple Telex, or another OS input method is supported. Browser conversion is not enabled.</span>
        </aside>
      )}

      <label className="pending-control">
        <input
          checked={value.title[`${language}_state`] === 'PENDING'}
          onChange={(event) => setPending(event.target.checked)}
          type="checkbox"
        />
        <span>{languageName} translation pending</span>
      </label>
      {value.title[`${language}_state`] === 'PENDING' && (
        <p role="status">The {languageName} translation is pending.</p>
      )}

      {field('title', value.title, (title) => onChange({ ...value, title }), false)}
      {field('summary', value.summary, (summary) => onChange({ ...value, summary }))}
      {field('learning objective', value.objectives[0], (objective) => onChange({
        ...value, objectives: [objective, ...value.objectives.slice(1)],
      }))}
      {value.blocks.map((block, index) => (
        <div key={`${block.kind}-${block.order}`}>
          {field(
            blockLabel(block.kind),
            block.content,
            (content) => onChange({
              ...value,
              blocks: value.blocks.map((item, itemIndex) => (
                itemIndex === index ? { ...item, content } : item
              )),
            }),
          )}
        </div>
      ))}
    </section>
  );
}

const blockLabel = (kind: string) => ({
  STATEMENT: 'problem statement',
  PROVIDED_INFORMATION: 'provided information',
  EXAMPLE: 'examples',
  CONSTRAINT: 'constraints and assumptions',
  HINT: 'hint',
  EXPLANATION: 'explanation',
  FEEDBACK: 'feedback prompt',
}[kind] ?? kind.toLowerCase());
