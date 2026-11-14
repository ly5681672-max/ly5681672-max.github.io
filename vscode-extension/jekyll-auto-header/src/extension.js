const vscode = require("vscode");
const { createFrontMatter } = require("./frontmatter");

function isPostMarkdown(uri) {
  const path = uri.path.replace(/\\/g, "/");
  return /(^|\\/)\_posts\\/[^/]+\\.md$/i.test(path);
}

async function insertHeader(uri) {
  if (!isPostMarkdown(uri)) return false;

  const document = await vscode.workspace.openTextDocument(uri);
  const text = document.getText();
  if (text.startsWith("---") || text.startsWith("\\uFEFF---")) return false;

  const header = createFrontMatter(uri.path.split("/").pop());
  const edit = new vscode.WorkspaceEdit();
  edit.insert(uri, new vscode.Position(0, 0), header);
  return vscode.workspace.applyEdit(edit);
}

function activate(context) {
  context.subscriptions.push(
    vscode.workspace.onDidCreateFiles(async (event) => {
      for (const uri of event.files) {
        try {
          await insertHeader(uri);
        } catch (error) {
          vscode.window.showErrorMessage(
            `Jekyll Auto Header: failed to insert front matter: ${error.message}`
          );
        }
      }
    }),
    vscode.commands.registerCommand("jekyll-auto-header.insertHeader", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;
      const success = await insertHeader(editor.document.uri);
      if (success) vscode.window.showInformationMessage("Jekyll front matter inserted.");
    })
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
