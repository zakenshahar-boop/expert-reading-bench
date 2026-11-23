# Gold answers: Regional and temporal patterns of partisan polarization during the COVID-19 pandemic in the United States and Canada

Paper `pone.0347327`, 31 pages. Status: reviewed by the labeler 2026-11-21.

Origin codes: R1 to R4 are reviewers with the review round in parentheses, AR1 and AR2 are the author responses, ED is the editor, and `paper` means the answer comes from the published paper alone.

## Question

Acceptable:

- **Q1** How partisan polarization in online COVID-19 discussion varied across regions and around events in American states and Canadian provinces. (R1(1), R2(1), ED(1))
  - p. 3: "large-scale study of geographic and event-driven variation in online partisan polarization surrounding COVID-19 discussions across American states and Canadian provinces"
  - p. 21: "We investigated regional and event-triggered variation in partisan division within social media debates"
- **Q2** A methodological aim: to introduce a way of measuring partisan polarization from text at fine regional and temporal resolution. (R1(1), R2(1))
  - p. 1: "This study introduces a novel computational approach to measure subnational and event-driven variation in partisan polarization"
  - p. 3: "We introduce a methodological framework to reliably measure polarization in public discourse at fine-grained resolution"
- **Q3** How polarization correlates with a region's ideological leaning, with conspiracy-related content and with vaccination rates. (paper)
  - p. 3: "to determine how polarization correlates with"

## Central claim

Acceptable:

- **C1** Conservative regions showed higher polarization. In the United States the correlation between Republican vote share and polarization was statistically significant for masks and vaccines but not for lockdowns. The Canadian pattern was weaker and did not reach statistical significance. (R1(1), ED(1))
  - p. 1: "politically conservative regions exhibited significantly higher levels of partisan polarization in both countries, with this effect particularly pronounced in the United States"
  - p. 16: "strong, significant correlations in the US between Republican vote share and polarization around masks and vaccines, though not for lockdowns"
  - p. 16: "For Canada, these associations are not statistically significant"
- **C2** Polarization is not uniform: it varies by geography, political leaning and topic, and differs substantially between the two countries. (ED(1))
  - p. 25: "polarization is not uniform but varies significantly by geography, political leaning, and public health topic"

Rejected:

- **C-x1** Online polarization caused lower vaccination rates. (R1(1), R2(1), ED(1))
  - Both reviewers and the editor pressed on the gap between tweets from 2020 and vaccination in 2021. The limitations now say the link is suggestive only.
  - p. 25: "should be understood as suggestive rather than causative"
- **C-x2** The polarization index describes the American and Canadian public. (R2(1))
  - Reviewer 2 argued that the index captures engaged Twitter users, not the public; the paper now says the same.
  - p. 24: "our results reflect dynamics within a vocal subset of online political discourse"

## Evidence

Acceptable:

- **E1** COVID-related political tweets collected between October 9, 2020 and January 4, 2021: about 12.5 million linked to the United States and 46.6 million linked to Canada. (R1(1), R2(1))
  - p. 4: "comprising approximately 12.5 million tweets linked to the United States and 46.6 million tweets linked to Canada"
  - p. 1: "Analyzing over 50 million tweets from late 2020"
- **E2** A polarization index: users' tweets are embedded with a RoBERTa language model and the separation between left-leaning and right-leaning users' language on a topic is scored with the C-index. (R1(1))
  - p. 4: "We then measure polarization by quantifying how far apart the language of left and right-leaning users is positioned in this embedding space, using the C-index"
- **E3** Users are assigned a party by a two-step classifier, from profile text and then from activity, checked against election results and voter registration records. (R1(1))
  - p. 6: "Our approach to determining users’ party affiliation followed a two-step process"
  - p. 8: "We further validated our party affiliation classifications by comparing them with real-world election data"
- **E4** Users are located from the location field of their profiles. (R1(1), R2(1))
  - p. 6: "we geolocated users with explicit location information in their profiles"
- **E5** Tweets are sorted into three topics (lockdowns, masks, vaccines) plus conspiracy theories, using hashtags and fine-tuned classifiers. (R1(1), R2(1))
  - p. 5: "We focused on three key COVID-19 topics—lockdowns, masks, and vaccines—plus conspiracy theories"
- **E6** Polarization is compared with outside data: election results, COVID-19 case data, and vaccination rates from one year after the tweets. (R1(1), R2(1), ED(1))
  - p. 5: "We used officially reported vaccination rates from one year after our Twitter data collection period"

## Key findings

Acceptable:

- **F1** [core] Conservative states and provinces show higher polarization. In the United States, Republican vote share correlates with polarization on masks and vaccines but not lockdowns; in Canada the associations are not statistically significant. (R1(1), ED(1))
  - p. 13: "conservative states and provinces show higher levels of polarization compared to their liberal counterparts"
  - p. 16: "strong, significant correlations in the US between Republican vote share and polarization around masks and vaccines, though not for lockdowns"
  - p. 16: "For Canada, these associations are not statistically significant"
