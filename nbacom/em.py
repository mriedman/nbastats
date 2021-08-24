import numpy as np
import scipy.stats
from copy import deepcopy



def main(K, x):
    print('Running {} EM algorithm...'
          .format('unsupervised'))

    # *** START CODE HERE ***
    # (1) Initialize mu and sigma by splitting the unlabeled data points uniformly at random
    # into K groups, then calculating the sample mean and covariance for each group
    # (2) Initialize phi to place equal probability on each Gaussian
    # phi should be a numpy array of shape (K,)
    # (3) Initialize the w values to place equal probability on each Gaussian
    # w should be a numpy array of shape (m, K)

    x_shuff = deepcopy(x)
    np.random.shuffle(x_shuff)
    mu = np.zeros((K, x.shape[1]))
    sigma = np.zeros((K, x.shape[1], x.shape[1]))
    n = x.shape[0]
    for j in range(K):
        xj = x_shuff[(n*j)//K:(n*(j+1))//K, :]
        mu[j] = np.mean(xj, axis=0)
        sigma[j] = np.cov(xj.T)

    phi = np.ones((K,)) / K
    n = x.shape[0]
    w = np.ones((n, K)) / K

    # *** END CODE HERE ***

    w = run_em(x, w, phi, mu, sigma)

    # Plot your predictions
    z_pred = np.zeros(n)
    if w is not None:  # Just a placeholder for the starter code
        for i in range(n):
            z_pred[i] = np.argmax(w[i])

    return z_pred

def run_em(x, w, phi, mu, sigma):
    """Problem 3(d): EM Algorithm (unsupervised).

    See inline comments for instructions.

    Args:
        x: Design matrix of shape (n_examples, dim).
        w: Initial weight matrix of shape (n_examples, k).
        phi: Initial mixture prior, of shape (k,).
        mu: Initial cluster means, list of k arrays of shape (dim,).
        sigma: Initial cluster covariances, list of k arrays of shape (dim, dim).

    Returns:
        Updated weight matrix of shape (n_examples, k) resulting from EM algorithm.
        More specifically, w[i, j] should contain the probability of
        example x^(i) belonging to the j-th Gaussian in the mixture.
    """
    eps = 1e-3  # Convergence threshold
    max_iter = 1000

    # Stop when the absolute change in log-likelihood is < eps
    it = 0
    ll = prev_ll = None
    ct = 0
    while it < max_iter and (prev_ll is None or np.abs(ll - prev_ll) >= eps):
        # E-step
        pdfs = np.array([scipy.stats.multivariate_normal.pdf(x, mean=i, cov=j, allow_singular=True) * k for i, j, k in zip(mu, sigma, phi)]).T
        w = pdfs / np.sum(pdfs, axis=1).reshape((-1,1))

        # M-step
        phi = np.sum(w, axis=0) / x.shape[0]
        mu = np.array([np.sum(w[:, j:j+1] * x, axis=0) for j in range(w.shape[1])])
        mu /= np.sum(w, axis=0).reshape((-1, 1))
        sigma = [(w[:, j:j+1] * (x - mu[j])).T @ (x - mu[j]) for j in range(w.shape[1])]
        sigma /= np.sum(w, axis=0).reshape((-1, 1, 1))

        # ll
        prev_ll = ll
        print(ll)

        print([np.linalg.det(j) for j in sigma])
        if any(np.linalg.det(j) < 1e-28 for j in sigma):
            pass

        pdfs = np.array([scipy.stats.multivariate_normal.pdf(x, mean=i, cov=j, allow_singular=True) * k for i, j, k in zip(mu, sigma, phi)]).T
        ll = np.sum(np.log(np.sum(pdfs, axis=1))).squeeze()
        ct += 1
        print('Iteration', ct, 'likelihood:', ll)

    return w