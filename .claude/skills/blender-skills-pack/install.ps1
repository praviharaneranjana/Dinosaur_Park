# Run from the Dinosaur_Park repo root (the folder that contains .claude, Assets, design ...)
# Copies the skills into .claude\skills WITHOUT overwriting anything that already exists.
$ErrorActionPreference = 'Stop'
$src = Join-Path $PSScriptRoot 'skills'
$dst = Join-Path (Get-Location) '.claude\skills'
New-Item -ItemType Directory -Force -Path $dst | Out-Null
$added = 0; $skipped = 0
Get-ChildItem -Path $src -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($src.Length).TrimStart('\')
  $target = Join-Path $dst $rel
  if (Test-Path $target) { $skipped++ } else {
    New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
    Copy-Item $_.FullName $target; $added++
  }
}
Copy-Item (Join-Path $PSScriptRoot 'SKILLS_GUIDE.md') (Join-Path (Get-Location) '.claude\skills\SKILLS_GUIDE.md') -ErrorAction SilentlyContinue
$n = (Get-ChildItem $dst -Recurse -Filter SKILL.md).Count
Write-Host "Added $added files, skipped $skipped existing. SKILL.md count in .claude\skills: $n"
Write-Host "Now paste AGENTS_SNIPPET.md into AGENTS.md (and CLAUDE.md if you use one)."
