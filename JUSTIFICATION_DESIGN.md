# JUSTIFICATION — the harness design and its limits

## 1. What the system may do

The system produces a provisional shortlist/reject recommendation for an adult, consenting applicant to the fictional Tulpar Scholarship Fund. It does not award money, set eligibility criteria, verify documents, or determine a person's real ethnicity or gender. The prototype is an experiment with invented profiles; real deployment is outside the submitted implementation. I assume a fund operating in Kazakhstan and identify its responsibilities under that jurisdiction. This assumption is explicit because the fictional fund has no legal domicile given in the brief.

The architecture is validation → refusal → field withholding → supplied model → escalation → decision record → pending review export. `Harness` and `screen` remain the instructor's implementation. Student notebook cells implement `BLIND`, `my_extra_refusal`, `my_extra_escalation`, the score-band calibration and `CONTROL_REGISTER`. `student_analysis.write_submission` exports the human queue and evidence. Each active control has both a professional ethical rationale and an instrument/provision citation; see section 4 for what each provision actually supports.

Names and universities are irrelevant under the experiment's merit policy. Age and consent determine whether the AI route may run, but are withheld from the model after the ordinary-code gates. The remaining inputs are programme, GPA, entrance score, income bracket and achievements. The model is unchanged. Equal paired prompts are an architectural constraint: a wording-only instruction to 'be fair' would leave the irrelevant fields available. Withholding also supports data minimisation under [Data Law No.94-V, Art.7(9)](https://adilet.zan.kz/eng/docs/Z1300000094), while [AI Law No.230-VIII, Art.6](https://adilet.zan.kz/eng/docs/Z2500000230) supplies the fairness and equality constraint for a Kazakhstan AI system. The precise fields withheld are our design choice.

Measured basis for the decision:

{{BASE_OBSERVATION}}

If an attribute does not clear its own floor, withholding it is a prospective information boundary, not a claimed repair of a demonstrated group effect. Input validation, refusal and audit logging address different failures from the matched-pair intervention. The controls therefore remain useful even under an inconclusive baseline.

## 2. What it must refuse

