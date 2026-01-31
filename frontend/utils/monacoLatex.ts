import type * as Monaco from 'monaco-editor'

export function registerLatexLanguage(monaco: typeof Monaco) {
  if (monaco.languages.getLanguages().some((lang) => lang.id === 'latex')) return

  monaco.languages.register({ id: 'latex' })

  monaco.languages.setMonarchTokensProvider('latex', {
    tokenizer: {
      root: [
        // コメント
        [/%.*$/, 'comment'],

        // 数式モード（ディスプレイ）
        [/\$\$/, { token: 'string', next: '@mathDisplay' }],
        [/\\\[/, { token: 'string', next: '@mathDisplayBracket' }],

        // 数式モード（インライン）
        [/\$/, { token: 'string', next: '@mathInline' }],
        [/\\\(/, { token: 'string', next: '@mathInlineParen' }],

        // 環境
        [/\\begin\{([^}]+)\}/, 'keyword'],
        [/\\end\{([^}]+)\}/, 'keyword'],

        // コマンド
        [/\\[a-zA-Z@]+\*?/, 'keyword'],

        // 括弧
        [/[{}]/, 'delimiter.bracket'],
        [/\[|\]/, 'delimiter.square']
      ],
      mathInline: [
        [/\$/, { token: 'string', next: '@pop' }],
        [/\\./, 'string'],
        [/[^$\\]+/, 'string']
      ],
      mathInlineParen: [
        [/\\\)/, { token: 'string', next: '@pop' }],
        [/\\./, 'string'],
        [/[^\\]+/, 'string']
      ],
      mathDisplay: [
        [/\$\$/, { token: 'string', next: '@pop' }],
        [/\\./, 'string'],
        [/[^$\\]+/, 'string']
      ],
      mathDisplayBracket: [
        [/\\\]/, { token: 'string', next: '@pop' }],
        [/\\./, 'string'],
        [/[^\\]+/, 'string']
      ]
    }
  })
}
