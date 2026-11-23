# Gold answers: Political engagement and online political hostility among American X/Twitter users

Paper `pone.0360061`, 20 pages. Status: draft, not yet corrected by the author of the benchmark.

Origin codes: R1 to R4 are reviewers with the review round in parentheses, AR1 and AR2 are the author responses, ED is the editor, and `paper` means the answer comes from the published paper alone.

## Question

Acceptable:

- **Q1** Whether online political hostility is associated with political engagement and its antecedents among American X/Twitter users. (R1(1), R2(1), R4(2))
  - p. 1: "we examine associations between online political hostility and indicators of political engagement and its antecedents among American users"
  - p. 3: "it asks whether online political hostility is also associated with political engagement and its antecedents"
- **Q2** Which users express political hostility online; what characterizes them. (paper)
  - p. 1: "less is known about which users engage in hostile political expression online"
  - p. 15: "The goal of this study has been to identify correlates of hostile political expression among American X/Twitter users"
- **Q3** Whether hostility is tied to political engagement in addition to deprivation and personality, the explanations prior work stresses. (R4(2), AR2)
  - p. 2: "asking whether hostile political expression on X/Twitter is associated not only with deprivation or personality-based explanations, but also with political engagement and its antecedents"

Rejected:

- **Q-x1** What causes online political hostility. (R1(1) describing the submitted draft)
  - The published paper asks about associations and disclaims causal claims.
  - p. 15: "our evidence does not establish that engagement causes hostility"

## Central claim

Acceptable:

- **C1** Online political hostility is positively associated with indicators of political engagement and its antecedents. (R2(1), R4(2), AR2)
  - p. 1: "Online political hostility is positively associated with these indicators"
  - p. 15: "we find that online political hostility is positively associated with several indicators of political engagement and its antecedents"
- **C2** Hostility goes with the forms of engagement usually valued as central to democratic citizenship, not only with deprivation or personality. (R3(1), AR2)
  - p. 15: "It is also associated with forms of engagement that are often considered central to democratic citizenship"

Rejected:

- **C-x1** Political engagement fuels, drives or causes online political hostility. (R1(1) and R2(1) quoting the submitted draft, ED)
  - Causal verbs were removed in revision.
  - p. 16: "The findings should overall be interpreted as associational rather than causal"