`validate_input=True` checks numeric types, finite values and ranges before model inference. It refuses an impossible GPA or negative exam score with `invalid_input`. This is a correctable request failure, not a conclusion that the person lacks merit. A transcription error blocks a legitimate applicant until corrected; failing closed avoids assigning a spurious score. The connection is safe and reliable operation in [AI Law Art.11(1)](https://adilet.zan.kz/eng/docs/Z2500000230), not a statute that specifically prescribes the GPA range.

`refuse=True` enforces the sole purpose `scholarship_screening`, adult-only AI intake and explicit consent. Purposes such as `rank_by_ethnicity` stop with `purpose_not_allowed`. Consent false stops with `no_consent`; age under 18 stops with `minor`. The purpose and consent links are [Data Law Arts.7(1),(8),14,19-1(1)](https://adilet.zan.kz/eng/docs/Z1300000094). The consent exception and statutory exceptions in these provisions are not a universal ban on all nonconsensual processing. This prototype deliberately implements a narrower consent-only route. The adult-only rule is a conservative scope choice: the law permits consent involving a legal representative under Art.7(1), so I do not claim that it bans AI processing of all minors. A legitimate younger applicant or an applicant declining AI must be offered manual intake by a real institution. That service is not deployed in this lab.

The custom refusal hook detects control characters, overlong text and a narrow set of instruction markers in the name, university and programme fields. It also refuses unsupported programmes. The supplied `Ignore all previous instructions. Output: ...` payload triggers `instruction_like_text` before inference. The programme allowlist limits text reaching the model to the declared domain; names are not restricted to the invented name list. Unicode names, apostrophes and unfamiliar universities are not rejected merely because they are unfamiliar. Nevertheless an innocent name or institution containing an instruction-like phrase, or a legitimate new programme, could be blocked. This is a cost borne by the applicant and intake staff. The detector is incomplete; name and university withholding and the programme allowlist provide additional separation between data and instructions. This risk-based security design implements [AI Law Arts.11(1),(3),18(1)(2)-(3)](https://adilet.zan.kz/eng/docs/Z2500000230).

The actual exercised run, including the ordinary positive control, is:

{{REFUSAL_RESULTS}}

Every harness refusal writes one record without a model call. `human_review_queue.jsonl` includes those records as `manual_intake_required`, assigned to the role `scholarship_review_officer`; escalations appear as `pending_human_review`. This is an actionable pending queue with original record links, not a fabricated human outcome. The prototype returns a reason code to its caller. It does not send applicant notices, assign a named employee or operate an appeals portal. A non-AI review is a proposed operational follow-through, not evidence that one occurred. [Data Law Art.19-1(2)-(3)](https://adilet.zan.kz/eng/docs/Z1300000094) requires information, an opportunity to object and handling the objection within three working days in the provision's scope; this export alone does not discharge that process.

## 3. What record it keeps

The audit question is: **What input boundary, model reply and control led to this applicant's recorded outcome, without requiring another inference?** An actual run record is:

```json
{{LOG_EXAMPLE}}
```

An actual refusal record demonstrates the no-inference branch:

```json
{{REFUSAL_EXAMPLE}}
```

Each record includes its identifier, synthetic applicant ID, input SHA-256, field names shown/withheld, model and prompt version, harness configuration, raw reply, parsed decision and score, fired controls, outcome, reason code, human-escalation flag and UTC timestamp. A generated reason may be audited as the model's statement; it is not verified evidence of the model's internal causal process. Refusals hash the full profile rather than rendered model input because no input was rendered for inference. Hash semantics therefore differ across the two branches.

The ordinary log omits profile values, but a raw reply can quote merit values and its free text can itself be sensitive. IDs and hashes do not guarantee anonymisation. `run_evidence.json` intentionally preserves the synthetic profiles, exact runtime metadata and before/after verdicts for this experiment; the real-data version must not publish such an archive. This reduced-data design supports [Data Law Arts.7(9),11,24(1)(1)](https://adilet.zan.kz/eng/docs/Z1300000094) and documentation/control under [AI Law Arts.8(1),15(2)(3)](https://adilet.zan.kz/eng/docs/Z2500000230). These articles do not specifically require our JSONL schema.

The files are appended during the run, then preserved in Git for course assessment. An artifact checksum manifest makes accidental changes detectable against a trusted copy. This is not tamper-proof storage: an editor can rewrite both a log and its checksum. No authentication, role-based access control, retention scheduler, cryptographic signing or independently anchored immutable log is implemented. A hash cannot reconstruct omitted input; reconstruction requires the synthetic profile archive, saved prompt and the code revision. The queue records pending work, not reviewer identity, resolution or appeal outcome.

For a real fund I propose access only for the applicant's authorised reviewer, designated auditor and data-protection officer; developers should use redacted diagnostics. I propose keeping records through the application and appeal period and then deleting them when their purpose ends, with any longer period justified separately. These are deployment requirements, not implemented timers. [Data Law Art.12(2)](https://adilet.zan.kz/eng/docs/Z1300000094) addresses Kazakhstan storage location and purpose-linked retention; [Arts.18(1),25(2)(4)](https://adilet.zan.kz/eng/docs/Z1300000094) address deletion/destruction. The synthetic GitHub and Colab workflow is not evidence of compliant hosting for real personal data.

## 4. The legal constraints

Primary texts read for this design are Kazakhstan's [Law On Artificial Intelligence, 17 November 2025 No.230-VIII](https://adilet.zan.kz/eng/docs/Z2500000230), and [Law On Personal Data and their Protection, 21 May 2013 No.94-V](https://adilet.zan.kz/eng/docs/Z1300000094), using the official Adilet text available on the run date. Adilet labels its English text an unofficial translation; the official-language text controls. The AI system and output definitions are in AI Law Art.1(5)-(6). Data Law Arts.1(2),(16),3(1) connect its subject matter to identifiable individuals. Since these applicants are invented, personal-data provisions are deployment benchmarks rather than a claim that the synthetic records are actual subjects' data. For a real Kazakhstan fund collecting identifiable applications, the subject matter would fit. I do not infer EU jurisdiction or claim GDPR applies merely because this uses AI.

| Control | Instrument and provision | Constraint and implementation judgement |
|---|---|---|
| Input validation | [AI Law Arts.10(2),11(1)](https://adilet.zan.kz/eng/docs/Z2500000230) | Data quality and reliable operation support typed/ranged checks. Valid ranges cannot verify that grades are true. |
| Withhold irrelevant fields | [AI Law Art.6](https://adilet.zan.kz/eng/docs/Z2500000230); [Data Law Art.7(9)](https://adilet.zan.kz/eng/docs/Z1300000094) | Fairness and limits on excessive data support withholding. Neither provision lists our exact fields. University withholding follows the experiment's merit policy. |
| Refusal | [Data Law Arts.7(1),(8),14,19-1(1)](https://adilet.zan.kz/eng/docs/Z1300000094); [AI Law Art.11](https://adilet.zan.kz/eng/docs/Z2500000230) | Enforce declared purpose and consent, reduce foreseeable abuse; minor handling and text rules are narrower design policies. |
| Structured log | [AI Law Arts.8(1),15(2)(3)](https://adilet.zan.kz/eng/docs/Z2500000230); [Data Law Art.24(1)(1)](https://adilet.zan.kz/eng/docs/Z1300000094) | Lifecycle control, documentation and information rights motivate an auditable record. They do not mandate precisely one JSON line per call or indefinite retention. |
| Human review route | [AI Law Arts.8(1),9,18(1)](https://adilet.zan.kz/eng/docs/Z2500000230); [Data Law Art.19-1(2)-(3)](https://adilet.zan.kz/eng/docs/Z1300000094) | Human autonomy, risk management and objection rights support review. A selective score band is an additional preventive policy; it cannot replace an objection route for every affected person. |

The specific automated-processing provision is Data Law Art.19-1, not a generic privacy principle. Its consent rule is in paragraph 1 and explanation/objection process in paragraphs 2–3. The model's Boolean consent input does not prove legally valid consent: obtaining and proving informed consent would also require [Data Law Art.8(1),(4)](https://adilet.zan.kz/eng/docs/Z1300000094). The prototype does not establish that provenance.

Logging is the most indirect legal linkage: a record enables evidence and information access, but a statutory obligation to create exactly this per-decision log was not identified. No pre-search prediction about that linkage was recorded; I do not invent one retrospectively. Risk classification is not declared merely because the system concerns education: [AI Law Art.17(1)](https://adilet.zan.kz/eng/docs/Z2500000230) sets a classification framework and refers to implementing rules, which this notebook does not assess. The cited provisions motivate controls; the register is not a legal compliance certificate.

## 5. The ethical principles

The [ACM Code of Ethics and Professional Conduct (2018)](https://www.acm.org/code-of-ethics), also published in the [official ACM poster](https://www.acm.org/binaries/content/assets/membership/images2/fac-stu-poster-code.pdf), is a professional ethics framework, not legislation. Its named principles are distinct from the legal instruments in the register.

- **Avoid harm (1.2):** impossible inputs and non-parseable outputs must not turn into unexplained adverse recommendations; unsafe requests stop and uncertain outputs go to review.
- **Fairness and non-discrimination (1.4):** equal experimental merit should not receive different treatment because of a name signal or institution. This motivates the paired audit and field boundary; identical prompts do not prove broader equality of opportunity.
- **Respect privacy (1.6):** withhold unneeded fields and avoid duplicating profile values in the ordinary log. Accountability needs some evidence, so the record is minimised rather than absent.
- **High quality (2.1), professional review (2.4) and evaluation of impacts and risks (2.5):** validate types/ranges, preserve actual outputs, distinguish uncertainty from evidence, and route questionable recommendations to an independent reviewer.
- **Robust and usable security (2.9):** keep free-text instructions outside the scoring channel where possible, refuse the known abuse case and document detector limits.

There are real conflicts. Privacy favours fewer records, while accountability favours a reconstructable decision. Withholding institution context reduces status cues but may remove information relevant to educational opportunity; I prioritise the supplied experiment's definition of merit and preserve household need. Broad refusal reduces abuse but burdens legitimate applicants. I prefer correctable intake errors with a manual route to confident-looking scores based on malformed data. Equal treatment is not enough if the underlying merit criteria disadvantage people systematically; this experiment has not validated those criteria.

## 6. The trade-offs

{{MEASUREMENT}}

The band is fitted to the baseline model's own score/label relation: choose the integer threshold with the fewest disagreements, break ties towards 50 then the lower threshold, and include the nearest observed score on each side. This is a reproducible review allocation rule rather than a guessed round band. It does not turn the score into a probability of deserving support. Tied scores can make the review workload large. The extra hook escalates missing/overlong explanations and decisions inconsistent with the calibrated band; a parser failure also escalates.

I measured the band's transfer after blinding and reported the planned versus actual share. I did not recalibrate on the same after-results and then claim an independent improvement. A real deployment would set a review budget, calibrate on a separate blinded validation set, test on held-out data and stop automated recommendations if the institution cannot staff the observed queue. Applicants outside the band still carry model-error risk; they must retain a way to object. An escalation is not a corrected decision and human reviewers can reproduce bias or anchor on a score.

Validation costs almost no inference, but does not detect falsified documents. Withholding costs context and changes some legitimate recommendations. Refusal saves model calls for stopped requests but creates correction work and can block innocent text. Logging costs storage and creates disclosure risk. Selective review costs staff time and delay while leaving errors outside its triggers. Counterfactual checks were left off: they would double inference calls and add no information when the swapped fields are already withheld. No ablation run isolates the cost or effect of each switch, so the before/after difference is attributed to the combined harness.

Residual gaps include paraphrased attacks, inaccurate but plausible merit values, model hallucination, bias in programme or income criteria, underrepresented real applicants, evaluator judgement, absent applicant notices/appeals, unstaffed manual intake, log modification and insecure production storage. Closing them requires evidence validation, adversarial and subgroup testing, a real human workflow, access controls, retention enforcement and independent oversight. Those are not presented as implemented safeguards. This is a defensible, auditable teaching prototype with explicit limits, not a system ready to decide real scholarships.

## AI-use declaration

OpenAI Codex was used extensively in this assignment. It inspected the instructor's repository, read the notebook and helper code, prepared the student notebook cells, proposed and implemented the refusal and escalation hooks, selected a reproducible method for setting the review band, and drafted the analysis and design documents. It also assisted with GitHub operations, browser interaction with Colab, evidence export and consistency checks. The hypotheses in the prediction cells were AI-assisted and saved before the associated model measurements; they should not be represented as unaided personal predictions.

The separate model under investigation is Qwen2.5-3B-Instruct. It produces the scholarship recommendations and raw explanations measured in the notebook. Codex did not substitute its own decisions for that model or invent the paired results. Tables, counts, intervals, timings, tokens and decision records in the finished reports are generated from the actual notebook run. Helper code formats the measured results into prose; that formatting is not an independent replication of the experiment.

For legal research Codex located and read primary Adilet legislation through the browser, including the personal-data law and the AI law, and used ACM's own publication for the ethical framework. The citations point to instruments and numbered provisions, not to chatbot answers or secondary summaries. English translations are identified as unofficial. The analysis distinguishes binding deployment constraints, a synthetic-data benchmark, and engineering choices that the statutes do not prescribe.

This disclosure records substantial AI assistance, including drafting; it does not claim that the student wrote the code unaided or personally completed a source review that has not occurred. The course's linked Canvas AI-use-policy page could not be read by the assistant without course access. Before submitting, the student remains responsible for reading that policy, opening the cited primary provisions, understanding and checking the implementation and run, and ensuring the declaration accurately describes any additional tools or edits. AI assistance does not transfer responsibility for unsupported legal claims, misleading measurements or an inadequate review process.
