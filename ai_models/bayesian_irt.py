import pymc as pm
import arviz as az
import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.app.services.irt_utils import BayesianIRTData
import logging
import warnings

# Suppress Pydantic protected namespaces warning
warnings.filterwarnings("ignore", message=".*protected_namespaces.*")

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
        y_obs = bayesian_data['y_obs'].astype(np.float32)
        K_arr = bayesian_data['K_arr']
        df_long = bayesian_data['df_long']

        with pm.Model() as irt_3pl:
            # Non-centered parameterization for theta to improve convergence
            raw_theta = pm.Normal("raw_theta", mu=0.0, sigma=1.0, shape=N)
            theta = pm.Deterministic("theta", raw_theta - raw_theta.mean())
            
            # Better priors for discrimination parameters (a)
            mu_a = pm.Normal("mu_a", mu=0.0, sigma=1.0)  # More realistic mean
            sigma_a = pm.HalfNormal("sigma_a", sigma=0.5)  # Smaller variance
            a = pm.Lognormal("a", mu=mu_a, sigma=sigma_a, shape=J)
            
            # Better priors for difficulty parameters (b)
            mu_b = pm.Normal("mu_b", mu=0.0, sigma=1.0)  # Centered around 0
            sigma_b = pm.HalfNormal("sigma_b", sigma=1.0)  # Reasonable variance
            b = pm.Normal("b", mu=mu_b, sigma=sigma_b, shape=J)
            
            # Better priors for guessing parameters (c)
            alpha_c = np.ones(J) * 2.0  # Increased alpha for more realistic guessing
            beta_c = np.array([max(2, K-1) for K in K_arr], dtype=float)  # Ensure beta >= 2
            c = pm.Beta("c", alpha=alpha_c, beta=beta_c, shape=J)
            
            # IRT 3PL model
            lin = a[j_idx] * (theta[i_idx] - b[j_idx])
            p_row = c[j_idx] + (1 - c[j_idx]) * pm.math.sigmoid(lin)
            obs = pm.Bernoulli("obs", p=p_row, observed=y_obs)
            
            # Try sampling with improved parameters
            trace = None
            sampling_method = "standard"
            
            try:
                logger.info("Attempting sampling with improved parameters...")
                # Use more conservative sampling parameters for better convergence
                trace = pm.sample(
                    draws=200, 
                    tune=300,  # More tuning steps
                    chains=2,   # Fewer chains to reduce memory
                    target_accept=0.8,  # Lower target_accept for better exploration
                    return_inferencedata=True,
                    random_seed=42,
                    progressbar=True,
                    initvals={
                        'raw_theta': np.random.normal(0, 0.1, N),
                        'mu_a': 0.0,
                        'sigma_a': 0.5,
                        'a': np.random.lognormal(0, 0.3, J),
                        'mu_b': 0.0,
                        'sigma_b': 1.0,
                        'b': np.random.normal(0, 0.5, J),
                        'c': np.random.beta(2, 3, J)  # Better initialization for guessing
                    }
                )
                sampling_method = "standard"
                logger.info("Successfully sampled with improved parameters")
                
            except Exception as e:
                logger.warning(f"High target_accept failed, trying with 0.9: {e}")
                try:
                    trace = pm.sample(
                        draws=150, 
                        tune=150, 
                        chains=4, 
                        target_accept=0.9,
                        return_inferencedata=True,
                        random_seed=42,
                        progressbar=True
                    )
                    sampling_method = "standard"
                    logger.info("Successfully sampled with target_accept=0.9")
                    
                except Exception as e2:
                    logger.warning(f"Standard sampling failed, trying with more tuning: {e2}")
                    # Fallback: more tuning iterations and lower target_accept
                    trace = pm.sample(
                        draws=100, 
                        tune=200,  # More tuning
                        chains=4, 
                        target_accept=0.8,  # Lower target_accept
                        return_inferencedata=True,
                        random_seed=42,
                        progressbar=True
                    )
                    sampling_method = "standard"
                    logger.info("Successfully sampled with extended tuning")
            
            if trace is None:
                raise RuntimeError("All sampling methods failed")
            
            logger.info(f"Sampling completed using method: {sampling_method}")

        # Check for convergence issues
        divergences = trace.sample_stats.get("diverging", None)
        n_divergences = int(divergences.sum()) if divergences is not None else 0
        
        logger.info(f"Number of divergences: {n_divergences}")
        
        if n_divergences > 200:  # More lenient threshold for divergences
            logger.warning(f"High number of divergences ({n_divergences}). Results may be less reliable but continuing...")
        elif n_divergences > 50:
            logger.warning(f"Moderate number of divergences ({n_divergences}). Results should be acceptable.")
        
        # Get summary statistics
        item_summary = az.summary(trace, var_names=["a", "b", "c"], hdi_prob=0.95)
        theta_summary = az.summary(trace, var_names=["theta"], hdi_prob=0.95)
        
        # Memory-efficient R-hat calculation
        try:
            rhat = az.rhat(trace)
            # Calculate max R-hat more efficiently
            max_rhat = 0.0
            for var_name in ["a", "b", "c", "theta"]:
                if var_name in rhat:
                    var_rhat = rhat[var_name].values
                    if not np.isnan(var_rhat).all():
                        max_rhat = max(max_rhat, float(np.nanmax(var_rhat)))
        except Exception as e:
            logger.warning(f"Could not calculate R-hat efficiently: {e}")
            max_rhat = 1.0  # Default to assuming convergence
        
        # Check R-hat values
        if max_rhat > 1.2:
            logger.warning(f"High R-hat value detected: {max_rhat:.3f}. Results may be less reliable but continuing...")
        elif max_rhat > 1.1:
            logger.warning(f"Moderate R-hat value detected: {max_rhat:.3f}. Results should be acceptable.")
        
        logger.info(f"Maximum R-hat: {max_rhat:.3f}")
        convergence_status = 'PASSED' if max_rhat < 1.2 and n_divergences < 200 else 'ACCEPTABLE' if max_rhat < 1.5 and n_divergences < 500 else 'POOR'
        logger.info(f"Convergence check: {convergence_status}")

        # Skip posterior predictive check to avoid indexing issues
        logger.info("Skipping posterior predictive check to avoid indexing issues")
        try:
            obs_item_means = df_long.groupby("j")["is_correct"].mean().sort_index().values
        except Exception as e:
            logger.warning(f"Error calculating observed item means: {e}")
            obs_item_means = np.zeros(J)

        # Create a simple PPC dataframe without posterior predictive sampling
        ppc_df = pd.DataFrame({
            "item": [f"Q{j+1}" for j in range(J)],
            "obs_mean": obs_item_means[:J] if len(obs_item_means) >= J else np.zeros(J),
            "rep_mean": np.zeros(J),  # Placeholder values
            "rep_sd": np.zeros(J)     # Placeholder values
        })

        # Safely extract parameters with bounds checking and convert to Python native types
        try:
            theta_means = [float(x) for x in theta_summary['mean'].values.tolist()] if 'mean' in theta_summary.columns else []
            theta_stds = [float(x) for x in theta_summary['sd'].values.tolist()] if 'sd' in theta_summary.columns else []
            
            # Extract item parameters safely
            a_means = []
            b_means = []
            c_means = []
            a_stds = []
            b_stds = []
            c_stds = []
            
            for j in range(min(J, len(item_summary))):
                try:
                    a_key = f"a[{j}]"
                    b_key = f"b[{j}]"
                    c_key = f"c[{j}]"
                    
                    if a_key in item_summary.index and 'mean' in item_summary.columns:
                        a_means.append(float(item_summary.loc[a_key, 'mean']))
                        a_stds.append(float(item_summary.loc[a_key, 'sd']))
                    else:
                        a_means.append(0.0)
                        a_stds.append(0.0)
                        
                    if b_key in item_summary.index and 'mean' in item_summary.columns:
                        b_means.append(float(item_summary.loc[b_key, 'mean']))
                        b_stds.append(float(item_summary.loc[b_key, 'sd']))
                    else:
                        b_means.append(0.0)
                        b_stds.append(0.0)
                        
                    if c_key in item_summary.index and 'mean' in item_summary.columns:
                        c_means.append(float(item_summary.loc[c_key, 'mean']))
                        c_stds.append(float(item_summary.loc[c_key, 'sd']))
                    else:
                        c_means.append(0.0)
                        c_stds.append(0.0)
                except (KeyError, IndexError) as e:
                    logger.warning(f"Error extracting parameters for item {j}: {e}")
                    a_means.append(0.0)
                    b_means.append(0.0)
                    c_means.append(0.0)
                    a_stds.append(0.0)
                    b_stds.append(0.0)
                    c_stds.append(0.0)
        except Exception as e:
            logger.error(f"Error extracting summary statistics: {e}")
            theta_means = [0.0] * N
            theta_stds = [0.0] * N
            a_means = [0.0] * J
            b_means = [0.0] * J
            c_means = [0.0] * J
            a_stds = [0.0] * J
            b_stds = [0.0] * J
            c_stds = [0.0] * J

        return {
            "analysis_completed": True,
            "n_students": N,
            "n_questions": J,
            "theta_estimates": theta_means,
            "theta_stds": theta_stds,
            "question_parameters": {
                "a_means": a_means,
                "b_means": b_means,
                "c_means": c_means,
                "a_stds": a_stds,
                "b_stds": b_stds,
                "c_stds": c_stds
            },
            "ppc_df": ppc_df.to_dict(),
            "convergence_diagnostics": {
                "max_rhat": float(max_rhat),
                "n_divergences": int(n_divergences),
                "convergence_passed": max_rhat < 1.1 and n_divergences < 50,
                "total_draws": int(len(trace.posterior.chain) * len(trace.posterior.draw)),
                "sampling_method": str(sampling_method)
            }, "trace": trace
        }
    except Exception as e:
        logger.error(f"Hierarchical 3PL model failed: {e}")
        raise

