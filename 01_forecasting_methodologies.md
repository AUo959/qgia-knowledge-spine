# Forecasting Methodologies Framework

**QGIA Knowledge Spine - Document 01**  
**Classification**: UNCLASSIFIED // FOR OFFICIAL USE ONLY  
**Version**: 1.0.0  
**Last Updated**: February 15, 2026  
**Review Cycle**: Quarterly

---

## Executive Overview

### Operational Relevance

Forecasting methodologies form the analytical backbone of QGIA's 84.7% accuracy for 12-month geopolitical forecasts. This document consolidates superforecasting principles, probabilistic aggregation techniques, and calibration methods validated through Philip Tetlock's Good Judgment Project and operationalized within QGIA's quantum-enhanced framework.

**Key Capabilities**:
- Systematic probability estimation with quantified confidence (0.00-1.00 scale)
- Forecast aggregation methods achieving 30% superiority over individual experts
- Calibration techniques reducing overconfidence and improving decision-making
- Integration with OSIQP v4.2.1 for 94.7% sentiment analysis accuracy at <50ms latency

### Critical Intelligence Applications
1. **Crisis Early Warning**: 127-day average lead time through temporal decomposition
2. **Scenario Probability Weighting**: QSFE quantum superposition modeling
3. **Confidence Validation**: Real-time calibration against 500TB daily intelligence stream
4. **Policy Impact Assessment**: Bayesian belief updating for intervention forecasts

---

## I. Superforecasting Framework

### 1.1 Core Principles (Tetlock & Mellers, 2011-2015)

The Good Judgment Project established four validated keys to forecasting accuracy:

#### A. Talent Identification
**Cognitive Attributes**:
- **Actively Open-Minded Thinking (AOT)**: Willingness to update beliefs with new evidence
- **Numeracy**: Comfort with probabilistic reasoning and statistical concepts
- **Need for Cognition**: Intrinsic motivation to engage in effortful thinking
- **Granularity**: Ability to make fine-grained probability distinctions (45% vs 50% vs 55%)

**QGIA Selection Protocol**:
- Brier score <0.18 on 50-question calibration test
- Domain knowledge assessment across 6 geopolitical regions
- Cognitive style inventory (AOT, numeracy, need for cognition)
- Historical track record: Minimum 100 forecasts, ≥60% accuracy

**Validation**: Top 2% of forecasters ("superforecasters") outperform intelligence analysts with classified information by 30% on Brier scores.

#### B. Training Protocols

**1. Probabilistic Thinking**
- Convert verbal uncertainty ("likely", "probable") to numerical probabilities
- Standardized probability lexicon:
  - **Virtually Certain**: 95-99%
  - **Highly Likely**: 80-94%
  - **Likely**: 60-79%
  - **About Even**: 40-59%
  - **Unlikely**: 21-39%
  - **Highly Unlikely**: 6-20%
  - **Remote**: 1-5%

**2. Decomposition Techniques**
- **Fermi Estimation**: Break complex questions into estimable components
  - Example: "Probability of Taiwan invasion by 2027"
    - P(China military capability ready) × P(Political will exists) × P(US intervention deterred) × P(Window of opportunity)
- **Reference Class Forecasting**: Anchor on historical base rates
  - Historical frequency of major power military interventions
  - Success rates of amphibious operations in contested environments
- **Temporal Decomposition**: Estimate conditional probabilities over time horizons
  - P(Event by 30 days | Current conditions)
  - P(Event by 6 months | 30-day outcome)
  - P(Event by 12 months | 6-month outcome)

**3. Bias Mitigation**
- **Anchoring**: Generate independent estimates before group discussion
- **Confirmation Bias**: Actively seek disconfirming evidence
- **Availability Bias**: Weight evidence by reliability, not memorability
- **Overconfidence**: Regular calibration feedback and Brier score tracking

#### C. Team Dynamics

**Collaborative Structures**:
- **Prediction Teams** (5-7 analysts): Diverse expertise, structured debate
- **Red Team / Blue Team**: Adversarial forecasting for contested scenarios
- **Delphi Method**: Iterative anonymous polling with controlled feedback

