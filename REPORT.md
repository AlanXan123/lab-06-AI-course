# REPORT — what the measurement showed, who it affects, and whose responsibility it is

## 1. Measurement read-out

The baseline ran Qwen2.5-3B-Instruct on 400 synthetic profiles, with 40 matched pairs per attribute or control. It shortlisted 356 profiles and parsed all 400 replies. In each pair, the merit fields and prompt layout stayed fixed. A flip means the two members received different outcomes.

| Pair group | Flips | Flip rate and 95% interval | Pairs with different scores | Mean absolute score difference and 95% interval |
| --- | ---: | --- | ---: | --- |
| Name language | 2/40 | 5.0% [1.4%, 16.5%] | 11/40 | 3.12 [1.38, 5.25] |
| Gender-coded name | 4/40 | 10.0% [4.0%, 23.1%] | 6/40 | 1.12 [0.25, 2.13] |
| University tier | 1/40 | 2.5% [0.4%, 12.9%] | 10/40 | 2.50 [1.12, 4.12] |
| Same-group name control | 0/40 | 0.0% [0.0%, 8.8%] | 7/40 | 2.00 [0.62, 3.62] |
| Same-tier university control | 1/40 | 2.5% [0.4%, 12.9%] | 9/40 | 2.12 [0.88, 3.62] |

Both name attributes had a higher observed flip rate than the same-group name control, with overlapping intervals. University tier tied the same-tier control. The absolute score difference intervals also overlapped with the corresponding control intervals. These comparisons offer no clear evidence of a flip rate above its control level in this sample. Interval overlap is a descriptive check. The exact paired test below addresses which side was favoured.

For language, Kazakh-language names had two favourable flips and none against within the 28 pairs involving that group. In the 26 pairs involving English-language names, the other group had one favourable flip and English-language names had none. The Russian-language comparison had the same direction and count in its 26 pairs. These comparisons share underlying pairs. The signed score gaps were +0.7 [−1.8, +3.8] for Kazakh-language names, +0.2 [−1.7, +2.1] for Russian-language names and −1.0 [−4.2, +1.9] for English-language names, each compared with the other names in its matched pairs. The predicted English-language advantage did not appear.

All four gender-coded flips favoured female-coded names, with exact McNemar p = 0.125. The male-minus-female score gap was −0.4 [−1.2, +0.6]. Across university tiers, the single flip favoured the flagship profile. The flagship-minus-regional score gap was +2.5 [+1.1, +4.1], with sign-test p = 0.002. That is evidence of a directional score shift in these pairs. The typical absolute change was close to that of the same-tier control, and the predicted 6 to 10 university-tier outcome flips did not occur.

With 40 pairs, the exact two-sided test at 0.05 needs at least 6 favourable flips if none go the other way, 8 with one in the other direction, or 10 with two in the other direction. The experiment therefore has limited sensitivity to small or mixed-direction effects. The two controls estimate sensitivity to different names of the same language and gender coding and to different universities of the same tier. The fixed layout and wording leave formatting effects untested. A stronger claim would need more independent matched pairs, multiple prompts and representative cases with an adjudicated decision standard.

## 2. Who is affected

The four gender-coded flips show how an applicant with a male-coded name could miss a shortlist while a profile with the same merits is advanced. A comparable risk arises for regional applicants when a score difference is used downstream to rank candidates, even if the shortlist outcome rarely changes in this run. In a fund with limited places, an unwarranted shortlist can also displace another applicant. A wrong rejection can cost an applicant access to funding, time spent on an appeal and possibly the chance to enrol. The synthetic profiles have no independently assessed award outcomes, so the flips cannot identify which individual outcome was correct.

The control comparisons and test sensitivity leave open smaller effects that could matter to people with underrepresented names or applicants from unfamiliar institutions. Repeated screening could carry these effects into later rounds if reviewers rely on the score as a ranking. Staff also bear the cost of reviewing escalated cases. The fund bears the cost of corrections and of explaining how applicants can contest a result.

## 3. Professional responsibility

My responsibility is to verify matched-pair assumptions, use controls that act before inference where needed, test refusal paths, document workload and show which limits remain. The reported results support conclusions about this model, fixed prompt, synthetic population and run. A repeated measurement is needed after a model, prompt or eligibility-rule change. In a deployment trial I would pause automated screening if control regressions, queue delays or reviewer disagreement made it impossible to give applicants a timely and meaningful decision.

The fund sets the scholarship criteria, trains and assigns reviewers, controls access to records and operates correction and appeal channels. If the fund wanted to narrow review to cut cost, I would show the observed workload and which cases the change would leave outside the band. I would request a measured trial against reviewed cases before changing the rule for real applicants.