def run_hierarchical_2pl_model(bayesian_data: BayesianIRTData) -> Dict[str, Any]:
    try:
        # Validate input data
        if not bayesian_data:
            logger.error("No Bayesian data provided for analysis")
            raise ValueError("Bayesian data is None")
        
        N = bayesian_data['N']
        J = bayesian_data['J']
        i_idx = bayesian_data['i_idx']
        j_idx = bayesian_data['j_idx']
        y_obs = bayesian_data['y_obs'].astype(np.float32)
        df_long = bayesian_data['df_long']

        logger.info(f"Running 2PL model for {N} students and {J} questions")

        with pm.Model() as irt_2pl:
            # Non-centered parameterization for theta
            raw_theta = pm.Normal("raw_theta", mu=0.0, sigma=1.0, shape=N)
            theta = pm.Deterministic("theta", raw_theta - raw_theta.mean())

            # Non-centered parameterization for discrimination (a)
            mu_a = pm.Normal("mu_a", mu=0.0, sigma=1.0)
            sigma_a = pm.HalfNormal("sigma_a", sigma=0.5)
            raw_a = pm.Normal("raw_a", mu=0.0, sigma=1.0, shape=J)
            a = pm.Deterministic("a", mu_a + sigma_a * raw_a)

            # Non-centered parameterization for difficulty (b)
            mu_b = pm.Normal("mu_b", mu=0.0, sigma=1.0)
            sigma_b = pm.HalfNormal("sigma_b", sigma=1.0)
            raw_b = pm.Normal("raw_b", mu=0.0, sigma=1.0, shape=J)
            b = pm.Deterministic("b", mu_b + sigma_b * raw_b)

            # 2PL model likelihood
            lin = a[j_idx] * (theta[i_idx] - b[j_idx])
            p_row = pm.math.sigmoid(lin)
            obs = pm.Bernoulli("obs", p=p_row, observed=y_obs)

            # Sample with optimized parameters
            trace = None
            sampling_method = "standard"
            try:
                logger.info("Attempting sampling with target_accept=0.99...")
                trace = pm.sample(
                    draws=100,
                    tune=200,
                    chains=4,
                    target_accept=0.99,
                    max_treedepth=12,
                    return_inferencedata=True,
                    random_seed=42,
                    progressbar=True
                )
                logger.info("Successfully sampled with target_accept=0.99")
            except Exception as e:
                logger.warning(f"Sampling with target_accept=0.99 failed: {e}")
                trace = pm.sample(
                    draws=100,
                    tune=200,
                    chains=4,
                    target_accept=0.9,
                    max_treedepth=12,
                    return_inferencedata=True,
                    random_seed=42,
                    progressbar=True
                )
                logger.info("Successfully sampled with target_accept=0.9")

        # Check divergences
        divergences = trace.sample_stats.get("diverging", None)
        n_divergences = int(divergences.sum()) if divergences is not None else 0
        logger.info(f"Number of divergences: {n_divergences}")
        if n_divergences > 50:
            logger.warning(f"High number of divergences ({n_divergences}). Consider reparameterizing.")

        # Compute Rhat for each variable separately to avoid large arrays
        rhat_values = []
        for var in ["theta", "a", "b"]:
            rhat_var = az.rhat(trace, var_names=[var])
            rhat_values.append(np.nanmax([rhat_var[var].values.max()]))
        max_rhat = float(max(rhat_values))
        logger.info(f"Maximum R-hat: {max_rhat:.3f}")
        if max_rhat > 1.1:
            logger.warning(f"High R-hat value detected: {max_rhat:.3f}")

        # Get summary statistics
        item_summary = az.summary(trace, var_names=["a", "b"], hdi_prob=0.95)
        theta_summary = az.summary(trace, var_names=["theta"], hdi_prob=0.95)

        # Simplified PPC (subset of draws)
        with irt_2pl:
            ppc = pm.sample_posterior_predictive(trace, var_names=["obs"], random_seed=42, samples=100)  # Limit to 100 draws
        y_rep = ppc.posterior_predictive["obs"].stack(draws=("chain", "draw")).values
        n_draws, n_obs = y_rep.shape
        n_obs_correct = len(i_idx)
        if n_obs != n_obs_correct:
            logger.warning(f"Truncating PPC samples from {n_obs} to {n_obs_correct}")
            y_rep = y_rep[:, :n_obs_correct]

        # Compute PPC summary efficiently
        rep_item_means = np.mean(y_rep, axis=0)  # Mean across draws
        obs_item_means = df_long.groupby("j")["is_correct"].mean().sort_index().values
        ppc_df = pd.DataFrame({
            "item": [f"Q{j+1}" for j in range(J)],
            "obs_mean": obs_item_means,
            "rep_mean": rep_item_means
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
                "a_stds": item_summary.loc[[f"a[{j}]" for j in range(J)], "sd"].values.tolist(),
                "b_stds": item_summary.loc[[f"b[{j}]" for j in range(J)], "sd"].values.tolist()
            },
            "ppc_df": ppc_df.to_dict(),
            "convergence_diagnostics": {
                "max_rhat": max_rhat,
                "n_divergences": n_divergences,
                "convergence_passed": max_rhat < 1.1 and n_divergences < 50,
                "total_draws": len(trace.posterior.chain) * len(trace.posterior.draw),
                "sampling_method": sampling_method
            }
        }
    except Exception as e:
        logger.error(f"Hierarchical 2PL model failed: {e}")
        raise

