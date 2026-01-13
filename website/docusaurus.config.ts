import { themes as prismThemes, type PrismTheme } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// Absent Contrast dark theme for Prism
const absentContrastTheme: PrismTheme = {
  plain: {
    color: '#aeb9c4',
    backgroundColor: '#0d1013',
  },
  styles: [
    {
      types: ['comment', 'prolog', 'doctype', 'cdata'],
      style: { color: '#44515e' },
    },
    {
      types: ['punctuation'],
      style: { color: '#7a8b99' },
    },
    {
      types: ['property', 'tag', 'boolean', 'number', 'constant', 'symbol'],
      style: { color: '#61bcc6' },
    },
    {
      types: ['selector', 'attr-name', 'string', 'char', 'builtin'],
      style: { color: '#addbbc' },
    },
    {
      types: ['operator', 'entity', 'url'],
      style: { color: '#aeb9c4' },
    },
    {
      types: ['atrule', 'attr-value', 'keyword'],
      style: { color: '#228a96' },
    },
    {
      types: ['function', 'class-name'],
      style: { color: '#e6eaef' },
    },
    {
      types: ['regex', 'important', 'variable'],
      style: { color: '#6ba77f' },
    },
  ],
};

const config: Config = {
  title: 'astr0',
  tagline: 'Per aspera ad astra — Through hardships to the stars',
  favicon: 'img/favicon.ico',

  url: 'https://oddurs.github.io',
  baseUrl: '/astr0/',

  organizationName: 'oddurs',
  projectName: 'astr0',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Structured data for search engines
  headTags: [
    {
      tagName: 'script',
      attributes: { type: 'application/ld+json' },
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org/',
        '@type': 'SoftwareApplication',
        name: 'astr0',
        description: 'Professional astronomy calculation toolkit for Python',
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Cross-platform',
        url: 'https://oddurs.github.io/astr0/',
        offers: {
          '@type': 'Offer',
          price: '0',
          priceCurrency: 'USD',
        },
      }),
    },
  ],

  // Future flags for v4 compatibility
  future: {
    v4: {
      removeLegacyPostBuildHeadAttribute: true,
    },
    experimental_faster: {
      swcJsLoader: true,
      swcJsMinimizer: true,
      swcHtmlMinimizer: true,
      lightningCssMinimizer: true,
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
    {
      href: 'https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap',
      type: 'text/css',
    },
  ],

  plugins: ['docusaurus-plugin-sass'],

  presets: [
    [
      'classic',
      {
        docs: {
          path: '../docs',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/oddurs/astr0/tree/master/',
          routeBasePath: 'docs',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          breadcrumbs: true,
          remarkPlugins: [
            remarkMath,
            [require('@docusaurus/remark-plugin-npm2yarn'), { sync: true }],
          ],
          rehypePlugins: [rehypeKatex],
        },
        blog: {
          showReadingTime: true,
          blogTitle: 'astr0 Blog',
          blogDescription: 'Release notes and updates for astr0',
          postsPerPage: 10,
          blogSidebarTitle: 'Recent Posts',
          blogSidebarCount: 'ALL',
        },
        theme: {
          customCss: './src/css/custom.scss',
        },
        sitemap: {
          lastmod: 'date',
          changefreq: 'weekly',
          priority: 0.5,
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // SEO metadata
    metadata: [
      { name: 'keywords', content: 'astronomy, python, cli, julian date, coordinates, sun, moon, planets, ephemeris' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ],

    image: 'img/astr0-social-card.png',

    // Announcement bar for v0.3.0 release
    announcementBar: {
      id: 'v0.3.0',
      content: 'astr0 v0.3.0 released with planets module! <a href="/astr0/docs/module-guides/planets">Learn more</a>',
      backgroundColor: '#7c3aed',
      textColor: '#ffffff',
      isCloseable: true,
    },

    navbar: {
      title: 'astr0',
      hideOnScroll: true,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentation',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left',
        },
        {
          href: 'https://github.com/oddurs/astr0',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://pypi.org/project/astr0/',
          label: 'PyPI',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            { label: 'Getting Started', to: '/getting-started/installation' },
            { label: 'CLI Reference', to: '/cli-reference/overview' },
            { label: 'Python API', to: '/python-api/overview' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'GitHub Issues', href: 'https://github.com/oddurs/astr0/issues' },
            { label: 'Contributing', href: 'https://github.com/oddurs/astr0/blob/master/CONTRIBUTING.md' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'GitHub', href: 'https://github.com/oddurs/astr0' },
            { label: 'PyPI', href: 'https://pypi.org/project/astr0/' },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} astr0 contributors. Built with Docusaurus.`,
    },

    // Sidebar behavior
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },

    // Table of contents
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },

    prism: {
      theme: absentContrastTheme,
      darkTheme: absentContrastTheme,
      additionalLanguages: ['bash', 'python', 'json', 'toml', 'diff'],
      magicComments: [
        {
          className: 'theme-code-block-highlighted-line',
          line: 'highlight-next-line',
          block: { start: 'highlight-start', end: 'highlight-end' },
        },
        {
          className: 'code-block-error-line',
          line: 'error-next-line',
        },
      ],
    },

    colorMode: {
      defaultMode: 'dark',
      disableSwitch: true,
      respectPrefersColorScheme: false,
    },
  } satisfies Preset.ThemeConfig,

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en'],
        indexBlog: false,
        docsRouteBasePath: '/',
        docsDir: '../docs',
      },
    ],
  ],
};

export default config;
