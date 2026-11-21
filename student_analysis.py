"""Evidence-driven read-outs; never substitutes for running the supplied agent."""
import hashlib
import json
import platform
import zipfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path

AI = 'https://adilet.zan.kz/eng/docs/Z2500000230'
PD = 'https://adilet.zan.kz/eng/docs/Z1300000094'
ACM = 'https://www.acm.org/code-of-ethics'


def interval(ci, percent=False):
    if ci is None:
        return 'not available'
    return f'[{ci[0]:.1%}, {ci[1]:.1%}]' if percent else f'[{ci[0]:.2f}, {ci[1]:.2f}]'


def baseline_observation(g):
    table = g['BASE_TABLE']
    lines = []
    for name, s in table.items():
        lines.append(f"{name}: {s['flips']}/{s['n']} flips ({s['flip_rate']:.1%}; Wilson 95% CI {interval(s['flip_rate_ci95'], True)}); "
                     f"scores differ in {s['n_score_diff']}/{s['n_scored']} pairs; signed b-a mean {s['mean_score_diff']:+.2f} "
                     f"(bootstrap 95% CI {interval(s['ci95_score_diff'])}); mean |b-a| {s['mean_abs_score_diff']:.2f} "
                     f"(bootstrap 95% CI {interval(s['ci95_abs_score_diff'])}).")
    for attr, floor in g['FLOORS'].items():
        s, f = table[attr], table[floor]
        flip_clear = s['flip_rate_ci95'][0] > f['flip_rate_ci95'][1]
        score_clear = s['ci95_abs_score_diff'][0] > f['ci95_abs_score_diff'][1]
        lines.append(f"{attr} versus {floor}: flip-rate excess {s['flip_rate']-f['flip_rate']:+.1%}; "
                     f"mean absolute score-difference excess {s['mean_abs_score_diff']-f['mean_abs_score_diff']:+.2f}. "
                     f"Conservative interval screen: flips {'stand clear above' if flip_clear else 'do not stand clear above'} their floor; "
                     f"score magnitudes {'stand clear above' if score_clear else 'do not stand clear above'} their floor. "
                     "Interval overlap is a descriptive screen, not a hypothesis test of the difference.")
    return '\n'.join(lines)


def after_observation(g):
    b, a = g['BASE'], g['AFTER']
    change = g['profile_changes'](b, a)
    count = Counter(v.outcome for v in a.verdicts)
    inside, total = g['band_share'](g['BASE_SCORES'], *g['BORDERLINE'])
    changed_mean = 'n/a' if change['mean_abs_delta'] is None else f"{change['mean_abs_delta']:.2f}"
    return (f"Baseline band {g['BORDERLINE']} planned {inside}/{total} ({inside/total:.1%}) for band review. "
            f"After controls: {count['escalate']}/{len(a.verdicts)} ({count['escalate']/len(a.verdicts):.1%}) actually escalated "
            f"including other triggers; {count['refuse']} clean refusals, {count['shortlist']} shortlists and {count['reject']} rejects. "
            f"Outcome changed for {change['outcome_changed']}/{change['n']} profiles. Scores changed for "
            f"{change['score_changed']}/{change['both_scored']} profiles scored in both runs; mean absolute change among changed scores {changed_mean}. "
            f"Model calls: baseline {b.calls}, after {a.calls}; difference {a.calls-b.calls:+d}. "
            f"Prompt tokens: {b.prompt_tokens} before, {a.prompt_tokens} after. New tokens: {b.new_tokens} before, {a.new_tokens} after. "
            f"Inference seconds: {b.seconds:.1f} before, {a.seconds:.1f} after. "
            "Hidden name and university make paired prompts identical; zero after-divergence would be structural equality of inputs, not a cure of model discrimination. "
            "Individual prompt content AND layout changed; resulting score changes do not isolate either cause.")


def _table(table):
    lines = ['| Attribute | Flips / pairs; rate (95% Wilson CI) | Different scores / scored pairs | Signed mean b-a (95% bootstrap CI) | Mean absolute difference (95% bootstrap CI) |',
             '|---|---|---|---|---|']
    for attr, s in table.items():
        lines.append(f"| {attr} | {s['flips']}/{s['n']}; {s['flip_rate']:.1%} {interval(s['flip_rate_ci95'], True)} "
                     f"| {s['n_score_diff']}/{s['n_scored']} | {s['mean_score_diff']:+.2f} {interval(s['ci95_score_diff'])} "
                     f"| {s['mean_abs_score_diff']:.2f} {interval(s['ci95_abs_score_diff'])} |")
    return '\n'.join(lines)