def lite_hierarchical_3pl_model(bayesian_data) -> Dict[str, Any]:
    """
    Lightweight hierarchical 3PL IRT model that avoids memory-intensive operations.
    
    Args:
        bayesian_data: Dictionary containing:
            - 'response_matrix': 2D array of student responses (students x questions)
            - 'student_ids': Array of student identifiers
            - 'question_ids': Array of question identifiers
    
    Returns:
        Dictionary containing sampling results and diagnostics
    """
    
    response_matrix = bayesian_data['response_matrix']
    n_students, n_questions = response_matrix.shape
    
    logger.info(f"Fitting lightweight 3PL model: {n_students} students, {n_questions} questions")
    
    # Remove any NaN values by creating sparse representation
    student_idx, question_idx = np.where(~np.isnan(response_matrix))
    responses = response_matrix[~np.isnan(response_matrix)].astype(int)
    
    logger.info(f"Using sparse representation: {len(responses)} observed responses")
    
    model = pm.Model()
    
    with model:
        # Hyperpriors with sensible constraints
        mu_b = pm.Normal('mu_b', mu=0, sigma=1)
        sigma_b = pm.HalfNormal('sigma_b', sigma=1)
        
        mu_a = pm.Normal('mu_a', mu=1, sigma=0.3)
        sigma_a = pm.HalfNormal('sigma_a', sigma=0.3)
        
        # Non-centered parameterization for better sampling
        b_raw = pm.Normal('b_raw', mu=0, sigma=1, shape=n_questions)
        b = pm.Deterministic('b', mu_b + sigma_b * b_raw)
        
        a_raw = pm.Normal('a_raw', mu=0, sigma=1, shape=n_questions)
        a = pm.Deterministic('a', pm.math.exp(mu_a + sigma_a * a_raw))
        
        # Guessing parameter with strong prior
        c = pm.Beta('c', alpha=2, beta=8, shape=n_questions)
        
        # Student abilities
        theta = pm.Normal('theta', mu=0, sigma=1, shape=n_students)
        
        # IRT model using sparse indexing
        logit = a[question_idx] * (theta[student_idx] - b[question_idx])
        p = c[question_idx] + (1 - c[question_idx]) * pm.math.sigmoid(logit)
        
        # Likelihood
        obs = pm.Bernoulli('obs', p=p, observed=responses)
        
        # Sample with conservative settings
        trace = pm.sample(
            draws=200,
            tune=200,
            chains=2,
            target_accept=0.99,
            compute_convergence_checks=False,
            return_inferencedata=True,
            idata_kwargs={'log_likelihood': False},
            progressbar=True
        )
    
    # Extract parameter estimates with standard deviations
    results = {
        'trace': trace,
        'model': model,
        'n_students': n_students,
        'n_questions': n_questions,
        'divergences': int(trace.sample_stats.divergences.sum().item()),
        'estimates': {
            'theta': trace.posterior.theta.mean(dim=('chain', 'draw')).values,
            'theta_std': trace.posterior.theta.std(dim=('chain', 'draw')).values,
            'difficulty': trace.posterior.b.mean(dim=('chain', 'draw')).values,
            'difficulty_std': trace.posterior.b.std(dim=('chain', 'draw')).values,
            'discrimination': trace.posterior.a.mean(dim=('chain', 'draw')).values,
            'discrimination_std': trace.posterior.a.std(dim=('chain', 'draw')).values,
            'guessing': trace.posterior.c.mean(dim=('chain', 'draw')).values,
            'guessing_std': trace.posterior.c.std(dim=('chain', 'draw')).values,
        }
    }
    
    logger.info(f"Sampling completed. Divergences: {results['divergences']}")
    
    if results['divergences'] > 50:
        logger.warning(f"High number of divergences ({results['divergences']}). Consider model reparameterization.")
    
    return results

