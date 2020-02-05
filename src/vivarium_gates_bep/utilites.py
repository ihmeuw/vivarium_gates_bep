import numpy as np
import scipy.stats


def sanitize_location(location: str):
    """Cleans up location formatting for writing and reading from file names.

    Parameters
    ----------
    location
        The unsanitized location name.

    Returns
    -------
        The sanitized location name (lower-case with white-space and
        special characters removed.

    """
    # FIXME: Should make this a reversible transformation.
    return location.replace(" ", "_").replace("'", "_").lower()


def sample_beta_distribution(seed: int, mean: float, variance: float, upper_bound: float, lower_bound: float) -> float:
    """Gets a single random draw from a scaled beta distribution.

    Parameters
    ----------
    seed
        Seed for the random number generator.
    mean
        The mean of the scaled beta distribution.
    variance
        The variance of the scaled beta distribution.
    upper_bound
        The upper bound of the support of the scaled beta distribution.
    lower_bound
        The lower bound of the support of the scaled beta distribution.

    Returns
    -------
        The random variate from the scaled beta distribution.

    """
    np.random.seed(seed)
    support_width = (upper_bound - lower_bound)
    mean = (mean - lower_bound) / support_width
    variance /= support_width ** 2
    alpha = mean * (mean * (1 - mean) / variance - 1)
    beta = (1 - mean) * (mean * (1 - mean) / variance - 1)
    return lower_bound + support_width*scipy.stats.beta.rvs(alpha, beta)