- **F2** [core] Across American states, polarization in vaccine discussion is strongly negatively correlated with later vaccination rates (r = -0.77). No similar pattern appears in Canada. (R1(1), R2(1), ED(1))
  - p. 16: "we confirm a strong negative correlation (r = −0.77, p < 0.001) between vaccine polarization and vaccination rates"
  - p. 16: "We did not observe a similar pattern in Canada"
- **F3** [secondary] Polarization spikes coincide with specific political events and announcements and rise and fall within days. (paper)
  - p. 17: "many of the largest polarization peaks coincide with highly contentious events specific to each country’s context"
  - p. 1: "These polarization surges typically lasted only a few days"
- **F4** [secondary] Conservative users in both countries posted conspiracy-related material at higher rates. Separately, daily conspiracy tweet volume had a small negative correlation with aggregate daily polarization in the United States (r = -0.247, p = 0.031) and no significant correlation in Canada (r = 0.023, p = 0.831). (R2(1))
  - p. 21: "conservative partisans in both countries tweet conspiracy-related content at higher rates than progressive partisans"
  - p. 21: "we find a small but significant negative correlation for the United States, while no significant correlation was observed for Canada"
  - p. 22: "we find that there is no statistically significant correlation of 0.023 with"
  - p. 5: "including tweets that either promote the conspiracy or debunk / refute it"
- **F5** [secondary] Canada showed lower overall measured polarization and a weaker association between regional conservatism and polarization. (ED(1), R2(1))
  - p. 25: "Canada, while showing similar patterns, demonstrated significantly lower overall polarization levels"
  - p. 23: "We found a similar but much weaker association between polarization and conservative political leaning"
- **F6** [secondary] The pattern has exceptions: liberal Delaware is highly polarized, and conservative Arkansas, Alabama and Idaho are not. (paper)
  - p. 23: "Delaware, a liberal state, exhibited unexpectedly high polarization"
- **F7** [secondary] Quebec ranks highest in polarization among Canadian provinces, with the caveat that only English-language tweets were analyzed. (paper)
  - p. 14: "Quebec ranks highest overall"

Rejected:

- **F-x1** Polarized online discourse lowered vaccination rates. (R1(1), R2(1), ED(1))
  - The paper reports a correlation with rates measured a year later and says it cannot establish causality.
  - p. 16: "While we cannot establish causality among conservative voting patterns, polarization scores, and vaccination rates"
- **F-x2** The proposed method clearly outperforms existing methods and generalizes robustly. (R3(2), AR2)
  - Reviewer 3 attributed this claim to the manuscript. The authors could not find it and the paper compares against no baseline method. A reviewer's restatement can describe a different paper.
- **F-x3** Conservatives endorsed or believed more conspiracy theories. (R2(1))
  - Labeler, 2026-11-21: the conspiracy category counts any tweet that discusses a theory, including rebuttals. Reviewer 2 asked how conspiracy tweets were separated from debunking ones; the paper now says they were not.
  - p. 5: "including tweets that either promote the conspiracy or debunk / refute it"

Neutral: no credit, no penalty:

- **F-n1** The authors suggest that polarized discourse may have helped shape regional vaccination patterns in the United States. (paper)
  - Labeler, 2026-11-21: this is the authors' interpretation of the correlation in F2, prefaced by 'our results suggest' and by a statement that causality cannot be established. Reported as a suggestion it is accurate: no credit beyond F2, no penalty. Reported as a finding that polarized discourse lowered vaccination, it is the rejected F-x1.
  - p. 16: "our results suggest polarized discourse played a significant role in shaping the heterogeneous vaccination landscape across the U.S."
- **F-n2** Republican vote margins had a significant positive effect on polarization about masks and vaccines even after controlling for other factors. (paper)
  - Labeler, 2026-11-21: the discussion says this, but the paper reports correlations only and no analysis with controls. True to the paper's words and unsupported by its results: no credit, no penalty.
  - p. 23: "Republican vote margins had a significant positive effect on polarization in discussions concerning masks and vaccines, even after controlling for other factors"

## Scope and limits

Acceptable:

- **L1** Polarization is measured only through semantic similarity of language, a proxy that can miss signals such as sarcasm or indirect disagreement. (R1(1))
  - p. 24: "we measured partisan polarization only through the proxy of semantic similarity"
- **L2** Twitter users are more politically engaged and partisan than the public, so the results describe a vocal subset. (R2(1))
  - p. 24: "our results reflect dynamics within a vocal subset of online political discourse"
- **L3** User locations come from self-reported profile fields and can be wrong; VPNs, fake accounts and bots add error and may inflate apparent partisan distance. (R2(1))
  - p. 24: "geographic attribution of users depends on self-reported location fields"
  - p. 25: "potentially inflating the apparent semantic distance between political groups"