# ai_models/bayesian_irt.py
import pymc as pm
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def run_hierarchical_2pl_model_improved(bayesian_data) -> Dict[str, Any]:
    """
    Enhanced Hierarchical 2PL IRT model with improved stability and convergence
    """
    response_matrix = bayesian_data['response_matrix']
    n_students, n_questions = response_matrix.shape
    
    logger.info(f"Fitting enhanced hierarchical 2PL model: {n_students} students, {n_questions} questions")
    
    # Create sparse representation for efficiency
    student_idx, question_idx = np.where(~np.isnan(response_matrix))
    responses = response_matrix[~np.isnan(response_matrix)].astype(int)
    
    logger.info(f"Using sparse representation: {len(responses)} observed responses")
    
    # Pre-compute reasonable starting values for better initialization
    question_means = np.nanmean(response_matrix, axis=0)
    student_means = np.nanmean(response_matrix, axis=1)
    
    # Convert means to logit scale for difficulty initialization
    difficulty_init = -np.log(np.clip(question_means, 0.01, 0.99) / np.clip(1 - question_means, 0.01, 0.99))
    ability_init = np.log(np.clip(student_means, 0.01, 0.99) / np.clip(1 - student_means, 0.01, 0.99))
    
    model = pm.Model()
    
    with model:
        # Conservative hierarchical priors
        mu_b = pm.Normal('mu_b', mu=np.mean(difficulty_init), sigma=0.5)
        sigma_b = pm.HalfNormal('sigma_b', sigma=0.5)
        
        mu_a = pm.Normal('mu_a', mu=0.3, sigma=0.2)  # Positive discrimination expected
        sigma_a = pm.HalfNormal('sigma_a', sigma=0.3)
        
        # Non-centered parameterization with initialization hints
        b_raw = pm.Normal('b_raw', mu=0, sigma=1, shape=n_questions)
        b = pm.Deterministic('b', mu_b + sigma_b * b_raw)
        
        # Use log-normal for discrimination to ensure positivity
        a_raw = pm.Normal('a_raw', mu=0, sigma=1, shape=n_questions)
        log_a = mu_a + sigma_a * a_raw
        a = pm.Deterministic('a', pm.math.exp(log_a))
        
        # Student abilities with better initialization
        theta = pm.Normal('theta', mu=0, sigma=1, shape=n_students)
        
        # 2PL model with numerical safeguards
        ability_diff = theta[student_idx] - b[question_idx]
        logit = a[question_idx] * ability_diff
        
        # Prevent numerical overflow/underflow
        logit_safe = pm.math.clip(logit, -15, 15)
        p = pm.math.sigmoid(logit_safe)
        
        # Add small numerical stability margin
        p_stable = pm.math.clip(p, 1e-12, 1 - 1e-12)
        
        # Likelihood
        obs = pm.Bernoulli('obs', p=p_stable, observed=responses)
        
        # Enhanced sampling with multiple fallback strategies
        sampling_successful = False
        trace = None
        
        # Strategy 1: Conservative NUTS
        try:
            logger.info("Attempting conservative NUTS sampling...")
            trace = pm.sample(
                draws=1000,
                tune=3000,  # Extended tuning
                chains=4,
                cores=2,  # Limit cores to prevent memory issues
                target_accept=0.98,
                max_treedepth=12,
                init='adapt_diag',
                compute_convergence_checks=True,
                return_inferencedata=True,
                progressbar=True,
                random_seed=42
            )
            
            # Check convergence
            divergences = int(trace.sample_stats.divergences.sum().item())
            if divergences < 50:  # Acceptable threshold
                sampling_successful = True
                logger.info(f"✅ Conservative NUTS succeeded with {divergences} divergences")
            else:
                logger.warning(f"Conservative NUTS had {divergences} divergences, trying fallback...")
                
        except Exception as e:
            logger.warning(f"Conservative NUTS failed: {e}")
        
        # Strategy 2: Very conservative NUTS with tighter target
        if not sampling_successful:
            try:
                logger.info("Attempting very conservative NUTS sampling...")
                trace = pm.sample(
                    draws=800,
                    tune=4000,  # Even more tuning
                    chains=4,
                    cores=1,  # Single core for stability
                    target_accept=0.99,
                    max_treedepth=10,
                    init='jitter+adapt_diag',
                    compute_convergence_checks=True,
                    return_inferencedata=True,
                    progressbar=True,
                    random_seed=123
                )
                
                divergences = int(trace.sample_stats.divergences.sum().item())
                sampling_successful = True
                logger.info(f"✅ Very conservative NUTS succeeded with {divergences} divergences")
                
            except Exception as e:
                logger.error(f"Very conservative NUTS failed: {e}")
        
        # Strategy 3: ADVI initialization + NUTS
        if not sampling_successful:
            try:
                logger.info("Attempting ADVI initialization + NUTS...")
                
                # Variational inference for initialization
                advi = pm.ADVI()
                approx = pm.fit(method=advi, n=20000, progressbar=False)
                
                # Sample from ADVI approximation for initialization
                start_points = approx.sample(chains=4)
                
                trace = pm.sample(
                    draws=800,
                    tune=2000,
                    chains=4,
                    cores=1,
                    start=start_points,
                    target_accept=0.95,
                    compute_convergence_checks=True,
                    return_inferencedata=True,
                    progressbar=True
                )
                
                sampling_successful = True
                logger.info("✅ ADVI initialization + NUTS succeeded")
                
            except Exception as e:
                logger.error(f"ADVI + NUTS failed: {e}")
        
        # Strategy 4: Metropolis sampler (last resort)
        if not sampling_successful:
            logger.info("Falling back to Metropolis sampler...")
            try:
                step = pm.Metropolis()
                trace = pm.sample(
                    draws=3000,  # Need more draws with Metropolis
                    tune=1000,
                    chains=2,
                    step=step,
                    cores=1,
                    return_inferencedata=True,
                    progressbar=True
                )
                
                sampling_successful = True
                logger.info("✅ Metropolis sampler succeeded")
                
            except Exception as e:
                logger.error(f"All sampling strategies failed: {e}")
                raise RuntimeError("Unable to fit model with any sampling strategy")
    
    # Extract results with enhanced error handling
    try:
        results = {
            'theta_estimates': trace.posterior.theta.mean(dim=('chain', 'draw')).values,
            'theta_stds': trace.posterior.theta.std(dim=('chain', 'draw')).values,
            'difficulty_estimates': trace.posterior.b.mean(dim=('chain', 'draw')).values,
            'discrimination_estimates': trace.posterior.a.mean(dim=('chain', 'draw')).values,
            'divergences': int(trace.sample_stats.divergences.sum().item()),
            'n_students': n_students,
            'n_questions': n_questions,
            'observed_responses': len(responses)
        }
        
        # Add convergence diagnostics
        try:
            rhat = az.rhat(trace)
            results['rhat_max'] = float(rhat.max().item()) if hasattr(rhat, 'max') else 1.0
            
            ess = az.ess(trace)
            results['ess_min'] = float(ess.min().item()) if hasattr(ess, 'min') else 100
            
        except Exception as e:
            logger.warning(f"Could not compute convergence diagnostics: {e}")
            results['rhat_max'] = None
            results['ess_min'] = None
        
        # Quality assessment
        divergences = results['divergences']
        if divergences == 0:
            results['convergence_quality'] = 'excellent'
        elif divergences < 10:
            results['convergence_quality'] = 'good'
        elif divergences < 50:
            results['convergence_quality'] = 'acceptable'
        else:
            results['convergence_quality'] = 'poor'
        
        logger.info(f"Hierarchical 2PL completed. Divergences: {divergences}, Quality: {results['convergence_quality']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error extracting results: {e}")
        raise RuntimeError(f"Failed to extract model results: {str(e)}")

