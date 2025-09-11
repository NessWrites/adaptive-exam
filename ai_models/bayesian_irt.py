import pymc as pm
import arviz as az
import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.app.services.irt_utils import BayesianIRTData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_hierarchical_3pl_model(bayesian_data: BayesianIRTData) -> Dict[str, Any]:
    try:
        if not bayesian_data:
            logger.error("No Bayesian data provided for analysis")
            raise ValueError("Bayesian data is None")

        N = bayesian_data['N']
        J = bayesian_data['J']
        i_idx = bayesian_data['i_idx']
        j_idx = bayesian_data['j_idx']
        y_obs = bayesian_data['y_obs']
        K_arr = bayesian_data['K_arr']
        df_long = bayesian_data['df_long']

        with pm.Model() as irt_3pl:
            raw_theta = pm.Normal("raw_theta", mu=0.0, sigma=1.0, shape=N)
            theta = pm.Deterministic("theta", (raw_theta - raw_theta.mean()) / raw_theta.std())
            mu_a = pm.Normal("mu_a", mu=0.0, sigma=1.0)
            sigma_a = pm.HalfNormal("sigma_a", sigma=0.5)
            a = pm.Lognormal("a", mu=mu_a, sigma=sigma_a, shape=J)
            mu_b = pm.Normal("mu_b", mu=0.0, sigma=1.0)
            sigma_b = pm.HalfNormal("sigma_b", sigma=1.0)
            b = pm.Normal("b", mu=mu_b, sigma=sigma_b, shape=J)
            alpha_c = np.ones(J) * 1.0
            beta_c = np.array([max(1, K-1) for K in K_arr], dtype=float)
            c = pm.Beta("c", alpha=alpha_c, beta=beta_c, shape=J)
            lin = a[j_idx] * (theta[i_idx] - b[j_idx])
            p_row = c[j_idx] + (1 - c[j_idx]) * pm.math.sigmoid(lin)
            obs = pm.Bernoulli("obs", p=p_row, observed=y_obs)
            trace = pm.sample(draws=1500, tune=1500, chains=4, target_accept=0.9, return_inferencedata=True)

        item_summary = az.summary(trace, var_names=["a", "b", "c"], hdi_prob=0.95)
        theta_summary = az.summary(trace, var_names=["theta"], hdi_prob=0.95)
        rhat = az.rhat(trace)
        max_rhat = float(np.nanmax(rhat.to_array().values.flatten()))

        with irt_3pl:
            ppc = pm.sample_posterior_predictive(trace, var_names=["obs"], random_seed=42)
        y_rep = ppc.posterior_predictive["obs"].stack(draws=("chain", "draw")).values
        n_draws, n_obs = y_rep.shape
        n_obs_correct = len(i_idx)
        
        if n_obs != n_obs_correct:
            logger.warning(f"Truncating PPC samples from {n_obs} to {n_obs_correct} observations")
            y_rep = y_rep[:, :n_obs_correct]
            n_obs = n_obs_correct

        ppc_long_list = []
        for draw in range(n_draws):
            for obs_idx in range(min(n_obs, len(i_idx))):
                ppc_long_list.append({
                    'draw': draw, 'i': i_idx[obs_idx], 'j': j_idx[obs_idx], 'y_rep': y_rep[draw, obs_idx]
                })
        ppc_long_df = pd.DataFrame(ppc_long_list)
        rep_item_means = ppc_long_df.groupby(['draw', 'j'])['y_rep'].mean().reset_index()
        rep_item_summary = rep_item_means.groupby('j')['y_rep'].agg(['mean', 'std']).reset_index()
        obs_item_means = df_long.groupby("j")["is_correct"].mean().sort_index().values

        ppc_df = pd.DataFrame({
            "item": [f"Q{j+1}" for j in range(J)],
            "obs_mean": obs_item_means,
            "rep_mean": rep_item_summary['mean'].values,
            "rep_sd": rep_item_summary['std'].values
        })

        return {
            "analysis_completed": True,
            "n_students": N,
            "n_questions": J,
            "theta_estimates": theta_summary['mean'].values.tolist(),
            "theta_stds": theta_summary['sd'].values.tolist(),
            "question_parameters": {
                "a_means": item_summary.loc[[f"a[{j}]" for j in range(J)], "mean"].values.tolist(),
                "b_means": item_summary.loc[[f"b[{j}]" for j in range(J)], "mean"].values.tolist(),
                "c_means": item_summary.loc[[f"c[{j}]" for j in range(J)], "mean"].values.tolist(),
                "a_stds": item_summary.loc[[f"a[{j}]" for j in range(J)], "sd"].values.tolist(),
                "b_stds": item_summary.loc[[f"b[{j}]" for j in range(J)], "sd"].values.tolist(),
                "c_stds": item_summary.loc[[f"c[{j}]" for j in range(J)], "sd"].values.tolist()
            },
            "ppc_df": ppc_df.to_dict(),
            "max_rhat": max_rhat
        }
    except Exception as e:
        logger.error(f"Hierarchical 3PL model failed: {e}")
        raise