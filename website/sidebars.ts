import type { SidebarsConfig } from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
      ],
    },
    {
      type: 'category',
      label: 'CLI Reference',
      items: [
        'cli-reference/overview',
        'cli-reference/reference',
        'cli-reference/time',
        'cli-reference/coords',
        'cli-reference/sun-moon',
        'cli-reference/planets',
      ],
    },
    {
      type: 'category',
      label: 'Python API',
      items: [
        'python-api/overview',
        'python-api/reference',
        'python-api/modules',
      ],
    },
    {
      type: 'category',
      label: 'Module Guides',
      items: [
        'module-guides/time',
        'module-guides/coords',
        'module-guides/angles',
        'module-guides/sun',
        'module-guides/moon',
        'module-guides/planets',
        'module-guides/observer',
        'module-guides/visibility',
        'module-guides/constants',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/verbose',
        'guides/precision',
      ],
    },
  ],
  development: [
    'development/overview',
    'development/testing',
    'development/contributing',
    'development/dependencies',
    'development/cheatsheet',
    'development/maintainers',
    'development/license',
  ],
};

export default sidebars;
