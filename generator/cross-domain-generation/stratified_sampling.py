import json
import random
from itertools import combinations

# reproducibility
random.seed(42)

# load topics
with open("data/topics.json", "r") as f:
    data = json.load(f)

# category mapping
categories = {
    "linear_algebra": [],
    "calculus": [],
    "statistics": [],
    "probability": []
}

# original topics.json had categories — rebuild mapping
la_topics = [
    "eigenvalues_and_eigenvectors",
    "matrix_decomposition_svd",
    "linear_transformations",
    "vector_spaces_and_subspaces",
    "rank_and_null_space",
    "least_squares_regression",
    "orthogonality_and_projections",
    "markov_chains",
    "determinants_and_invertibility",
    "covariance_matrix"
]

ca_topics = [
    "gradient_and_partial_derivatives",
    "optimization_maxima_and_minima",
    "differential_equations_odes",
    "integration_and_area_under_curve",
    "taylor_series_approximation",
    "multivariable_optimization",
    "gradient_descent",
    "rate_of_change_and_related_rates",
    "fourier_transform",
    "limits_and_continuity"
]

st_topics = [
    "hypothesis_testing",
    "confidence_intervals",
    "regression_analysis",
    "central_limit_theorem",
    "type_i_and_type_ii_errors",
    "sampling_methods_and_bias",
    "anova_variance_analysis",
    "correlation_vs_causation",
    "bayesian_updating",
    "time_series_analysis"
]

pr_topics = [
    "conditional_probability",
    "bayes_theorem",
    "random_variables_and_distributions",
    "law_of_large_numbers",
    "expected_value",
    "variance_and_standard_deviation",
    "independence_and_correlation",
    "poisson_process",
    "monte_carlo_simulation",
    "information_theory_and_entropy"
]

# ── Generate All Pairs Per Stratum ─────────────────────────

# Stratum 1: Same category
stratum_1 = (
    list(combinations(la_topics, 2)) +
    list(combinations(ca_topics, 2)) +
    list(combinations(st_topics, 2)) +
    list(combinations(pr_topics, 2))
)

# Stratum 2a: Adjacent category
stratum_2a = (
    [(a, b) for a in la_topics for b in ca_topics] +
    [(a, b) for a in ca_topics for b in st_topics] +
    [(a, b) for a in st_topics for b in pr_topics]
)

# Stratum 2b: Distant category
stratum_2b = (
    [(a, b) for a in la_topics for b in st_topics] +
    [(a, b) for a in la_topics for b in pr_topics] +
    [(a, b) for a in ca_topics for b in pr_topics]
)

print(f"Stratum 1  (same)     : {len(stratum_1)} pairs")
print(f"Stratum 2a (adjacent) : {len(stratum_2a)} pairs")
print(f"Stratum 2b (distant)  : {len(stratum_2b)} pairs")
print(f"Total population      : {len(stratum_1) + len(stratum_2a) + len(stratum_2b)} pairs")

# ── Sample 20% From Each Stratum ───────────────────────────

sample_1  = random.sample(stratum_1,  int(len(stratum_1)  * 0.20))
sample_2a = random.sample(stratum_2a, int(len(stratum_2a) * 0.20))
sample_2b = random.sample(stratum_2b, int(len(stratum_2b) * 0.20))

all_samples = sample_1 + sample_2a + sample_2b

print(f"\nSample 1  (same)     : {len(sample_1)} pairs")
print(f"Sample 2a (adjacent) : {len(sample_2a)} pairs")
print(f"Sample 2b (distant)  : {len(sample_2b)} pairs")
print(f"Total sample         : {len(all_samples)} pairs")

# ── Write To File ──────────────────────────────────────────

with open("pair_combination_sample.txt", "w") as f:
    f.write(f"Total Sample: {len(all_samples)} pairs\n")
    f.write(f"Seed: 42\n")
    f.write(f"{'='*60}\n\n")

    f.write(f"STRATUM 1 — Same Category ({len(sample_1)} pairs)\n")
    f.write(f"{'-'*60}\n")
    for i, (t1, t2) in enumerate(sample_1, 1):
        f.write(f"{t1}, {t2}\n")

    f.write(f"\nSTRATUM 2A — Adjacent Category ({len(sample_2a)} pairs)\n")
    f.write(f"{'-'*60}\n")
    for i, (t1, t2) in enumerate(sample_2a, 1):
        f.write(f"{t1}, {t2}\n")

    f.write(f"\nSTRATUM 2B — Distant Category ({len(sample_2b)} pairs)\n")
    f.write(f"{'-'*60}\n")
    for i, (t1, t2) in enumerate(sample_2b, 1):
        f.write(f"{t1}, {t2}\n")

print(f"\nWritten to pair_combination_sample.txt")