# Git Commands Memo

## Check the current branch
- git branch

## Get the latest branch
- git switch (branch-name)
- git pull origin (branch-name)

## Create a new branch
- git switch -c (new-branch-name)

## Check changes
- git status

## Check the changed content
- git diff ("q" on keybord is the command to finish)

## Save changes
- git add (file-name)
- git add .
- git commit -m "Describe the change"

## Push the branch to GitHub
- git push origin (branch-name)
- git push

## Check the commit history
- git log --onelile

## Cancel an unstaged change
- git restore (file-name)


## Basic workflow
1. git switch main
2. git pull origin main
3. git switch -c new-branch-name
4. Edit files
5. git status
6. git add file-name
7. git commit -m "Describe the change"
8. git push -u origin new-branch-name
9. Create a Pull Request on GitHub
10. Merge into main