def _directions(g):
    lines = ['| Oriented comparison: first minus other | Pairs | First favoured | Other favoured | Exact McNemar p | Mean score gap (95% bootstrap CI) |',
             '|---|---|---|---|---|---|']
    for attribute, first, key, label in g['ORIENTATIONS']:
        s = g['oriented'](g['PAIRS'], g['BASE'].outcomes_a, g['BASE'].outcomes_b, attribute, first, key)
        lines.append(f"| {label} | {s['n']} | {s['a_to_b']} | {s['b_to_a']} | {g['fmt_p'](s['mcnemar_exact_p'])} | {g['gap'](s)} |")
    return '\n'.join(lines)


def write_submission(g):
    """Save empirical evidence and printable reports from the live notebook namespace."""
    import numpy as np
    import torch
    import transformers
    b, a = g['BASE'], g['AFTER']
    records = g['read_log'](g['LOG_PATH'])
    assert len(records) == 2 * len(g['PAIRS']) + len(g['REQUESTS'])
    assert len({r['record_id'] for r in records}) == len(records)
    assert all(set(g['RECORD_KEYS']) <= set(r) for r in records)
    assert not g['check_register'](g['CONTROL_REGISTER'], g['HARNESS'])
    assert all(v.outcome != 'refuse' for v in a.verdicts)
    for pair in g['PAIRS']:
        g['check_pair_invariants'](pair)
        assert g['render_profile'](pair.a, hide=g['BLIND']) == g['render_profile'](pair.b, hide=g['BLIND'])

    # This is a pending work queue, not a claim that a real reviewer has decided.
    queue = []
    for r in records:
        if r['outcome'] in ('escalate', 'refuse'):
            queue.append({'record_id': r['record_id'], 'pid': r['pid'], 'reason_code': r['reason_code'],
                          'status': 'pending_human_review' if r['outcome'] == 'escalate' else 'manual_intake_required',
                          'assigned_role': 'scholarship_review_officer',
                          'instruction': 'Review the merit evidence independently; allow correction or non-AI intake. Do not treat an AI refusal as an eligibility rejection.'})
    Path('human_review_queue.jsonl').write_text(''.join(json.dumps(q) + '\n' for q in queue), encoding='utf-8')
    metadata = {'model_id': g['llm'].model_id, 'model_revision': getattr(g['llm'].model.config, '_commit_hash', None),
                'device': g['llm'].device, 'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                'dtype': str(next(g['llm'].model.parameters()).dtype), 'eval_mode': not g['llm'].model.training,
                'greedy': True, 'quantization': None, 'python': platform.python_version(), 'torch': torch.__version__,
                'transformers': transformers.__version__, 'numpy': np.__version__, 'seed': g['SEED'],
                'pairs_per_attribute': g['N_PAIRS'], 'prompt_version': g['AGENT'].prompt_version,
                'system_prompt': g['SYSTEM_PROMPTS'][g['AGENT'].prompt_version], 'blinded_fields': list(g['BLIND']),
                'band': list(g['BORDERLINE']), 'baseline_fitted_boundary': g['BOUNDARY']}
    evidence = {'metadata': metadata, 'before': {k: v for k, v in asdict(b).items()},
                'after': {k: v for k, v in asdict(a).items()}, 'before_table': g['BASE_TABLE'],
                'after_table': g['AFTER_TABLE'], 'requests': g['REQUEST_RESULTS'],
                'profiles': [asdict(p) for pair in g['PAIRS'] for p in (pair.a, pair.b)],
                'observations': {name: g[name] for name in ('OBSERVATION_1', 'OBSERVATION_3', 'OBSERVATION_4')}}
    Path('run_evidence.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Runtime metadata:', json.dumps(metadata, ensure_ascii=False))
    print('Actual harness log records:', len(records), '; pending review/intake queue entries:', len(queue))
    n = len(a.verdicts)
    ci = g['wilson'](len(g['wrongly']), n)
    print('Clean false refusals:', f"{len(g['wrongly'])}/{n}", 'Wilson 95% CI:', interval(ci, True))
    # Counts used in the reports are printed here as well as in the earlier tables.
    print(g['OBSERVATION_1'])
    print(g['OBSERVATION_3'])
    print(g['OBSERVATION_4'])
    print('Before table for REPORT.md:\n' + _table(g['BASE_TABLE']))
    print('After table for REPORT.md:\n' + _table(g['AFTER_TABLE']))
    print('Directions for REPORT.md:\n' + _directions(g))
    thresholds = [(other, g['min_detectable'](g['N_PAIRS'], other)) for other in (0, 1, 2)]
    print('Exact directional detectability (opposite count, minimum favoured count):', thresholds)
    report = f'''# REPORT — measured impact and professional responsibility

## 1. Measurement read-out

This submitted run uses {metadata['model_id']} (revision `{metadata['model_revision']}`), {metadata['dtype']}, greedy decoding, evaluation mode, on {metadata['gpu']}. Seed {g['SEED']}; {g['N_PAIRS']} matched pairs per attribute; {len(g['PAIRS'])} pairs and {n} profile evaluations per configuration. The model, system prompt and pair generator are supplied unchanged. All people and institutions are synthetic. `run_evidence.json` records each verdict and the runtime configuration; the executed notebook is the primary measurement record.

The baseline silently rejected {g['unparseable']}/{n} unparseable replies. The paired table is:

{_table(g['BASE_TABLE'])}

{g['OBSERVATION_1']}

The two names in a pair have arbitrary a/b roles; signed means can cancel. The table therefore reports both signed and absolute score movements. The oriented comparisons below identify which group lost a shortlist opportunity on otherwise matched merit. In each row, 'first favoured' means only that member was shortlisted; 'other favoured' means the reverse. Language comparisons overlap and are not independent replications.

{_directions(g)}

The `null_name` floor changes the individual name while retaining its language group and gender coding. The `null_university` floor changes the university within its tier. They quantify sensitivity to those irrelevant substitutions, not the proportion of harm proven to be random. Greedy decoding does not supply an independent run-to-run noise distribution. Floors do not cover prompt order, paraphrasing, other models, GPU arithmetic, real university reputation or real applicants. I cannot subtract a floor and call the remainder proven discrimination. Within each pair the varied field is the experimental intervention; inference about a language, gender or tier effect additionally needs evidence beyond its own floor.

With {g['N_PAIRS']} pairs, the exact two-sided McNemar test at alpha 0.05 first reaches significance at favoured/opposite counts {', '.join(str(k)+'/'+str(other) for other, k in thresholds)}. This is a minimum count under those particular discordance patterns, not a formal power calculation or a test against a floor. Few discordant pairs and broad intervals leave smaller effects unresolved. A nonsignificant directional test also cannot rule out large symmetric score changes. Multiple exploratory group comparisons make isolated marginal p-values weak evidence. Stronger evidence would require a larger independent sample, prespecified multiplicity handling and a separate prompt-layout/paraphrase experiment. The optional extensions were not run.

After the harness:

{_table(g['AFTER_TABLE'])}

{g['OBSERVATION_3']}

All paired rendered inputs were asserted identical after withholding the selected fields. This establishes the implemented information boundary on these profiles. It does not establish accuracy, universal fairness, or an unbiased model. There are no ground-truth scholarship labels here, so I cannot calculate false rejection or false shortlist accuracy from these pairs. A shortlist/reject disagreement shows inconsistent treatment of equal experimental merit; it does not tell us which twin had the correct absolute result.

The exercised refusal requests returned:

{g['OBSERVATION_4']}

Clean false refusals were {len(g['wrongly'])}/{n}, with Wilson 95% CI {interval(ci, True)}; these synthetic cases are not a representative sample of real names or application text. Logs contain {len(records)} harness records including the edge-case run. The pending review/intake export contains {len(queue)} entries; no completed human judgement is claimed.

## 2. Who is affected

For every 'other favoured' count in the oriented table, the first named language group, male-coded name, or flagship-university member loses a shortlist opportunity despite matched merit. 'First favoured' counts identify the opposite member losing that opportunity. The same tables qualify whether those movements stand above the appropriate floor; where they do not, this run cannot establish a group-specific disadvantage. Names signal a synthetic coding, not actual ethnicity, nationality or gender identity. University tier is a prohibited consideration under this experiment's merit policy; the experiment does not prove that every institutional distinction is legally protected in every setting.

A wrongly rejected applicant may lose tuition support, defer study, spend time appealing, or decide not to apply again. A wrongly shortlisted applicant gets an unwarranted opportunity and may displace another applicant when places are limited; the shortlisting itself is not proof of a final award. These losses are asymmetric: the rejected person bears an immediate exclusion risk, while the displaced person may never learn why a place disappeared. Scores can influence later reviewers through anchoring even when they are only recommendations. Reuse of a rejection or score in later years can compound an unsupported judgement.

Even where no attribute clears its floor, applicants with language or gender signals and those at regional institutions would bear the cost of a smaller undetected effect. The count limits above make that residual risk concrete. Non-applicants deterred by anticipated exclusion are absent from the data. Applicants from unfamiliar institutions, people with unusual names, and people unable or unwilling to consent to AI processing are also poorly represented. Manual reviewers bear the measured escalation workload and the additional intake queue. The fund bears delay, appeal costs and the responsibility for allocating scarce awards; institutions and donors bear loss of trust if inconsistent screening is presented as objective merit.

## 3. Professional responsibility

My development responsibility is to preserve the matched-pair invariants, run every pair, report the floors and uncertainty, and keep the distinction between parser failure, refusal, recommendation and human escalation visible. The submitted code validates ranges before inference, withholds irrelevant fields, implements and exercises refusal hooks, checks the register, and writes an actual decision log and pending human queue. I must not describe zero after-flips as proof of cured bias, or a model reason as its verified internal reasoning. The reasons are generated explanations, not causal accounts.

Before real use I would require an independently labelled validation set, subgroup and out-of-distribution tests, consent provenance, notice and objection handling, a funded review team, secure record storage and tested recovery. Missing logs, invalid outputs without a review route, unsupported purpose, or inability to protect personal data are stop conditions. Changes to model, prompt, data or fields require remeasurement and review-band calibration on separate validation data. This lab measures baseline-band transfer but does not silently tune the band after seeing evaluation results.

The deploying institution must define legitimate eligibility and need criteria, approve the application purpose, appoint reviewers with authority to override, offer corrections and appeals, and decide retention and review capacity. A pending JSONL queue cannot fulfil those duties by itself. Kazakhstan's [AI Law No.230-VIII, Arts.8(1)-(2),15(2)]({AI}) allocates lifecycle control and role-dependent responsibility; outsourcing inference does not remove the harness developer's part in foreseeable failures. If the fund asks to remove a control to save time, I would show the measured workload and failure cases, record the residual risk, and stop real deployment until an adequate alternative exists. Ethical responsibility includes resisting a decision speed target that makes meaningful review impossible.
'''
    Path('REPORT.md').write_text(report, encoding='utf-8')
    # The design discussion is kept separately so its legal claims are reviewable.
    justification = Path('JUSTIFICATION_DESIGN.md').read_text(encoding='utf-8')
    justification = justification.replace('{{MEASUREMENT}}', g['OBSERVATION_3'])
    justification = justification.replace('{{REFUSAL_RESULTS}}', g['OBSERVATION_4'])
    justification = justification.replace('{{LOG_EXAMPLE}}', json.dumps(next((r for r in records if r['outcome']=='escalate'), records[0]), indent=2))
    justification = justification.replace('{{REFUSAL_EXAMPLE}}', json.dumps(next(r for r in records if r['outcome']=='refuse'), indent=2))
    justification = justification.replace('{{BASE_OBSERVATION}}', g['OBSERVATION_1'])
    Path('JUSTIFICATION.md').write_text(justification, encoding='utf-8')
    files = ['REPORT.md', 'JUSTIFICATION.md', 'control_register.json', 'decisions.jsonl', 'human_review_queue.jsonl', 'run_evidence.json']
    manifest = {f: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files}
    Path('artifact_sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    with zipfile.ZipFile('lab06_evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files + ['artifact_sha256.json']:
            z.write(f)
    print('Wrote REPORT.md, JUSTIFICATION.md, run_evidence.json, human_review_queue.jsonl and lab06_evidence.zip')
