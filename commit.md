# How to commit your work

Everyone works on their own branch. Nobody pushes directly to `main`; Role A reviews and merges everything into it.

## First-time setup (once)

Ask Role A to add you to the GitHub repo as a collaborator, then run:

```bash
git clone https://github.com/DevOlabode/clinic.exe.git
cd clinic.exe
git config user.name "Your Name"
git config user.email "you@example.com"
```

Use the email on your GitHub account. If you need to run the app with the AI, create a file called `.env` in this folder for your API keys and `MODEL`. Git ignores it.

The first time you push, Git may ask you to log in. Your GitHub password won't work here, so use `gh auth login` if you have the GitHub CLI, or a [personal access token](https://github.com/settings/tokens) in place of the password.

## The everyday routine

**1. Get the latest `main` and start a branch**

```bash
git switch main
git pull
git switch -c frontend/intake-form
```

Start the branch name with your area, `backend/`, `frontend/`, `catalog/` or `pitch/`, followed by a few words about the task.

**2. Do one small piece of work, then see what changed**

```bash
git status
```

**3. Commit it**

Add the files by name so nothing extra gets in, such as test quotes from `quotes/`:

```bash
git add templates/index.html static/style.css
git commit -m "Add intake form layout"
```

Write the message as a short command that says what the commit does:

| Good | Not useful |
| --- | --- |
| `Add quantity buttons to plan page` | `update` |
| `Fix room subtotal when an item is removed` | `fixed stuff` |
| `Add first 20 catalog items` | `asdf` |

**4. Push it**

```bash
git push -u origin frontend/intake-form   # first push on this branch
git push                                  # every push after that
```

Commit and push often, so your work is never only on your laptop.

**5. Open a pull request when the piece is ready**

1. Open the [repo on GitHub](https://github.com/DevOlabode/clinic.exe).
2. Click **Compare & pull request** on the banner for your branch.
3. Say what you changed and how you checked it.
4. Tell Role A in the group chat.

**6. After it's merged, go back to step 1**

Start a new branch for the next piece of work.

## Get the newest `main` into your branch

Do this if your branch has been open a while or you need something a teammate just merged:

```bash
git fetch origin
git merge origin/main
```

## When something goes wrong

**Merge conflict.** Open each file Git lists and find the `<<<<<<<` and `>>>>>>>` markers. Edit the section so it's correct, delete the markers, then run:

```bash
git add path/to/file
git commit
```

Run `git merge --abort` to back out and return to how things were. If the conflict is in a file another role owns, ask its owner before choosing a version.

**You edited files on `main` but haven't committed.** Move the changes to a new branch:

```bash
git switch -c frontend/my-work
```

**You committed on `main` but haven't pushed.** Run these in order. Your commits move to the new branch and `main` goes back to matching GitHub:

```bash
git switch -c frontend/my-work
git branch -f main origin/main
```

**The last commit message is wrong, and you haven't pushed.**

```bash
git commit --amend -m "Better message"
```

**You want to throw away your edits to a file.** This can't be undone:

```bash
git restore path/to/file
```

**You committed an API key.** Tell the team and revoke the key in its provider's dashboard right away, even if you haven't pushed. Then create a new key and put it in `.env`. Deleting the key in a later commit doesn't remove it from the history, so revoking is the fix.

**Stuck for more than 30 minutes?** Say so in the group chat, and don't force-push or delete your folder to get out of it.

## Team rules

- **Stay in your own files.** Each role owns its files (see Roles in [plan.md](plan.md)), which is how we avoid conflicts.
- **Huddle before changing the JSON contract.** If a change affects the formats in `plan.md`, take two minutes to agree on it first.
- **Keep secrets and real data out of the repo.** Never commit `.env` or paste keys in Discord, and never use real patient or client data.
- **Respect the freeze.** After the Sunday morning feature freeze, only bug fixes approved by Role A get merged.

## For Role A

1. Read the pull request's **Files changed** tab, then click **Merge pull request**.
2. Tell the team, so they know to pull the new `main`.
3. At the freeze, tag the demo version:

```bash
git switch main
git pull
git tag demo
git push origin demo
```