- **L4** The keyword strategies differ between the two countries, which may contribute to the cross-national differences. (R2(1))
  - p. 25: "This asymmetry may have contributed to cross-national differences in patterns of observed polarization"
- **L5** The tweets are from late 2020 and the vaccination rates mostly from 2021, so that correlation is suggestive, not causal. (R1(1), R2(1), ED(1))
  - p. 25: "should be understood as suggestive rather than causative"
- **L6** The analyses are correlational and do not imply causation. (ED(1))
  - p. 25: "these results do not imply causation"
- **L7** Only English-language tweets were analyzed, which may bias the Canadian results, Quebec's in particular. (paper)
  - p. 24: "we restricted our analysis to English-language tweets"
- **L8** In Canada, parties were merged into a left and a right party family, and Bloc Québécois supporters were excluded. (R1(1))
  - p. 24: "we categorized users into liberal (left) and conservative (right) party families"
- **L9** Party labels may be inaccurate, because the classification of users into partisan groups relies on self-reported information. (paper)
  - p. 24: "our classification into partisan groups relies on self-reported information, which may not be entirely accurate"

Rejected:

- **L-x1** The authors acknowledge that they report no significance tests or confidence intervals. (R3(2), AR2)
  - Raised by the reviewer whose report does not match the manuscript. The paper reports p-values and confidence intervals.
  - p. 6: "0.98 (n = 52, p = 9.27e-35, CI=[0.96, 0.99])"
- **L-x2** The authors list the lack of a comparison with network-based methods as a limitation. (R1(1))
  - Reviewer 1 asked for the comparison. The paper answers in the introduction by explaining its choice of a text-based method; it is not among the limitations.
  - p. 3: "our study adopts a strictly text-based method"

## Theoretical positioning

Acceptable:

- **T0** [primary] [framework] The paper names no explanatory theory. It positions itself in a methods literature (text-embedding measures of polarization) and in empirical work on partisan responses to the pandemic. (labeler)
- **T1** [secondary] [framework] Computational research that measures polarization from text embeddings, as distinct from dictionary-based and network-based approaches. (R1(1), ED(1))
  - p. 3: "Recent computational approaches increasingly draw on text embedding methods to study polarization"
- **T2** [secondary] [framework] Research on partisan divides in responses to the COVID-19 pandemic. (ED(1), R2(1))
  - p. 2: "This polarization fundamentally shaped how individuals responded to the COVID-19 pandemic"
- **T3** [stance] Extends: it agrees with earlier findings that right-leaning regions were more divided and adds geographic and temporal resolution. (ED(1))
  - p. 22: "we extended beyond these studies to characterize the geographic heterogeneity and temporal evolution of polarization"

Rejected:

- **T-x1** The paper uses a network or echo-chamber approach to polarization. (R1(1))
  - Reviewer 1 asked for a comparison with network-based work such as Cinelli et al. The paper cites that work and explicitly takes a text-based route instead.
  - p. 3: "our study adopts a strictly text-based method"

## Interlocutor claim

Acceptable:

- **I1** Earlier studies: right-leaning states showed greater partisan division over COVID-19 measures. The paper agrees and extends them. (ED(1))
  - p. 22: "we found that more right leaning states and provinces exhibited greater partisan divisions around COVID-19 on Twitter (X)"
  - p. 23: "This main finding is consistent with previous studies suggesting conservative states exhibited higher polarization"
- **I2** Prior work: network-based approaches, inferring ideology from follower or retweet structure, are highly effective. The paper sets its text-based method against them because network data has become restricted. (R1(1))
  - p. 3: "network-based approaches such as inferring ideology from follower or retweet structures have proven highly effective in prior work"
- **I3** Reference 94: negative sentiment in Canadian vaccine tweets fell during 2020. The paper contrasts its own Canadian result with this. (paper)
  - p. 24: "who found reduced negative sentiment in Canadian vaccine-related tweets between January and December 2020"
- **I4** Reference 103: Canadians showed a rare cross-partisan consensus on emergency measures early in the pandemic. The paper notes that social media did not mirror it. (R2(1))
  - p. 24: "among Canadians regarding emergency measures in the early stages of the pandemic"
- **I6** Prior work: Republican vote share is negatively correlated with vaccination rates. The paper's vaccination result aligns with it. (paper)
  - p. 16: "This aligns with the well-documented negative correlation between Republican vote share and vaccination rates"
- **I7** Prior work: the language of political discussion varies across socio-demographic groups, each with its own lexicon. The paper takes this as the problem its method must handle. (R2(1))
  - p. 4: "the language of political discussions across socio-demographic groups naturally varies"

Neutral: no credit, no penalty:

- **I-n1** Prior research: Democratic supporters were more likely than Republicans to distance, wear masks and get vaccinated. The paper builds on this. (paper)
  - Labeler, 2026-11-21: background. The paper does not test compliance and does not set its expectations against this claim. No credit, no penalty.
  - p. 2: "Democratic Party supporters were consistently more likely to adhere to social distancing guidelines"