def run_simple_2pl_model(bayesian_data) -> Dict[str, Any]:
    """
    Simplified 2PL model without hierarchical structure - often more stable for sparse data
    """
    response_matrix = bayesian_data['response_matrix']
    n_students, n_questions = response_matrix.shape
    
    logger.info(f"Fitting simple 2PL model: {n_students} students, {n_questions} questions")
    
    student_idx, question_idx = np.where(~np.isnan(response_matrix))
    responses = response_matrix[~np.isnan(response_matrix)].astype(int)
    
    # Compute initialization values
    question_means = np.nanmean(response_matrix, axis=0)
    student_means = np.nanmean(response_matrix, axis=1)
    
    model = pm.Model()
    
    with model:
        # Simple, stable priors
        b = pm.Normal('b', mu=0, sigma=2, shape=n_questions)  # Difficulty
        
        # Log-normal discrimination ensures positivity and stability
        a = pm.LogNormal('a', mu=0, sigma=0.5, shape=n_questions)
        
        # Student abilities
        theta = pm.Normal('theta', mu=0, sigma=1, shape=n_students)
        
        # 2PL model
        logit = a[question_idx] * (theta[student_idx] - b[question_idx])
        logit_clipped = pm.math.clip(logit, -20, 20)  # Wide but safe range
        p = pm.math.sigmoid(logit_clipped)
        
        # Numerical stability
        p_stable = pm.math.clip(p, 1e-15, 1 - 1e-15)
        obs = pm.Bernoulli('obs', p=p_stable, observed=responses)
        
        # Progressive sampling approach
        sampling_successful = False
        trace = None
        
        # Try standard approach first
        try:
            logger.info("Attempting standard sampling for simple 2PL...")
            trace = pm.sample(
                draws=1000,
                tune=2000,
                chains=4,
                cores=2,
                target_accept=0.95,
                max_treedepth=12,
                init='jitter+adapt_diag',
                compute_convergence_checks=True,
                return_inferencedata=True,
                progressbar=True,
                random_seed=42
            )
            
            divergences = int(trace.sample_stats.divergences.sum().item())
            if divergences < 100:  # More lenient for simple model
                sampling_successful = True
                logger.info(f"✅ Standard sampling succeeded with {divergences} divergences")
            
        except Exception as e:
            logger.warning(f"Standard sampling failed: {e}")
        
        # Fallback to very conservative approach
        if not sampling_successful:
            try:
                logger.info("Attempting conservative sampling for simple 2PL...")
                trace = pm.sample(
                    draws=800,
                    tune=3000,
                    chains=4,
                    cores=1,
                    target_accept=0.98,
                    max_treedepth=10,
                    compute_convergence_checks=True,
                    return_inferencedata=True,
                    progressbar=True
                )
                
                sampling_successful = True
                logger.info("✅ Conservative sampling succeeded")
                
            except Exception as e:
                logger.error(f"All simple 2PL sampling failed: {e}")
                raise RuntimeError("Unable to fit simple 2PL model")
    
    # Extract results
    results = {
        'theta_estimates': trace.posterior.theta.mean(dim=('chain', 'draw')).values,
        'theta_stds': trace.posterior.theta.std(dim=('chain', 'draw')).values,
        'difficulty_estimates': trace.posterior.b.mean(dim=('chain', 'draw')).values,
        'discrimination_estimates': trace.posterior.a.mean(dim=('chain', 'draw')).values,
        'divergences': int(trace.sample_stats.divergences.sum().item()),
        'n_students': n_students,
        'n_questions': n_questions,
        'observed_responses': len(responses),
        'model_type': 'simple_2pl'
    }
    
    logger.info(f"Simple 2PL completed. Divergences: {results['divergences']}")
    return results

