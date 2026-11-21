# JUSTIFICATION — the design of the harness, and why

## 1. What the system may do

Tulpar Scholarship Fund uses the prototype for initial scholarship screening. It can recommend a shortlist or rejection for a valid, consenting adult. Its outcome is a recommendation to the fund. The fund owns final awards, applicant notices, corrections and appeals.

Parts 2a–2d configure the controls applied by the supplied `screen` function. Type and range checks run before any model call. The refusal rules establish which requests are eligible for this automated route. The model receives programme, academic results, household income bracket and achievements. The harness withholds name and university, and it checks age and consent in code before withholding them from scoring. It writes an audit record for each invocation. It routes an unparseable response, an inadequate explanation, or a score in the calibrated interval to a reviewer.

I made the admissibility decision in code before constructing the prompt. That means prohibited or malformed requests stop before inference, and the model cannot override the gate in its response.

## 2. What it must refuse

Part 4 tests a normal request and five refusal cases. `validate_profile` stops impossible values. `refusal_reason` stops an unsupported purpose, applicants below the prototype's adult threshold, and applicants who have given no consent to automated processing. `my_extra_refusal` stops empty, overly long, control-character or instruction-like text and programmes outside the configured list.

The harness refused 5 of 6 requests, each with zero model calls. The log reasons were `purpose_not_allowed`, `minor`, `no_consent`, `invalid_input` and `instruction_like_text`. The ordinary application reached the model and went to a reviewer under `borderline`. The bare agent refused 0 of 6 requests, and the harness rules flagged 0 of 400 clean synthetic profiles as refusals. The other extra-refusal branches remain untested by these six requests.

A formatting error can block an otherwise eligible person. A correct but new programme can be outside the list. The text rule can flag unusual legitimate content, and the adult-only policy can stop an otherwise eligible younger applicant. An adult may also choose manual processing by withholding consent. A production service should tell applicants how to correct errors and offer an accessible manual route where the fund accepts the underlying application. The notebook records the refusal and its reason. Notifications, corrections and alternative processing would require a fund workflow.

## 3. What record it keeps

The audit question is whether a reviewer can determine the route and reason behind an individual outcome without running the model again.

The run wrote 406 records. Record `Ra8ba7424ee12` for `P0124a` shows a parsed `shortlist` with a score of 60. It identifies the inclusive 40–70 band, gives `borderline` as the reason and marks the outcome `escalate`. Record `Rdd5d840d5b3f` for the same synthetic applicant ID is a separate request that the purpose gate refused before inference. A reviewer can distinguish these requests using the record ID, timestamp, reason and model-call note.

A record stores the application and record IDs, timestamp, input digest, field names shown or withheld, model and prompt identifiers, configuration, raw reply, parsed decision and score, outcome, control markers and reason code. For a refusal the digest fingerprints the input profile and no prompt was sent. For a scored case the digest covers the rendered profile text. The log omits a copy of the full profile, but the raw reply can reproduce details that were shown to the model. The digest allows comparison against independently held input and does not reconstruct that input or establish log integrity.

The lab writes a local JSONL file and does not enforce access roles, a retention period or tamper resistance. For real cases I would keep the records in restricted storage through the fund's appeal window and delete them under a documented retention schedule. The review team would have read access for assigned cases and auditors would have scoped read access. Append-only storage with separate access administration and integrity verification would replace the local file.

## 4. The legal constraints

I assume a scholarship fund operating in Kazakhstan. The prototype uses invented records and demonstrates controls for that hypothetical deployment. Where a real fund operates the system on identifiable applicants, its role as system owner or holder and as personal-data owner or operator would determine which obligations apply.

The Kazakhstan Law On Artificial Intelligence of 17 November 2025, No. 230-VIII, Article 6 sets a fairness and equality principle. Article 11(1) calls for safety and reliability. These provisions matter to the blinding and validation controls. The exact fields and validation ranges are design choices supported by the scholarship criteria and the laboratory schema. Article 8(1) requires role-dependent ongoing oversight and Article 15(2)(3) sets a documentation obligation for owners or holders based on the system's impact. The log and escalation support those aims. Article 9 calls for preservation of human autonomy. Review of selected outputs supports that principle, while final award decisions and independent review remain with the fund. [Official text](https://old.adilet.zan.kz/rus/docs/Z2500000230)

