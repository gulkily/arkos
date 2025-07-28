# About

This is the ARK 2.0 frontend. It's a Svelte web app, and it currently has four pages:

- a landing page
- an about page
- a "dashboard"
- a calendar-only view
- a chat-only view

# Tech stack

## Languages

- TypeScript
- Svelte

## CI dependencies

- Prettier
- ESLint
- Vitest
- @testing-library/svelte

## Other dependencies

- SvelteKit
- @event-calendar/core
- ajv
- vitest-fetch-mock

# Todo list

## Pre-MVP

- Add authentication (primarily MIT Touchstone, possibly others)
- Make the UI more user-friendly when the backend returns a malformed response
- Testing cleanup + expansion
  - Mock components (both library and ARK2.0-specific)
  - ~~Mock user-generated content~~ (maybe randomize?)
  - Determine code coverage
    - Figure out how `.c8rc` or `.nycrc` work so we can remove unnecessary files from the report
- Fine-tune the CSS to look nicer
  - Figure out visual brand identity (fonts? colors? logo?)

## Post-MVP

- Additional pages
  - user settings page (eg dark/light mode, etc)
  - Some way for users to submit feedback
  - Task list tracking
    - Specifically track assignments/classwork and their due dates?
- Mobile-friendliness?

# Installation

## Slow

1. Install node.js if you don’t have it already.
2. Install npm if you don’t have it already.
3. Install git if you don’t have it already.
4. `cd` into your favorite folder.
5. Clone the entire repo using `git clone https://github.com/SGIARK/ARK2.0`.
6. `cd` into `ARK2.0/frontend` to access the `frontend` folder.
7. Install the remaining dependencies using `npm install`.
8. Run `npm run dev`, then immediately hit the O key, to launch the (currently rather sparse) frontend in your web browser.

## Quick

Open a terminal window, copy-paste this entire code block, and hit enter. Be warned: this assumes you already installed node.js, npm, and git, that you've cd'd into your favorite repository already, and that you use VS Code as your code editor.

```sh
git clone https://github.com/SGIARK/ARK2.0
cd ARK2.0/frontend
npm install
npm run lint
npm test
npm run dev
code .
```

# File structure

(As of July 28, 2025.)

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
    - `chat.svelte` (shows the chat view)
    - `navbar.svelte`
  - `lib`
    - `index.ts` (currently empty but kept as a placeholder)
    - `schema_types.ts` (for type declarations)
  - `routes`
    - `about`
      - `+page.svelte`
    - `calendar`
      - `+page.svelte`
    - `chat`
      - `+page.svelte`
    - `dashboard`
      - `+page.svelte`
    - `+page.svelte`
- `static`
  - `favicon.png` (not used right now)
  - `styles.css`
- `svelte.config.js`
- `test`
  - `components`
    - `Calendar.test.ts` (for testing `src/components/Calendar.svelte`)
    - `chat.test.ts` (for testing `src/components/chat.svelte`)
  - `routes`
    - `calendar.test.ts`
    - `chat.test.ts`
  - `mock-backend.ts` (creates the mock backend)
  - `mock-backend.test.ts` (for testing the mock backend)
- `tsconfig.json`
- `vite.config.ts`
- `vitest-setup-client.ts`

# Contributing

As always, make a pull request.

## Style + quality guidelines

Before submitting your pull request, please do the following checks. The first three will also be run by GitHub Actions.

- Reformat everything using `npx prettier **/* --write`.
- Lint everything using `npx eslint **/*`. The output should be empty; if not, you should fix the issue(s) identified.
- Run the test cases using `npm test`. They should all pass; if not, you should fix the ones that fail.
- Finally, try using the new version of the UI yourself by running `npm run dev` to make sure it isn’t subtly broken in some way.

## Components

If your page or component code becomes too long or unwieldy, consider splitting it into another component. Since we are NOT building a single-page app, ask yourself if it could also plausibly be an entire page instead.

## Appearance

All CSS styles should live in `static/styles.css`. Do NOT use `import '[something].css` in any `<script>` tag because Svelte/Vite will automatically convert this into an injected `<style>` tag, and this is bad. Alternatively, you can add a `<link>` tag within the `<svelte:head>` directive.

If you plan on making major changes to the UI, please dogfood the new version yourself. If possible, let the other ARK 2.0 team members try it. Keep in mind that a great UI can often be just one CSS rule or one stray HTML tag away from an abysmal one.

## Automated testing

All test code should go in the `test` folder. Do NOT put any test code in the `src` folder. This makes it easy to review test code at a glance. Tests for `src/components/` go in `test/components/` and tests for `src/routes/` go in `test/routes/`.

As a general rule of thumb, every `.svelte` and `.ts` file in the `src` folder needs a corresponding test suite. However, this excludes `app.d.ts`, TypeScript type declarations, and static Svelte components or routes whose content will never change.

To test a dynamic Svelte component, write one test per HTML tag. If the content or children of a certain tag can vary depending on certain variables (such as props, state, and/or network requests), write multiple tests for that tag using input space partitioning. You don't need to test tags that are purely for layout purposes and that will never change. See the `test` folder for some examples.

Test plain `.ts` files using input space partitioning for each function/class/etc.

## JSON schemas

Schemas go in `../schemas/`. This is *intentionally* a repo top-level folder because double-checking responses and requests are malformed is also very useful for backend-side code.

Use `ajv` to validate data against a schema. Don't roll your own validator, because it'll probably be a lot flakier. Make sure to type your validator with `ValidateFunction<T>` instead of just `ValidateFunction`, so that you can convince TypeScript can narrow the data's type for you.

# Helpful links if you get stuck

## Documentation

- [ESLint](https://eslint.org/docs/latest/use/)
- MDN web
  - [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)
  - [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)
  - [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
  - [Request](https://developer.mozilla.org/en-US/docs/Web/API/Request): useful when developing or testing the mock backend
  - [Response](https://developer.mozilla.org/en-US/docs/Web/API/Response): also useful for the mock backend
- [Prettier](https://prettier.io/docs/)
- [Svelte](https://svelte.dev/docs/svelte/overview)
- [SvelteKit](https://svelte.dev/docs/kit/introduction)
- [Testing Library](https://testing-library.com/docs/)
  - [queries](https://testing-library.com/docs/queries/about)
  - [@testing-library/svelte](https://testing-library.com/docs/svelte-testing-library/intro)
- [TypeScript](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Vitest](https://vitest.dev/guide/)
- [@event-calendar GitHub repo](https://github.com/vkurko/calendar)
- [ajv API reference](https://ajv.js.org/api.html)
  - [ajv guide](https://ajv.js.org/guide/typescript.html)
- [vitest-fetch-mock README](https://www.npmjs.com/package/vitest-fetch-mock)

## Others

- [MIT SIPB Mattermost server](https://mattermost.xvm.mit.edu/sipb)
  - [ARK channel](https://mattermost.xvm.mit.edu/sipb/channels/ark)
- [StackOverflow](https://stackoverflow.com)
- [ChatGPT](https://chatgpt.com)
- [Claude.ai](https://claude.ai)