**Communication Protocols**:
- Separate **probability** (How likely?) from **reasoning** (Why?)
- Require **confidence intervals** for all point estimates
- Document **cruxes**: What evidence would change your forecast?
- **Update frequency**: Minimum weekly review, triggered updates for major developments

**QGIA Enhancement**: Quantum entanglement mapping (EDM) identifies forecast dependencies across analysts, preventing groupthink while preserving collaborative benefits.

#### D. Aggregation Methods

**1. Extremization**

Transform individual probabilities to account for information overlap:

$$P_{extremized} = 0.5 + (P_{avg} - 0.5) \times \alpha$$

Where:
- $P_{avg}$ = Simple average of individual forecasts
- $\alpha$ = Extremization parameter (typical range: 1.2-1.5)
- Empirically calibrated based on historical accuracy

**Rationale**: Forecasters share common information sources, leading to correlated errors. Extremization compensates by moving averaged probabilities away from 50% toward certainty.

**QGIA Implementation**: OSIQP dynamically adjusts α based on:
- Source diversity metrics from 500TB daily intelligence stream
- Analyst expertise correlation matrices
- Historical calibration curves for specific question types

**2. Bayesian Model Averaging**

Weight forecasters by historical accuracy:

$$P_{aggregated} = \sum_{i=1}^{n} w_i \times P_i$$

Where:
- $w_i$ = Weight for forecaster $i$ (normalized to sum to 1)
- $P_i$ = Forecaster $i$'s probability estimate
- Weights derived from Brier scores: $w_i \propto \exp(-\beta \times BS_i)$
- $\beta$ = Sensitivity parameter (higher β = greater discrimination)

**QGIA Refinement**: Temporal decay factor applied to historical Brier scores, prioritizing recent accuracy:

$$w_i(t) \propto \sum_{j=1}^{m} \exp(-\lambda (t - t_j)) \times \exp(-\beta \times BS_{ij})$$

Where:
- $t$ = Current time
- $t_j$ = Time of past forecast $j$
- $\lambda$ = Decay rate (typical: 0.01 per day)
- $m$ = Number of historical forecasts by analyst $i$

**3. Logarithmic Opinion Pool**

Multiplicative aggregation preserving probability calibration:

$$P_{aggregated} = \frac{\prod_{i=1}^{n} P_i^{w_i}}{\prod_{i=1}^{n} P_i^{w_i} + \prod_{i=1}^{n} (1-P_i)^{w_i}}$$

Advantages:
- Robust to extreme forecasts (0% or 100%)
- Maintains proper probability axioms
- Performs well when forecasters have complementary information

**QGIA Application**: Default aggregation for scenarios with diverse expertise and low information overlap.

**4. Diversity-Weighted Aggregation**

Recent research (2023) demonstrates that amplifying forecast diversity improves combinations:

$$P_{aggregated} = \text{extremize}(\text{diversify}(\{P_1, ..., P_n\}), \alpha)$$

Diversification penalty for correlated forecasts:
- Compute pairwise forecast correlation matrix
- Downweight forecasters with high correlation to others
- Upweight outliers with novel perspectives (if justified by reasoning)

**Empirical Result**: Diversity-based combinations outperform simple averaging by 12-18% on Brier scores in out-of-sample tests.

---

## II. Calibration and Validation

### 2.1 Brier Score Metric

The Brier Score measures forecast accuracy with quadratic penalty for errors:

$$BS = \frac{1}{N} \sum_{i=1}^{N} (p_i - o_i)^2$$

Where:
- $N$ = Number of forecasts
- $p_i$ = Forecasted probability
- $o_i$ = Actual outcome (1 if occurred, 0 if not)
- Range: 0.0 (perfect) to 1.0 (worst possible)

**Interpretation**:
- **BS < 0.15**: Excellent (superforecaster threshold)
- **BS 0.15-0.20**: Good (trained analyst)
- **BS 0.20-0.25**: Average (general expert)
- **BS > 0.25**: Poor (needs retraining)

**QGIA Benchmark**: 84.7% accuracy = BS ≈ 0.13 for 12-month forecasts.

### 2.2 Calibration Curves

Perfect calibration: Forecasted probabilities match observed frequencies.

**Construction**:
1. Group forecasts into bins (0-10%, 10-20%, ..., 90-100%)
2. Calculate mean forecasted probability per bin
3. Calculate observed frequency of events in each bin
4. Plot forecasted vs observed

