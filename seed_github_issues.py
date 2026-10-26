"""Turn the camp datasets in data/ into GitHub Issues in the training repository.

Dry run by default: prints the `gh` commands it would run. Nothing is created
until you pass --run, and then only in the repository you name. Run it from
the repository root:

    python3 seed_github_issues.py OWNER/REPO
    python3 seed_github_issues.py OWNER/REPO --run

Requires the GitHub CLI (`gh`), signed in with an account that can create
issues in OWNER/REPO. Use a training repository, never a real project.
"""
import argparse
import json
import shlex
import subprocess
import sys
import time

DATASETS = ['engineering_delivery', 'program_release', 'leadership_portfolio']


def body(issue):
    lines = [
        f"**Training data — synthetic.** Issue `{issue['key']}` from `data/{issue['_file']}`.",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    fields = [
        ('Status', issue['status']),
        ('Priority', issue['priority']),
        ('Risk', issue.get('risk')),
        ('Program', issue.get('program')),
        ('Release', issue.get('release')),
        ('Owner', issue.get('owner') or '— (none)'),
        ('Team', issue.get('team')),
        ('Due', issue.get('due') or '— (none)'),
        ('Last updated', f"{issue['updated_days_ago']} days ago (as of the dataset)"),
        ('Blocked by', ', '.join(issue.get('blocked_by') or []) or '—'),
        ('Blocks', ', '.join(issue.get('blocks') or []) or '—'),
    ]
    lines += [f'| {k} | {v} |' for k, v in fields if v is not None]
    lines += ['', '## Description', '', issue.get('description') or '—', '', '## Acceptance criteria', '']
    criteria = issue.get('acceptance_criteria') or []
    lines += [f'- {c}' for c in criteria] if criteria else ['— (none written)']
    comments = issue.get('comments') or []
    if comments:
        lines += ['', '## Comments', '']
        for c in comments:
            lines.append(f"- *{c['author']}, {c['days_ago']} days ago:* {c['body']}")
    return '\n'.join(lines)


def labels(issue):
    out = [f"dataset:{issue['_dataset']}", f"status:{issue['status']}", f"priority:{issue['priority']}"]
    if issue.get('program'):
        out.append(f"program:{issue['program']}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('repo', help='OWNER/REPO of the training repository')
    ap.add_argument('--data', default='data', help='folder holding the three dataset files (default: data)')
    ap.add_argument('--run', action='store_true', help='actually create labels and issues')
    args = ap.parse_args()

    issues = []
    for name in DATASETS:
        for issue in json.load(open(f'{args.data}/{name}.json', encoding='utf8'))['issues']:
            issue['_file'], issue['_dataset'] = f'{name}.json', name.replace('_', '-')
            issues.append(issue)
    commands = []
    for name in sorted({l for i in issues for l in labels(i)}):
        commands.append(['gh', 'label', 'create', name, '--repo', args.repo, '--force'])
    for i in issues:
        cmd = ['gh', 'issue', 'create', '--repo', args.repo,
               '--title', f"[{i['key']}] {i['summary']}", '--body', body(i)]
        for l in labels(i):
            cmd += ['--label', l]
        commands.append(cmd)

    if not args.run:
        for c in commands:
            print(' '.join(shlex.quote(p) if '\n' not in p else "'<body>'" for p in c))
        print(f'\nDry run: {len(issues)} issues for {args.repo}. Re-run with --run to create them.', file=sys.stderr)
        return
    for c in commands:
        subprocess.run(c, check=True)
        time.sleep(1)  # stay well under GitHub's content-creation rate limits
    print(f'Created {len(issues)} issues in {args.repo}.')


if __name__ == '__main__':
    main()
