# Multidimensional IRT (MIRT) Logic Used in the Adaptive Exam System

This document explains the mathematical and algorithmic logic behind the **Multidimensional Item Response Theory (MIRT)** used in the `MIRTCATSimulator` class. All formulas are provided in clean Markdown format.

---

# 1. What is Multidimensional IRT (MIRT)?

Traditional IRT (e.g., 1PL, 2PL, 3PL models) assumes a **single latent trait** (ability). MIRT generalizes this by assuming each examinee has **multiple abilities** simultaneously, such as:

* A **General Factor** (overall ML ability)
* **Topic Factors** (ANN, CNN, Linear Models, Statistics, etc.)
* **Cognitive Levels** (Knowledge, Application, Analysis)

Thus, instead of a scalar ability ( \theta ), we estimate a vector:

$$
\boldsymbol{\theta} = [\theta_{General}, \theta_{ANN}, \theta_{CNN}, ..., \theta_{Knowledge}, \theta_{Application}, \theta_{Analysis}]
$$

Each item loads on a subset of these dimensions according to the **Q-matrix**.

---

# 2. Q-Matrix Construction

The Q-matrix represents which latent abilities each item measures.

For each item:

* It *always* loads on the General factor: `General = 1`
* It loads on exactly one Topic factor (e.g., ANN)
* It loads on exactly one Cognitive factor (e.g., Application)

Example row:

| General | ANN | CNN | Stats | Knowledge | Application | Analysis |
| ------- | --- | --- | ----- | --------- | ----------- | -------- |
| 1       | 0   | 1   | 0     | 0         | 1           | 0        |

The discrimination vector for an item becomes:

$$
\mathbf{a} = [a_{General}, a_{ANN}, a_{CNN}, ..., a_{Analysis}]
$$

In the simulator, each non-zero dimension has discrimination = the item’s `a` parameter.

---

# 3. Multidimensional 3PL Model

The probability that a user with ability vector ( \boldsymbol{\theta} ) answers item *i* correctly is:

$$
P_i(\boldsymbol{\theta}) = c_i + (1 - c_i) \frac{1}{1 + \exp\left(-1.7(\mathbf{a}_i^T \boldsymbol{\theta} - b_i)\right)}
$$

Where:

* ( c_i ) = guessing parameter
* ( b_i ) = difficulty
* ( \mathbf{a}_i ) = discrimination vector for item i
* 1.7 = scaling constant (makes logistic curve approximate normal ogive)

The linear predictor:

$$
Z_i = \mathbf{a}_i^T \boldsymbol{\theta} - b_i
$$

Thus:

$$
P_i = c_i + (1-c_i) \cdot \text{logistic}(1.7 Z_i)
$$

---

# 4. Multidimensional 2PL Model

If `model_type='2PL'`, the guessing parameter is removed:

$$
P_i(\boldsymbol{\theta}) = \frac{1}{1 + \exp\left(-1.7(\mathbf{a}_i^T \boldsymbol{\theta} - b_i)\right)}
$$

---

# 5. Fisher Information in MIRT

The Fisher Information for MIRT items is a matrix:

$$
\mathbf{I}_i(\boldsymbol{\theta}) = (1.7)^2 \cdot \frac{Q}{P} \cdot \frac{(P - c)^2}{(1 - c)^2} (\mathbf{a}_i \mathbf{a}_i^T)
$$

Where:

* ( P ) = item response probability
* ( Q = 1 - P )

The simulator uses **the trace of the matrix** as a scalar measure:

$$
I_i = \mathrm{trace}(\mathbf{I}_i)
$$

This is used to select the most informative item.

---

# 6. Ability Estimation: EAP (Expected A Posteriori)

We approximate the posterior ability distribution:

$$
p(\boldsymbol{\theta} | \text{responses}) \propto L(\boldsymbol{\theta}) p(\boldsymbol{\theta})
$$

where the likelihood is:

$$
L(\boldsymbol{\theta}) = \prod_{i} P_i(\boldsymbol{\theta})^{u_i} (1 - P_i(\boldsymbol{\theta}))^{1-u_i}
$$

and the prior is multivariate normal:

$$
\boldsymbol{\theta} \sim N(\mathbf{0}, 2\mathbf{I})
$$

Monte Carlo sampling with ( n = 100 ) samples is used:

$$
\hat{\boldsymbol{\theta}}*{EAP} = \sum*{k=1}^{n} w_k \boldsymbol{\theta}_k
$$

Weights are computed using:

$$
w_k = \frac{L(\boldsymbol{\theta}_k) p(\boldsymbol{\theta}_k)}{\sum_j L(\boldsymbol{\theta}_j) p(\boldsymbol{\theta}_j)}
$$

Standard errors are the square root of posterior variance:

$$
SE_j = \sqrt{\mathrm{Var}(\theta_j)}
$$

---

# 7. Item Selection: Shadow Test Approach

The simulator maintains content constraints:

* Minimum 2 items per topic
* Balanced cognitive levels

Shadow-test logic:

1. **First item** → random (fast start)
2. Filter remaining items that satisfy content constraints
3. Compute Fisher Information for candidates
4. Select item with highest information

---

# 8. Content Balancing Logic

When selecting items:

* If a topic has fewer than required items: only items from that topic are allowed
* Otherwise: all items are allowed

Topic counters:

```
self.topic_counts[topic] += 1
self.cognitive_counts[level] += 1
```

---

# 9. Diagnostic Reporting

Final theta vector:

$$
\boldsymbol{\theta}_{final} = [\theta_1, \theta_2, ..., \theta_d]
$$

Interpretation is given per dimension:

* Low (below -1.0)
* Moderate (-1.0 to +1.0)
* High (above +1.0)

General factor is used as the **overall score**.

---

# 10. Summary of Key Equations

### 3PL MIRT:

$$
P_i = c_i + (1 - c_i) \cdot \frac{1}{1 + e^{-1.7(\mathbf{a}^T\boldsymbol{\theta} - b_i)}}
$$

### Fisher Information (trace):

$$
I_i = \text{trace}\left((1.7)^2 \frac{Q}{P} \frac{(P-c)^2}{(1-c)^2} (\mathbf{a}\mathbf{a}^T) \right)
$$

### EAP:

$$
\hat{\boldsymbol{\theta}} = \sum_k w_k \boldsymbol{\theta}_k
$$

### Likelihood:

$$
L(\boldsymbol{\theta}) = \prod_{i} P_i^{u_i} (1-P_i)^{1-u_i}
$$