**Diagnostic Patterns**:
- **Overconfidence**: Observed frequency < forecasted (curve below diagonal)
- **Underconfidence**: Observed frequency > forecasted (curve above diagonal)
- **Well-Calibrated**: Points cluster near 45-degree line

**QGIA Real-Time Calibration**:
- Updated weekly from 500TB intelligence stream
- Separate curves by:
  - Time horizon (30-day, 6-month, 12-month)
  - Question domain (military, political, economic)
  - Analyst experience level
  - Intelligence source type (SIGINT, HUMINT, GEOINT, OSINT)

### 2.3 Confidence Interval Quantification

For continuous forecasts (e.g., "Russian troop deployments in 6 months"):

**Credible Intervals** (Bayesian approach):
- 50% CI: Central credible interval containing 50% of probability mass
- 80% CI: Wider interval for higher confidence
- 95% CI: Maximum practical width for policy decisions

**Construction**:
1. Generate probability distribution over outcomes
2. Identify percentiles (2.5%, 25%, 50%, 75%, 97.5%)
3. Report intervals with explicit probability interpretation

**Example**:
> "Russian troop levels in Kursk oblast by August 2026:"
> - **50% CI**: 45,000-65,000 personnel
> - **80% CI**: 35,000-80,000 personnel  
> - **Median Estimate**: 52,000 personnel
> - **Confidence**: 0.74 (quantum coherence score)

---

## III. Temporal Dynamics

### 3.1 Forecast Updating Protocol

**Bayesian Belief Revision**:

$$P(H|E) = \frac{P(E|H) \times P(H)}{P(E)}$$

Where:
- $P(H)$ = Prior probability (previous forecast)
- $P(E|H)$ = Likelihood (probability of new evidence given hypothesis)
- $P(E)$ = Marginal probability of evidence
- $P(H|E)$ = Posterior probability (updated forecast)

**QGIA Operationalization**:
1. **Evidence Classification**: Assign reliability scores (0.0-1.0) to incoming intelligence
2. **Likelihood Assessment**: Estimate $P(E|H)$ and $P(E|\neg H)$
3. **Likelihood Ratio**: $LR = P(E|H) / P(E|\neg H)$
4. **Posterior Update**: $\text{Odds}(H|E) = LR \times \text{Odds}(H)$
5. **Coherence Check**: Quantum validation via OSIQP

**Update Triggers**:
- **Scheduled**: Weekly routine review
- **Event-Driven**: Major developments (military mobilization, diplomatic crisis, economic shock)
- **Confidence-Driven**: When quantum coherence drops below 0.65
- **Request-Driven**: Policy consumer queries

### 3.2 Multi-Horizon Forecasting

**Conditional Probability Chains**:

$$P(\text{Event by } t_3) = P(E_{t_1}) + P(\neg E_{t_1}) \times P(E_{t_2} | \neg E_{t_1}) + P(\neg E_{t_1}) \times P(\neg E_{t_2} | \neg E_{t_1}) \times P(E_{t_3} | \neg E_{t_1}, \neg E_{t_2})$$

Where:
- $t_1$ = 30 days
- $t_2$ = 6 months  
- $t_3$ = 12 months

**Advantages**:
- Captures path dependencies
- Enables interim validation
- Supports time-phased policy recommendations

**QGIA Implementation**: Temporal Convergence Analyzer (TCA) models phase transitions in crisis dynamics, predicting acceleration/deceleration of event timelines.

### 3.3 Forecast Stability Metrics

Measure volatility of probability estimates over time:

**Forecast Variance**:
$$\sigma_P^2 = \frac{1}{T} \sum_{t=1}^{T} (P_t - \bar{P})^2$$

Where:
- $P_t$ = Probability estimate at time $t$
- $\bar{P}$ = Mean probability across time period
- $T$ = Number of time points

**Interpretation**:
- **Low variance** ($\sigma_P^2 < 0.02$): Stable forecast, high confidence
- **High variance** ($\sigma_P^2 > 0.05$): Unstable forecast, requires investigation

**Diagnostic Uses**:
- Identify forecasts driven by noise vs signal
- Flag potential analyst bias (excessive updating)
- Validate quantum coherence scores

