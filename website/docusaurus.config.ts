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
  title: 'starward',
  tagline: 'Per aspera ad astra — Through hardships to the stars',
  favicon: 'img/favicon.ico',

  url: 'https://starward.dev',
  baseUrl: '/',

  organizationName: 'oddurs',
  projectName: 'starward',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Structured data for search engines and favicons
  headTags: [
    {
      tagName: 'script',
      attributes: { type: 'application/ld+json' },
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org/',
        '@type': 'SoftwareApplication',
        name: 'starward',
        description: 'Professional astronomy calculation toolkit for Python',
        applicationCategory: 'DeveloperApplication',
        operatingSystem: 'Cross-platform',
        url: 'https://starward.dev',
        offers: {
          '@type': 'Offer',
          price: '0',
          priceCurrency: 'USD',
        },
      }),
    },
    {
      tagName: 'link',
      attributes: { rel: 'apple-touch-icon', sizes: '180x180', href: '/img/apple-touch-icon.png' },
    },
    {
      tagName: 'link',
      attributes: { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/img/favicon-32x32.png' },
    },
    {
      tagName: 'link',
      attributes: { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/img/favicon-16x16.png' },
    },
    {
      tagName: 'link',
      attributes: { rel: 'manifest', href: '/site.webmanifest' },
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
    {
      href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
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
          editUrl: 'https://github.com/oddurs/starward/tree/master/',
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
          blogTitle: 'starward Blog',
          blogDescription: 'Release notes and updates for starward',
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

    image: 'img/starward-social-card.png',

    navbar: {
      logo: {
        alt: 'starward logo',
        src: 'img/logo.svg',
      },
      hideOnScroll: true,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentation',
        },
        {
          type: 'docSidebar',
          sidebarId: 'development',
          position: 'left',
          label: 'Development',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left',
        },
        {
          href: 'https://github.com/oddurs/starward',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://pypi.org/project/starward/',
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
            { label: 'Getting Started', to: '/docs/getting-started/installation' },
            { label: 'CLI Reference', to: '/docs/cli-reference/overview' },
            { label: 'Python API', to: '/docs/python-api/overview' },
          ],
        },
        {
          title: 'Development',
          items: [
            { label: 'Contributing', to: '/docs/development/contributing' },
            { label: 'Testing', to: '/docs/development/testing' },
            { label: 'Cheatsheet', to: '/docs/development/cheatsheet' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'GitHub Issues', href: 'https://github.com/oddurs/starward/issues' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'GitHub', href: 'https://github.com/oddurs/starward' },
            { label: 'PyPI', href: 'https://pypi.org/project/starward/' },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} starward contributors. Built with Docusaurus.`,
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
