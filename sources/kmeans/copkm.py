import numpy as np
from numpy import linalg as npl

from .common import initialize_centers, tolerance
from scipy.spatial.distance import cdist as dist

class COPKMeans:
    def __init__(self, n_clusters=2, max_iter=100, tol=1e-4, init=None, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.init = init
        self.random_state = random_state

        # Initialization variables
        self.cluster_centers_ = None

        # Result variables
        self.labels_ = None
        self.n_iter_ = 0

    def fit(self, X, const_mat=None):
        self._initialize(X, const_mat)

        return self._fit(X, const_mat)

    def partial_fit(self, X, const_mat=None):
        if self.cluster_centers_ is None:
            self._initialize(X, const_mat)

        return self._fit(X, const_mat)

    def _initialize(self, X, const_mat=None):
        self.cluster_centers_ = initialize_centers(X, self.n_clusters, self.init, const_mat=const_mat, random_state=self.random_state)

    def _fit(self, X, const_mat=None):
        tol = tolerance(X, self.tol)

        for iteration in range(self.max_iter):
            # Assign clusters
            self.labels_ = self.assign_clusters(X, const_mat)

            if -1 in self.labels_:
                return self # exit - no solution

            # Estimate new centers
            prev_cluster_centers = self.cluster_centers_.copy()
            self.cluster_centers_ = np.array([
                X[self.labels_ == i].mean(axis=0)
                for i in range(self.n_clusters)
            ])

            # Check for convergence
            if npl.norm(self.cluster_centers_ - prev_cluster_centers) < tol:
                break

        self.n_iter_ = iteration + 1

        return self

    def assign_clusters(self, X, const_mat):
        labels = np.full(X.shape[0], fill_value=-1)
        cdist = dist(X, self.cluster_centers_)

        for i in range(len(X)):
            for j in cdist[i].argsort():
                # check violate contraints
                for _ in labels[np.argwhere(const_mat[i] == 1)]:
                    if not (_ == j or j == -1):
                        continue

                if np.any(labels[np.argwhere(const_mat[i] == -1)] == j):
                    continue

                labels[i] = j
                break

        return labels