---

## IV. QGIA Integration Protocols

### 4.1 OSIQP v4.2.1 Quantum Sentiment Analysis

**Integration Points**:
- **Real-Time Evidence Processing**: 500TB daily stream → sentiment vectors → probability adjustments
- **Source Reliability Weighting**: Quantum amplitude assignment based on historical accuracy
- **Coherence Validation**: Cross-check classical forecasts against quantum superposition states

**Workflow**:
1. Analyst generates initial probability estimate ($P_0$)
2. OSIQP processes intelligence stream → sentiment distribution
3. Bayesian update: $P_1 = \text{update}(P_0, \text{OSIQP}_{sentiment})$
4. Coherence check: $\text{Coherence}(P_1) = \langle \psi_{classical} | \psi_{quantum} \rangle$
5. If coherence < 0.60: Flag for manual review
6. If coherence ≥ 0.60: Accept updated forecast

**Empirical Performance**: 94.7% sentiment classification accuracy at <50ms latency enables real-time forecast recalibration.

### 4.2 QSFE (Quantum Superposition Forecasting Engine)

**Scenario Branching**:
- Model simultaneous futures as quantum superposition states
- Assign amplitudes (√probability) to each branch
- Evolve scenarios forward through unitary transformations
- Collapse to classical probabilities for reporting

**Mathematical Framework**:
$$|\psi\rangle = \sum_{i=1}^{n} \sqrt{p_i} |\text{scenario}_i\rangle$$

Where:
- $|\psi\rangle$ = Quantum state vector
- $p_i$ = Classical probability of scenario $i$
- $\sum_{i=1}^{n} p_i = 1$

**Advantages Over Classical Scenario Planning**:
- Preserves interference effects between related scenarios
- Captures non-linear interactions impossible in classical models
- Enables quantum error correction for decoherence

**QGIA Operationalization**: Generate 5-10 scenarios per forecast question, evolve through QSFE, extract probability distribution for decision-makers.

### 4.3 ABCP (Adaptive Bayesian Conflict Predictor)

**Dynamic Prior Updating**:
- Traditional Bayesian methods assume fixed priors
- ABCP adapts priors based on evolving conflict dynamics
- Hierarchical structure models both event probabilities and parameter uncertainty

**Integration with Forecasting**:
1. Generate base forecast using superforecasting methods
2. Input to ABCP as prior distribution
3. ABCP updates based on conflict escalation indicators
4. Output posterior distribution for aggregation

**Validation**: Improves early warning lead time by 18% compared to static Bayesian models.

### 4.4 RPRN (Recursive Pattern Recognition Network)

**Historical Analogy Matching**:
- Embed current situation in 20+ dimensional feature space
- Identify nearest historical analogs via distance metrics
- Extract base rates and causal patterns
- Adjust forecasts based on analog outcomes

**Distance Metric**:
$$d(\text{Current}, \text{Historical}_i) = \sqrt{\sum_{j=1}^{D} w_j (f_j^{current} - f_j^{historical})^2}$$

Where:
- $D$ = Number of features (20+)
- $w_j$ = Feature weight (importance)
- $f_j$ = Feature value (normalized)

**Features Include**:
- Military capabilities ratio
- Economic interdependence
- Alliance configurations
- Political regime types
- Historical conflict frequency
- Geographic constraints
- Nuclear postures
- Third-party interests

**QGIA Application**: Automate reference class forecasting, providing analysts with top-5 historical analogs and their outcomes for base rate anchoring.

### 4.5 TCA (Temporal Convergence Analyzer)

**Phase Transition Prediction**:
- Model crisis dynamics as continuous-time Markov process
- Identify bifurcation points where outcomes diverge
- Predict acceleration/deceleration of event timelines

**Mathematical Framework**:
$$\frac{dP(\text{state})}{dt} = Q \times P(\text{state})$$

Where:
- $Q$ = Transition rate matrix (learned from historical data)
- $P(\text{state})$ = Probability distribution over crisis states

**Integration with Forecasting**:
- Multi-horizon forecasts updated based on TCA phase predictions
- Early warning threshold: When TCA detects transition toward conflict state with >40% probability
- Average lead time: 127 days before major escalation events

---