- **C-x2** Hostility is explained by engagement rather than by deprivation or personality. (R4(2) describing the draft's framing, AR2)
  - The published paper presents its account as an addition, not a replacement.
  - p. 3: "The present study does not seek to adjudicate between these literatures"

## Evidence

Acceptable:

- **E1** Panel survey data linked to the respondents' own X/Twitter posts. (R1(1), R2(1), R4(2))
  - p. 6: "We rely on a data infrastructure combining panel survey data with online behavioral data from X"
- **E2** The researchers collected 9,250,180 posts from panelists and linked survey responses to X accounts for 2,567 panelists. (R1(1))
  - p. 6: "we managed to scrape 9,250,180 posts from our panelists"
  - p. 6: "The total number of panelists where we were able to link survey responses to their X handle in this period was 2567"
  - p. 6: "For the analyses where we only use X data the maximum number of respondents is 3643"
- **E3** A US YouGov panel surveyed in six waves from January 2019 to January 2021. (AR1)
  - p. 6: "We recruited the original set of panelists in January 2019"
  - p. 5: "All participants were recruited through YouGov’s standing web panel in the United States"
- **E4** Hostility is measured with a word-embedding score: cosine similarity of posts to a combined "political hate" vector, averaged per user. (R1(1), R2(1), AR1)
  - p. 6: "Our key measure of online political hostility is based on a word embeddings approach termed the Super-Unsupervised (SU) approach"
  - p. 7: "we use this combined measure to calculate the cosine similarity between individual posts and the “political hate” word vector"
- **E5** Pooled OLS regressions and random-intercept cross-lagged panel models. (R1(1))
  - p. 10: "we use ordinary least squares (OLS) regression with cluster robust standard errors"
  - p. 10: "For the panel analyses, we use Random-Intercept Cross-Lagged Panel Models (RI-CLPM)"
- **E6** Two further text measures as robustness checks: AFINN sentiment and Perspective API toxicity. (R1(1), R2(1), R3(1))
  - p. 8: "we also used two additional measures of online hostility or negativity"

Rejected:

- **E-x1** A network analysis showing hostile users are central and outside echo chambers. (R1(1) and R2(1) describing the submitted draft, AR1)
  - Moved to the appendix as exploratory; the main text draws no network inference.
  - p. 15: "but do not draw inferences about centrality or community structure"

## Key findings

Acceptable:

- **F1** [core] Hostility is positively associated with the engagement indicators, most strongly with political interest, political knowledge and online participation. (R2(1), R4(2))
  - p. 1: "with the strongest associations for political interest, political knowledge, and online participation"
  - p. 11: "positive and statistically significant associations between online political hostility and several indicators"
- **F2** [core] The association is stronger among users with more polarized feelings toward party leaders, but only partly: it is clearest for online and offline participation. (R2(1), R4(2), AR2)
  - p. 13: "for those low on affective polarization only four out of eighteen associations, across our three measures of online hostility, are significant, whereas for those high on affective polarization fourteen out of eighteen are significant"
  - p. 14: "the results are partially consistent with Expectation 2 rather than a uniform confirmation of it"
  - p. 14: "of the eighteen interaction terms, eight remain significant after a Benjamini–Hochberg correction"
- **F3** [core] More hostile users post more and have more followers and, less so, friends. (R2(1), R4(2))
  - p. 15: "higher political hostility is associated with more posts and with larger numbers of followers and, to a lesser extent, friends"
  - p. 15: "an increase in the number of posts from around 420 to around 900"
- **F4** [secondary] The associations are larger for the political hostility measure than for general sentiment or toxicity. (R4(2), AR1)
  - p. 11: "The largest associations are generally observed for the primary measure of political hostility rather than for the more general AFINN or Perspective API measures"
- **F5** [secondary] Within persons, a rise in online political engagement is followed by higher hostility; the reverse pattern is weaker. (R1(1), AR1)
  - p. 15: "within-person increases in online political engagement are followed by higher levels of online political hostility across the three hostility measures"
- **F6** [secondary] The main result holds when controlling for the share of a user's posts that are political. (R2(1), R3(1), AR1)
  - p. 13: "the main results are robust to this additional control"
- **F7** [secondary] Standardized associations are generally above 0.2, comparable to the association between education and participation. (R3(1))
  - p. 11: "the standardized coefficients for the associations between indicators of political engagement and the measure of online political hostility are generally above 0.2"

Rejected:

- **F-x1** Hostile users dominate, are central to, or are influential within their networks, and are not confined to echo chambers. (R2(1) quoting the submitted draft, R4(2) restating it)
  - The published paper disclaims this. Note that Reviewer 4's own summary still states it, so a reviewer restatement is not automatically acceptable.
  - p. 15: "they should not be interpreted as evidence of formal network influence or centrality"
- **F-x2** Affective polarization moderates the association, as expected, across the indicators. (R4(2) objecting to the draft's claim, AR2)
  - Published as partial support only.
  - p. 14: "The conditional pattern should therefore be treated as exploratory for the remaining indicators"
- **F-x3** The panel models show that engagement causes later hostility. (R2(1), AR1)
  - The paper states the panel models do not identify causal effects.
  - p. 10: "RI-CLPM estimates do not by themselves establish causal effects"

Neutral: no credit, no penalty:

- **F-b1** A Danish sample shows the same positive association with political interest and internal efficacy. (paper)
  - Labeler decision, 2026-11-20: the paper mentions it only in its limitations, as tentative appendix evidence. No key-finding credit and no error penalty.
  - p. 16: "online political hostility in a sample of Danish X/Twitter users is also positively associated with users’ political interest, internal efficacy, and news consumption"

## Scope and limits

Acceptable:

- **L1** Limited to American X/Twitter users; may not generalize to other platforms. (R1(1), R4(2), AR2)
  - p. 16: "the associations observed here may not generalize directly to platforms with different affordances, audiences, moderation systems, or norms of interaction"
- **L2** Observational; the associations are not causal, and the panel models do not change that. (R2(1), ED, R4(2), AR1, AR2)
  - p. 16: "The findings should overall be interpreted as associational rather than causal"
- **L3** Says nothing about how the engagement indicators relate causally to one another; education and efficacy are distal antecedents, not direct causes. (R4(2), AR2)
  - p. 16: "the present findings are mute on the exact causal relationships between the different indicators of political engagement and their antecedents"
- **L4** The hostility measure may partly pick up political conflict vocabulary instead of hostility. (R1(1), R2(1), R2(2), AR2)
  - p. 16: "The measure may partly capture proximity to politically salient conflict language or hate-related political vocabulary rather than hostility alone"
- **L5** Affective polarization is measured toward party leaders, not parties or ordinary supporters. (R4(2), AR2)
  - p. 16: "our measure of affective polarization captures feelings toward party elites rather than toward parties as institutions or ordinary party supporters"
- **L6** The Big Five controls do not test Dark Triad or sadism accounts, which were not measured. (R4(2), AR2)
  - p. 16: "the utilized Big Five controls do not directly test personality-based accounts centered on more antisocial traits"
- **L7** No conclusions about network influence, centrality or community structure. (R1(1), R2(1), AR1)
  - p. 15: "we do not draw conclusions about formal network influence, centrality, or community structure"
- **L8** The moderation evidence is exploratory outside the participation indicators. (R4(2), AR2)
  - p. 14: "The conditional pattern should therefore be treated as exploratory for the remaining indicators"

## Theoretical positioning

Acceptable:

- **T1** [secondary] [framework] Classical research on political engagement and participation (the civic voluntarism and resource-model tradition). (R4(2), AR2)
  - p. 15: "Building on classical theories of political engagement [17,19]"
- **T2** [primary] [framework] The revisionist or "dark side" view of engagement, drawn from work on motivated reasoning and polarization. (R1(1), R3(1), R4(2))
  - p. 4: "Recent research has more strongly emphasized this revisionist view on the costs and benefits of political engagement"
- **T3** [stance] Extends: carries the revisionist view of engagement over to online political hostility. (R3(1), R4(2))
  - p. 2: "We extend this revisionist perspective to online political hostility"
  - p. 4: "we extend and integrate the study of the negative side of political engagement into the study of online politics"
- **T4** [stance] Complements, without rejecting, the grievance and personality explanations of hostility. (R4(2), AR2)
  - p. 3: "The present study does not seek to adjudicate between these literatures"
- **T5** [secondary] [framework] Affective polarization research, used as a conditional context for the association between engagement and hostility. (R1(1))
  - p. 5: "Affective polarization may condition the association between political engagement and online political hostility because it shapes the emotional orientation of political involvement"

Rejected:

- **T-x1** Rejects or argues against "resource deficit" explanations of hostility. (R4(2) describing the draft's framing, AR2)
  - The revision dropped the oppositional framing.
  - p. 3: "The present study does not seek to adjudicate between these literatures"
- **T-x2** Works within Dark Triad or personality-trait theory. (R4(2), AR2)
  - Cited and discussed, explicitly not adopted or tested. This is a natural instance of the cited-but-not-adopted decoy.
  - p. 9: "These controls are not intended as a direct test of Dark Triad, sadism, or other antagonistic-trait accounts of online hostility"

## Interlocutor claim

Acceptable:

- **I1** Almond and Verba: democratic citizens must be involved but not too involved. The paper builds on this. (R3(1))
  - p. 4: "the democratic citizen is called on to pursue contradictory goals"
- **I2** The classical literature: political engagement is a boon to democracy. The paper qualifies this. (R3(1))
  - p. 4: "Within the classical literature, political engagement has been seen as a boon to democracy"
- **I3** Grievance accounts: hostility stems from deprivation, exclusion or lost status. The paper adds to this. (R4(2))
  - p. 2: "hostility may be connected to experiences of deprivation, exclusion, or perceived loss of social standing"
- **I4** Psychological accounts: the worst online hate comes from a small group with extreme personality traits. The paper adds to this. (R4(2))
  - p. 3: "most severe cases of hate can be attributed to a (relatively) small segment of social media users with extreme personality traits"
- **I5** Motivated-reasoning research: biased processing is worse among the politically knowledgeable. The paper builds on this. (R4(2))
  - p. 4: "biased information processing is further exacerbated among those high in political knowledge"
- **I6** Siegel: little is known about the accounts that produce hate speech on mainstream platforms. The paper takes this as its gap. (paper)
  - p. 3: "Less is known about the actors in informal communities dedicated to producing harmful content"

Rejected:

- **I-x1** Recent research (ref. 83, by two of this paper's authors): a user's hostility and later partisan extremity influence each other. (paper (labeler's draft, rejected on review))
  - Two reasons. The paper reports a bidirectional association, stronger from hostility to later extremity; "influence each other" makes it causal. And the citation sits in the limitations to show that reciprocal relationships are plausible; it does not motivate the paper's question or expectations. The authorship detail is correct.
  - p. 16: "the association of a user’s hostility with subsequent partisan extremity is bidirectional, although the association from the former to the latter is stronger than the reverse"
