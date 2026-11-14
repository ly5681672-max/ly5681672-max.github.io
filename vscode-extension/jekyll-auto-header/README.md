# Jekyll Auto Header (Web Extension)

A VS Code Web Extension for github.dev. When a Markdown file is created directly under the workspace's `_posts/` directory, it inserts Jekyll YAML front matter immediately.

## Behavior

- Listens to the VS Code `workspace.onDidCreateFiles` event.
- Works with dated, undated, English, and Chinese filenames.
- Uses the filename (without `.md`; strips a leading `YYYY-MM-DD-` when present) as the title.
- Uses the current time in `Asia/Shanghai`, formatted with `+0800`.
- Leaves files with an existing YAML front matter untouched.
- Does not rename files or modify existing body text.
- Includes a manual command: **Jekyll Auto Header: Insert Header**.

## Development

```sh
npm install
npm test
npm run build
```

The `browser` entry and bundled browser output make this a Web Extension for github.dev. The Node entry is included for desktop VS Code compatibility.

## Marketplace publication

The manifest currently uses the provisional publisher ID `ly5681672-max`. Marketplace publication requires that this exact publisher ID be registered and an Azure DevOps Marketplace Personal Access Token be configured as a GitHub Actions secret named `VSCE_PAT`. Do not commit the token.