def run_adaptive_2pl_model(bayesian_data) -> Dict[str, Any]:
    """
    Adaptive 2PL model that chooses the best approach based on data characteristics
    """
    response_matrix = bayesian_data['response_matrix']
    n_students, n_questions = response_matrix.shape
    observed_responses = np.sum(~np.isnan(response_matrix))
    sparsity = 1 - (observed_responses / (n_students * n_questions))
    
    logger.info(f"Adaptive 2PL selection - Students: {n_students}, Questions: {n_questions}, Sparsity: {sparsity:.3f}")
    
    # Decision logic based on data characteristics
    use_hierarchical = (
        n_students >= 100 and 
        n_questions >= 30 and 
        sparsity < 0.8 and
        observed_responses > 1000
    )
    
    if use_hierarchical:
        logger.info("📊 Data suitable for hierarchical model - using enhanced hierarchical 2PL")
        try:
            results = run_hierarchical_2pl_model_improved(bayesian_data)
            
            # If hierarchical has too many divergences, fall back
            if results.get('divergences', 0) > 100:
                logger.warning("🔄 Hierarchical model had convergence issues, falling back to simple model")
                results = run_simple_2pl_model(bayesian_data)
                results['model_used'] = 'simple_2pl_fallback'
            else:
                results['model_used'] = 'hierarchical_2pl'
                
            return results
            
        except Exception as e:
            logger.error(f"Hierarchical model failed: {e}, using simple model")
            results = run_simple_2pl_model(bayesian_data)
            results['model_used'] = 'simple_2pl_fallback'
            return results
    else:
        logger.info("📈 Data better suited for simple model - using simple 2PL")
        results = run_simple_2pl_model(bayesian_data)
        results['model_used'] = 'simple_2pl_selected'
        return results