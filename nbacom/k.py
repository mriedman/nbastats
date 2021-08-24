import numpy as np


def init_centroids(num_clusters, data):
    elem_coords = np.random.randint(0, data.shape[0], num_clusters)
    centroids_init = np.array([data[i] for i in elem_coords])

    return centroids_init


def update_centroids(centroids, data, max_iter=30):
    new_centroids = np.zeros(centroids.shape)

    for _ in range(max_iter):
        dist = np.array([np.linalg.norm(data - mu.reshape(1, -1), axis=1) for mu in centroids])
        min_dist = np.argmin(dist, axis=0)
        for i in range(dist.shape[0]):
            sh = data.shape[:-1] + (1,)
            ind = np.array(list(map(lambda x: x == i, min_dist))).reshape(sh)
            if np.sum(np.abs(ind * data)) == 0:
                new_centroids[i] = np.sum(ind * data, axis=0)
            else:
                new_centroids[i] = np.sum(ind * data, axis=0) / np.sum(ind)

        if np.linalg.norm(new_centroids-centroids) == 0 and _ >= 30:
            break

        centroids = new_centroids

    return new_centroids