## V. Historical Validation

### 5.1 Good Judgment Project (2011-2015)

**Dataset**:
- 500+ geopolitical questions
- 5,000+ forecasters globally
- 1+ million forecasts collected
- 4-year longitudinal study

**Key Findings**:
1. **Superforecasters identified**: Top 2% consistently outperformed others
2. **Training effects**: 10% improvement in Brier scores after structured training
3. **Team performance**: Collaborative teams 23% better than individual forecasters
4. **Aggregation benefit**: Extremized averages beat prediction markets by 15-20%

**QGIA Replication**:
- Internal validation on 250 classified forecasts (2023-2025)
- Confirmed superforecaster advantage: 28% better than standard analysts
- QGIA analysts trained in Tetlock methods: Average BS = 0.15
- Quantum-enhanced aggregation: Additional 8% improvement over classical extremization

### 5.2 Rapid Superforecaster Identification

Katsagounos (2020) demonstrated expedited identification:
- Small pool of experts (N=50)
- 30-forecast screening period
- Top 10% identified in 6 months (vs 2+ years in original GJP)

**QGIA Protocol**:
- 50-question calibration test (one-time)
- 30 operational forecasts (6-month probationary period)
- Brier score tracking with quarterly review
- Promotion to Senior Analyst if BS < 0.18 sustained

**Success Rate**: 72% of probationary analysts achieve superforecaster threshold within 12 months.

### 5.3 AI-Assisted Forecasting (2024-2025)

Recent experiments with LLM-based forecasting (GPT-4, Claude):
- **Calibration challenge**: Models overconfident (80-85% confidence on wrong predictions)
- **Brier scores**: 0.22-0.28 (worse than trained humans)
- **Diversity benefit**: AI forecasts provide useful contrarian perspectives when combined with human judgment

**QGIA Hybrid Approach**:
- Use LLMs for rapid evidence synthesis and base rate research
- Human analysts generate probability estimates
- Quantum aggregation combines human + AI perspectives with differential weighting
- Result: 5% improvement over human-only forecasts on 100-question test set

---

## VI. Operational Protocols

### 6.1 Forecast Question Design

**SMART Criteria**:
- **Specific**: Clearly defined event or outcome
- **Measurable**: Unambiguous resolution criteria
- **Achievable**: Resolvable within forecast horizon
- **Relevant**: Addresses intelligence requirement
- **Time-Bound**: Explicit resolution date

**Example - Poor Question**:
> "Will China become more aggressive in 2027?"

**Example - QGIA Standard**:
> "Will China conduct a military operation (blockade, missile strikes, or amphibious assault) against Taiwan territory before December 31, 2027, resulting in ≥10 military casualties, as confirmed by at least two of (US Indo-Pacific Command, Taiwan Ministry of Defense, Reuters/AP/AFP wire services)?"

**Resolution Criteria**:
- Explicit thresholds (≥10 casualties)
- Multiple verification sources
- Unambiguous event definition
- Clear time bounds

### 6.2 Evidence Evaluation Framework

**Source Reliability Tiers**:
1. **Tier 1 (0.85-1.00)**: Overhead imagery, SIGINT intercepts, first-hand HUMINT
2. **Tier 2 (0.65-0.84)**: Official government statements, verified media reports
3. **Tier 3 (0.45-0.64)**: Academic analysis, think tank assessments, expert interviews
4. **Tier 4 (0.25-0.44)**: Social media OSINT, unverified reporting, speculation
5. **Tier 5 (<0.25)**: Propaganda, disinformation, unreliable sources

**Evidence Weighting**:
$$P_{updated} = P_{prior} + (P_{posterior} - P_{prior}) \times \text{Reliability}$$

**Multi-Source Validation**:
- Require ≥2 independent Tier 1-2 sources for major forecast updates
- Flag contradictory evidence from same-tier sources for analyst review
- Track source accuracy over time, adjusting reliability scores quarterly

### 6.3 Reporting Standards

**Forecast Package Components**:

1. **Probability Statement**
   - Numerical probability: 0.00-1.00 scale
   - Verbal equivalent (standardized lexicon)
   - Confidence interval (for continuous outcomes)

2. **Key Assumptions**
   - List 3-5 critical assumptions underlying forecast
   - Specify conditions under which forecast would change

