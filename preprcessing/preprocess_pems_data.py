import os
import pickle
import random
from argparse import ArgumentParser
from itertools import product

import numpy as np
import pandas as pd
import networkx as nx

from causallearn.utils.PCUtils.BackgroundKnowledge import BackgroundKnowledge
from causallearn.graph.GraphNode import GraphNode


def get_adjacency_matrix(distance_df, sensor_ids, quantile=0.1):
    """
    Function modified from original DCRNN source code.
        :param distance_df: data frame with three columns: [from, to, distance].
        :param sensor_ids: list of sensor ids.
        :param quantile: entries that are not in Q<quantile> are set to zero for sparsity.
        :return:
    """
    num_sensors = len(sensor_ids)
    dist_mx = np.zeros((num_sensors, num_sensors), dtype=np.float32)
    adj_mx = np.ones((num_sensors, num_sensors), dtype=np.float32)
    dist_mx[:] = np.nan
    # Builds sensor id to index map.
    sensor_id_to_ind = {}
    for i, sensor_id in enumerate(sensor_ids):
        sensor_id_to_ind[sensor_id] = i

    # Fills cells in the matrix with distances.
    for row in distance_df.values:
        if row[0] not in sensor_id_to_ind or row[1] not in sensor_id_to_ind:
            continue
        dist_mx[sensor_id_to_ind[row[0]], sensor_id_to_ind[row[1]]] = row[2]
    print(np.any(np.all(np.isnan(dist_mx), axis=1) & np.all(np.isnan(dist_mx), axis=0)))
    # Calculates the standard deviation as theta.
    quantiles = np.maximum(np.nanquantile(dist_mx, quantile, keepdims=True, axis=1),
                           np.nanmin(dist_mx, keepdims=True, axis=1))
    # Make the adjacent matrix symmetric by taking the max.
    # adj_mx = np.maximum.reduce([adj_mx, adj_mx.T])

    # Sets entries that lower than a threshold, i.e., k, to zero for sparsity.
    adj_mx[dist_mx > quantiles] = 0
    adj_mx[np.isnan(dist_mx)] = 0
    # adj_mx[dist_mx == 0] = 0
    return sensor_ids, sensor_id_to_ind, adj_mx, dist_mx


def remove_isolated_ids(sensor_ids, dist_list):
    m = np.zeros((len(sensor_ids), len(sensor_ids)), dtype=np.float32)
    m[:] = np.nan
    for _, (i, j, d) in dist_list.iterrows():
        m[sensor_id_to_idx[i], sensor_id_to_idx[j]] = d
    quantiles = np.maximum(np.nanquantile(m, 0.05, keepdims=True, axis=1), np.nanmin(m, keepdims=True, axis=1))
    m[m > quantiles] = np.nan

    isolated_idxs = np.all(np.isnan(m), axis=1) & np.all(np.isnan(m), axis=0)
    isolated_idxs = [sensor_ids[idx] for idx, is_isolated in enumerate(isolated_idxs) if is_isolated]

    for id in isolated_idxs:
        sensor_ids.remove(id)
    return sensor_ids


