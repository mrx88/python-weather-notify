workflow "Build" {
  on = "push"
  resolves = ["lint"]
}

action "lint" {
  uses = "./.github/workflows/lint.yml"
}