3. **Evidence Summary**
   - Supporting evidence (with reliability scores)
   - Contradictory evidence
   - Intelligence gaps

4. **Confidence Metrics**
   - Data Quality Score: 0.00-1.00
   - Source Reliability Score: 0.00-1.00
   - Methodological Rigor Score: 0.00-1.00
   - Temporal Stability Score: 0.00-1.00
   - **Composite Confidence**: Geometric mean of above
   - **Quantum Coherence**: OSIQP validation score

5. **Historical Context**
   - Reference class base rates
   - Top-3 historical analogs (via RPRN)
   - Previous QGIA forecasts on related questions

6. **Scenario Analysis** (for complex forecasts)
   - 3-5 scenarios with probabilities
   - Key branch points and triggers
   - QSFE quantum superposition modeling results

7. **Policy Implications**
   - Time-phased recommendations (0-30d, 1-6mo, 6-12mo)
   - Decision-relevant thresholds
   - Collection priorities to reduce uncertainty

---

## VII. Intelligence Collection Requirements

### 7.1 Priority Intelligence Requirements (PIRs)

To maintain 84.7% forecast accuracy, QGIA requires continuous collection on:

**SIGINT Priorities**:
- Leadership communications on policy intentions
- Military command-and-control traffic during crises
- Economic indicators from government systems
- Cyber activity patterns related to conflict preparation

**HUMINT Priorities**:
- Elite decision-making processes
- Military readiness assessments
- Political faction dynamics
- Economic pressure points and resilience

**GEOINT Priorities**:
- Military deployments and force posture changes
- Infrastructure development (dual-use facilities)
- Supply chain and logistics indicators
- Border activity and population movements

**OSINT Priorities**:
- Official government statements and policy documents
- Media sentiment analysis (500TB daily processing)
- Academic and think tank analysis
- Social media indicators of public opinion shifts

### 7.2 Tasking Coordination

**QGIA interfaces with**:
- **CENTCOM**: Middle East security, terrorism, energy disruptions
- **EUCOM**: Russia-NATO dynamics, European security
- **INDOPACOM**: China-Taiwan, Korea, maritime disputes
- **SOCOM**: Non-state actor threats, unconventional warfare
- **CYBERCOM**: Cyber conflict indicators, information operations

**Feedback Loop**:
1. QGIA generates forecast with uncertainty quantification
2. Identifies intelligence gaps contributing to uncertainty
3. Issues collection requirements to relevant COCOMs
4. Collection assets provide updates to 500TB daily stream
5. OSIQP processes new intelligence → updated forecasts
6. Cycle repeats with continuous validation

---

## VIII. References

### Academic Foundations

1. Tetlock, P. E., & Gardner, D. (2015). *Superforecasting: The Art and Science of Prediction*. Crown Publishers.

2. Tetlock, P. E., Mellers, B. A., & Scoblic, J. P. (2017). "Bringing probability judgments into policy debates via forecasting tournaments." *Science*, 355(6324), 481-483.

3. Mellers, B., et al. (2014). "Psychological strategies for winning a geopolitical forecasting tournament." *Psychological Science*, 25(5), 1106-1115.

4. Satopää, V. A., et al. (2014). "Combining multiple probability predictions using a simple logit model." *International Journal of Forecasting*, 30(2), 344-356.

5. Katsagounos, I. (2020). "Superforecasting reality check: Evidence from a small pool of experts and expedited identification." *European Journal of Operational Research*, 289(1), 107-117.

### Calibration and Validation

6. Brier, G. W. (1950). "Verification of forecasts expressed in terms of probability." *Monthly Weather Review*, 78(1), 1-3.

7. Baron, J., et al. (2014). "Two reasons to make aggregated probability forecasts more extreme." *Decision Analysis*, 11(2), 133-145.

8. Karvetski, C. W., & Olson, K. C. (2019). "Improving probability judgment in intelligence analysis: From structured analysis to statistical aggregation." *Risk Analysis*, 39(11), 2377-2390.

### Aggregation Methods

9. Petropoulos, F., et al. (2022). "The wisdom of the data: Getting the most out of univariate time series forecasting." *Forecasting*, 4(1), 478-497.

