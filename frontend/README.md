# About

This is the ARK 2.0 frontend. It currently shows exactly one page: a calendar and a chat interface side-by-side. It’s currently a single-page app, but we plan on making it a multi-page app (using SvelteKit routing).

## Languages and dependencies

- TypeScript
- Svelte
- SvelteKit
- Prettier
- ESLint
- Vitest
- @testing-library/svelte
- @event-calendar/core

## Todos

### PRE-MVP
- Split the chat feature into its own component
- Figure out how to use library components in the UI
- Split the UI into multiple pages
    - Marketing landing page
    - Dashboard
    - Calendar-only view
    - Chat-only view
    - (potentially other pages in the future)
- Add authentication (primarily MIT Touchstone, possibly others)
- Make it interactive
    - Test basic user interaction using Cypress/Playwright/etc
- Connect to the backend
    - Detect unexpected/malformed backend output and display an appropriate error message? (to safeguard against potential backend-side bugs)
- Testing cleanup + expansion
    - ~~Refactor the UI HTML markup so that `screen.getByRole` or `screen.getByText` works (potentially making it more accessible)~~ (now refactored to use `screen.getByTestId` for now)
    - Mock the backend
    - Mock components (both library and ARK2.0-specific)
    - Mock user-generated content
    - Potentially determine code coverage
        - Figure out how `.c8rc` or `.nycrc` work so we can remove unnecessary files from the report
- Create a Figma mockup to guide future frontend development
- Set up at least one CI check

### POTENTIALLY POST-MVP:
- Fine-tune the CSS and/or HTML markup to look nicer
    - Figure out visual brand identity (favorite fonts? colors? logo?)
- User settings page (eg dark/light mode, etc)
- Some way for users to submit feedback
- Task list tracking
    - Specifically track assignments/classwork and their due dates
- Mobile-friendliness?
- Expand pre-commit CI checks aggressively

# Installation

## Slow

1. Install node.js if you don’t have it already.
2. Install npm if you don’t have it already.
3. Install git if you don’t have it already.
4. `cd` into your favorite folder.
5. Clone the entire repo using `git clone https://github.com/SGIARK/ARK2.0` (note: this repo is private)
6. `cd` into `ARK2.0/frontend` to access the `frontend` folder.
7. Install the remaining dependencies using `npm install`.
8. Run `npm run dev`, then immediately hit the O key, to launch the (currently extremely sparse) frontend in your web browser.

## Quick

Copy-paste this for a quickstart (assuming you already have node.js, npm, and git, and have cd'd in your favorite repository already).

```
git clone https://github.com/SGIARK/ARK2.0
cd ARK2.0/frontend
npm install
npx prettier **/* --check
npx eslint {src,test}/*
npm test
npm run dev
```

# File structure

(As of May 11, 2025.)

- `.npmrc`
- `.prettierignore`
- `.prettierrc`
- `.svelte-kit`
- `README.md` (this very file!)
- `eslint.config.js`
- `node_modules`
- `package-lock.json`
- `package.json`
- `src` (all the actual frontend code goes here!)
    - `app.d.ts`
    - `app.html`
    - `components`
        - `Calendar.svelte` (shows the calendar view)
    - `lib`
        - `index.ts` (currently empty but kept as a placeholder)
    - `routes`
        - `+page.svelte`
- `static`
    - `favicon.png` (not used right now)
    - `styles.css`
- `svelte.config.js`
- `test`
    - `Calendar.test.ts` (for testing the `<Calendar/>` component)
    - `page.svelte.test.ts` (for testing `src/routes/+page.svelte`, which is currently the only page available)
- `tsconfig.json`
- `vite.config.ts`
- `vitest-setup-client.ts`

# Contributing

As always, make a pull request.

## Style + quality guidelines

Before submitting your pull request, please do the following checks. It’s a good idea to do some or all of these before every commit too. The first three could potentially go into GitHub Actions, but we haven’t done that yet.

- Reformat everything using `npx prettier **/* --write`.
- Lint everything using `npx eslint **/*`. The output should be empty; if not, you should fix the issue(s) identified.
- Run the test cases using `npm test`. They should all pass; if not, you should fix the ones that fail.
- Finally, try using the new version of the UI yourself by running `npm run dev` to make sure it isn’t subtly broken in some way.

## Components

If your page or component code becomes too long or unwieldy, consider splitting it into another component. Since we are NOT building a single-page app, ask yourself if it could also plausibly be an entire page instead.

## Appearance

All CSS styles should live in `static/styles.css` for the time being. Do NOT use `import '[something].css` in any `<script>` tag because Svelte/Vite will automatically convert this into an injected `<style>` tag, and this is bad. Alternatively, you can add a `<link>` tag within the `<svelte:head>` directive.

If you plan on making major changes to the UI, please dogfood the new version yourself. If possible, let the other ARK 2.0 team members try it. Keep in mind that a great UI can often be just one CSS rule or one stray HTML tag away from an abysmal one.

## Automated testing

All test code should go in the `test` folder. Do NOT put any test code in the `src` folder. This makes it easier to review test code at a glance.

Every `.svelte` and `.ts` file in the `src` folder needs to be tested, with the obvious exception of `app.d.ts`.

As a general rule of thumb, to test a Svelte component, write one test per HTML tag. If the content or children of a certain tag can vary depending on certain variables (such as props, state, and/or network requests), write multiple tests for that tag using input space partitioning. Tags that are purely for layout purposes and will never change don’t need to be tested if you don’t want to. See the `test` folder for some examples.

Plain `.ts` files should be tested using input space partitioning for each function/class/etc. This should be fairly straightforward.

# Helpful links if you get stuck

## Documentation

- [ESLint](https://eslint.org/docs/latest/use/)
- MDN web
  - [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)
  - [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)
  - [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [Prettier](https://prettier.io/docs/)
- [Svelte](https://svelte.dev/docs/svelte/overview)
- [SvelteKit](https://svelte.dev/docs/kit/introduction)
- [Testing Library](https://testing-library.com/docs/)
  - [queries](https://testing-library.com/docs/queries/about)
  - [@testing-library/svelte](https://testing-library.com/docs/svelte-testing-library/intro)
- [TypeScript](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Vitest](https://vitest.dev/guide/)
- [@event-calendar GitHub repo](https://github.com/vkurko/calendar)

## Others

- [MIT SIPB Mattermost server](https://mattermost.xvm.mit.edu/sipb)
  - [ARK channel](https://mattermost.xvm.mit.edu/sipb/channels/ark)
- [StackOverflow](https://stackoverflow.com)
- [ChatGPT](https://chatgpt.com)
- [Claude.ai](https://claude.ai)