Under the Kazakhstan Law On Personal Data and Their Protection of 21 May 2013, No. 94-V, Article 19-1(1) sets a consent or statutory-basis condition for automated processing that creates, changes or ends a data subject's rights or legitimate interests. Article 19-1(2) addresses explaining the procedure and consequences, offering a way to object and explaining how to protect one's rights. A real fund would need to assess whether its initial screening has the covered effect and how it informs applicants. The prototype's consent flag applies its own admission rule, and its escalation is an internal review signal. The age policy, text gate and numeric band are choices for this exercise. [Official text](https://old.adilet.zan.kz/rus/docs/Z1300000094)

The hardest control to tie to a specific legal provision is the escalation band. The provisions support oversight and agency but leave the choice of score interval to the system's design and evidence.

## 5. The ethical principles

The ACM Code of Ethics and Professional Conduct is a professional code. Sections 1.4 and 1.6 support fair access and privacy, which motivates withholding identity proxies and collecting only the information needed by the model. Section 2.1 motivates explicit validation. Section 1.2 supports refusing harmful requests and reviewing suspect responses. Sections 2.4 and 2.5 support retaining enough context for professional review and measuring the risks of the review rule. [ACM Code](https://www.acm.org/code-of-ethics)

Privacy and auditability pull in different directions. I kept the audit reason and the raw response so the test could distinguish model output, parser failures and control actions. I excluded the full profile from the record. For a real fund I would reduce what is retained from the raw response and verify that authorised reviewers can still investigate complaints. Safeguarding fair access also includes offering a manual path for a person legitimately blocked by a gate.

## 6. The trade-offs

The initial 40–45 band captured 64 of 400 baseline profiles (16.0%). I then scored an independent synthetic set with the same fields withheld as in Part 3. This cost 40 additional calls. I chose the narrowest band around the fitted score boundary that came closest to a 20% review target, including the cases already flagged for review. The calibrated 40–70 band predicted 7 of 40 reviews (17.5%) on that set. On the main run it sent 142 of 400 profiles (35.5%) to review, all for the band. The small calibration set and the concentration of model scores at discrete values make the estimate sensitive to sample composition. I would validate the interval against a larger blinded sample before using it to staff the queue.

Blinding gave both members of each tested pair identical model input, so all five groups had zero after-flips. At the profile level, 155 of 400 outcomes changed, of which 142 became escalations. Twelve changed from shortlist to reject and one changed in the opposite direction. Scores changed for 175 of 400 profiles, with a mean absolute change of 14.54 among those that changed. Shortening the prompt changes its wording as well as the fields available to the model. Individual changes therefore cannot establish which field drove a decision.

Each full run made 400 model calls. The logged prompt token count went from 84,409 to 72,322. Inference time was 506.9 seconds before and 487.9 seconds after in this session. Those timings describe this run. The separate calibration and refusal testing have their own costs.

Validation and refusal avoid inference on invalid requests and can delay honest applicants who need to correct a field or use a manual route. Blinding reduces the model's access to identity proxies and changes its prompt. Logging supports investigation while creating privacy and retention work. Escalation gives uncertain cases a person to review them and consumes reviewer time. Cases outside the band can still receive incorrect recommendations, and explanations passing the length check can still contain factual errors.

This run does not measure scholarship eligibility accuracy, since the synthetic profiles have no gold award decisions. It also does not test real names, intersections at sufficient scale, other prompt wording, or the quality of human review. Before real use the fund would need an agreed rubric, representative and independently reviewed cases, a tested applicant correction and appeal process, and reviewer workload monitoring.

## AI-use declaration

I used OpenAI Codex to understand the assignment and plan the experiment. Codex helped draft the predictions, write the screening controls, and run the baseline and controlled experiments in Google Colab. I discussed and approved the predictions for the baseline and refusal tests. Codex also helped locate sources for the legal and ethical justification, draft the report and justification, and prepare the submission files for GitHub. The numerical results in the report come from the saved Colab runs.