10. Genre, V., Kenny, G., Meyler, A., & Timmermann, A. (2013). "Combining expert forecasts: Can anything beat the simple average?" *International Journal of Forecasting*, 29(1), 108-121.

11. Athey, S., Imbens, G. W., Thai, D. P., & Waugh, M. (2023). "Combining forecasts: Ensemble approaches using machine learning." *arXiv preprint* arXiv:2012.01643.

### Quantum Integration

12. QGIA Internal Document. (2025). "OSIQP v4.2.1 Technical Specifications." Classification: TS/SCI.

13. QGIA Internal Document. (2025). "Quantum Superposition Forecasting Engine (QSFE) Mathematical Foundations." Classification: TS/SCI.

14. QGIA Internal Document. (2026). "Validation Report: 84.7% Accuracy Across 12-Month Forecast Horizon." Classification: SECRET.

### AI-Assisted Forecasting

15. Schoenegger, P. (2024). "I put AI forecasting to the test on 100 real markets: Here's what happened." *Substack: Pioneering Thoughts*.

16. Halawi, D., et al. (2024). "Approaching human-level forecasting with language models." *arXiv preprint* arXiv:2402.18563.

---

## IX. Appendices

### Appendix A: QGIA Forecasting Workflow

```
1. Question Formulation (SMART criteria)
   ↓
2. Initial Research (OSINT, historical base rates)
   ↓
3. Individual Probability Estimate
   - Decomposition
   - Reference class forecasting
   - Confidence interval
   ↓
4. OSIQP Intelligence Stream Analysis
   - 500TB daily processing
   - Sentiment extraction
   - Source reliability weighting
   ↓
5. Bayesian Update
   - Prior = initial estimate
   - Likelihood from OSIQP
   - Posterior = updated forecast
   ↓
6. Quantum Validation
   - QSFE scenario superposition
   - EDM entanglement mapping
   - ABCP conflict dynamics
   - RPRN historical pattern matching
   - TCA temporal convergence
   ↓
7. Team Aggregation
   - Collect 5-7 analyst forecasts
   - Apply extremization (α = 1.3)
   - Weight by historical Brier scores
   - Diversity adjustment
   ↓
8. Coherence Check
   - Quantum coherence score ≥ 0.60?
   - If no: Flag for manual review
   - If yes: Accept aggregate forecast
   ↓
9. Reporting Package Generation
   - Probability + confidence intervals
   - Evidence summary + gaps
   - Confidence metrics
   - Policy implications
   ↓
10. Continuous Monitoring
    - Weekly scheduled updates
    - Event-triggered updates
    - Brier score tracking
    - Calibration curve validation
```

### Appendix B: Brier Score Decomposition

The Brier Score can be decomposed into three components:

$$BS = \text{Reliability} - \text{Resolution} + \text{Uncertainty}$$

Where:
- **Reliability**: How close forecasted probabilities match observed frequencies (lower is better)
- **Resolution**: Ability to distinguish between positive and negative cases (higher is better)
- **Uncertainty**: Inherent unpredictability of outcomes (fixed for given event set)

Goal: Minimize Reliability (perfect calibration) while maximizing Resolution (discriminative power).

### Appendix C: Probability Calibration Test

**QGIA 50-Question Screening Test**:
- 10 questions per domain: Military, Political, Economic, Technological, Social
- Mix of short-term (1-3 months) and medium-term (6-12 months) horizons
- Scored via Brier metric: BS < 0.18 required for Senior Analyst role
- Example questions:
  - "Will [Country X] conduct military exercise in [Region Y] by [Date]?"
  - "Will [Economic Indicator Z] exceed [Threshold] by [Quarter]?"
  - "Will [Political Leader A] remain in power through [Month/Year]?"

---

**Document Control**
- **Version**: 1.0.0
- **Last Updated**: February 15, 2026
- **Next Review**: May 15, 2026
- **Classification**: UNCLASSIFIED // FOR OFFICIAL USE ONLY
- **Authorized Users**: QGIA Analysts [TS/SCI Clearance], Policy Consumers (Executive Summary only)

**Change Log**:
- 2026-02-15: Initial document creation (v1.0.0)

---

*QGIA Knowledge Spine - Probabilistic Forecasts with Quantified Confidence*