def subsample_nodes(sensor_ids, adj_mx, dist_mx, num_nodes=20, top_k=4, seed=42):
    random.seed(seed)

    sensor_ids_sub = [sensor_ids[i] for i in np.argsort(np.sum(adj_mx, axis=1))[-(num_nodes // top_k):]]

    sensor_ids_idxs = [sensor_ids.index(sensor_id) for sensor_id in sensor_ids_sub]
    dist_mx[np.isnan(dist_mx)] = np.inf
    dist_mx_sub = dist_mx[sensor_ids_idxs]
    neighbours = np.argsort(dist_mx_sub, axis=1)[:, :top_k]

    sensor_ids_sub = set([sensor_ids[i] for i in neighbours.reshape(-1)]) & set(sensor_ids_sub)
    while len(sensor_ids_sub) < num_nodes:
        sensor_ids_sub.add(random.sample(sensor_ids, k=1)[0])

    while len(sensor_ids_sub) > num_nodes:
        sensor_ids_sub.pop()

    sensor_ids_sub = list(sensor_ids_sub)
    sensor_ids_idxs = [sensor_ids.index(sensor_id) for sensor_id in sensor_ids_sub]

    adj_mx = adj_mx[sensor_ids_idxs][:, sensor_ids_idxs]
    dist_mx = dist_mx[sensor_ids_idxs][:, sensor_ids_idxs]

    sensor_ids = sensor_ids_sub
    sensor_id_to_ind = {sensor_id: i for i, sensor_id in enumerate(sensor_ids)}
    return sensor_ids, sensor_id_to_ind, adj_mx, dist_mx


def process_window(w):
    date = w.pop('date').iloc[0]
    d = {f'{col}_{t}': w.loc[t, col] for col in w.columns for t in range(T)}
    d['day_of_the_week'] = date.day_of_week
    d['hour'] = date.hour
    return d


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--source_dir', default='data/')
    parser.add_argument('--num_nodes', default=20, type=int)
    parser.add_argument('--time_window', default=2, type=int)
    parser.add_argument('--seed', default=42, type=int)
    args = parser.parse_args()

    with open(os.path.join(args.source_dir, 'adj_mx_PEMS-BAY.pkl'), 'rb') as f:
        sensor_ids, sensor_id_to_idx, adj = pickle.load(f, encoding='latin-1')

    dist_list = pd.read_csv(os.path.join(args.source_dir, 'distances_bay_2017.csv'), header=None)
    dist_list = dist_list.astype({0: str, 1: str})
    dist_list.loc[dist_list[0] == dist_list[1], 2] = np.nan

    data = pd.read_csv(os.path.join(args.source_dir, 'PEMS-BAY.csv'))
    data = data.rename(columns={'Unnamed: 0': 'date'})

    sensor_ids = remove_isolated_ids(sensor_ids, dist_list)

    sensor_ids, _, adj_mx, dist_mx = get_adjacency_matrix(dist_list, sensor_ids, 0.1)
    sensor_ids, sensor_id_to_ind, adj_mx, dist_mx = \
        subsample_nodes(sensor_ids, adj_mx, dist_mx, args.num_nodes, seed=args.seed)

    T = args.time_window
    adj_list = {f'{sensor_id}_{i}': [] for sensor_id in sensor_ids for i in range(T)}
    adj_list['day_of_the_week'] = []
    adj_list['hour'] = []
    for sensor_id in sensor_ids:
        v = f'{sensor_id}_{0}'
        adj_list['day_of_the_week'].append(v)
        adj_list['hour'].append(v)

    for t in range(T - 1):
        for sensor_id in sensor_ids:
            adj_list[f'{sensor_id}_{t}'].append(f'{sensor_id}_{t + 1}')
            for v, adj in enumerate(adj_mx[sensor_id_to_ind[sensor_id]]):
                if adj > 0:
                    adj_list[f'{sensor_id}_{t}'].append(f'{sensor_ids[v]}_{t + 1}')

    data = data.drop(columns=[c for c in data.columns if c != 'date' and c not in sensor_ids])

    data['date'] = pd.to_datetime(data['date'])
    # TODO: refactor ugly
    windowed_data = [process_window(data.iloc[i:i + T].reset_index(drop=True)) for i in
                     range(0, data.shape[0] - T + 1, T)]
    windowed_df = pd.DataFrame(windowed_data)


    mapping = {col: idx for idx, col in enumerate(windowed_df.columns)}

    adj_list_mapped = {mapping[k]: [mapping[i] for i in v] for k, v in adj_list.items()}
    GT_graph = nx.from_dict_of_lists(adj_list_mapped, create_using=nx.DiGraph())

    background_knowledge = BackgroundKnowledge()

    day_of_the_week = GraphNode('day_of_the_week')
    hour = GraphNode('hour')

    for t in range(1, T):
        for sensor_id in sensor_ids:
            node_next = GraphNode(mapping[f'{sensor_id}_{t}'])

            for t_prim in range(t):
                node_prev = GraphNode(mapping[f'{sensor_id}_{t_prim}'])
                # prevent edges back in time
                background_knowledge.add_forbidden_by_node(node_next, node_prev)
            # assumptions about influence of day of week and hour
            # background_knowledge.add_forbidden_by_node(mapping[day_of_the_week], mapping[node_next])
            # background_knowledge.add_forbidden_by_node(mapping[hour], mapping[node_next])
    # uncomment to add more information to background_knowledge and forbid edges within first timestamp
    # for sensor_id1, sensor_id2 in product(sensor_ids, sensor_ids):
    #     node_prev = GraphNode(mapping[f'{sensor_id1}_{0}'])
    #     node_next = GraphNode(mapping[f'{sensor_id2}_{0}'])
    #
    #     background_knowledge.add_forbidden_by_node(node_next, node_prev)

    with open(os.path.join(args.source_dir, f'gt_pems_graph_{T}_{args.num_nodes}.pkl'), 'wb') as f:
        pickle.dump(GT_graph, f)

    with open(os.path.join(args.source_dir, f'background_knowledge_pems_graph_{T}_{args.num_nodes}.pkl'), 'wb') as f:
        pickle.dump(background_knowledge, f)

    windowed_df.to_csv(os.path.join(args.source_dir, f'windowed_data_{T}_{args.num_nodes}.csv'), index=False)
