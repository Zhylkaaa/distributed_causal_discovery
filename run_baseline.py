import pickle

import pandas as pd
from causallearn.search.ConstraintBased.PC import pc


if __name__ == '__main__':
    with open('data/gt_pems_graph_2_20.pkl', 'rb') as f:
        GT_graph = pickle.load(f)

    with open('data/background_knowledge_pems_graph_2_20.pkl', 'rb') as f:
        background_knowlage = pickle.load(f)

    windowed_df = pd.read_csv('data/windowed_data_2_20.csv')

    print(windowed_df.values.shape)
    print(GT_graph.number_of_nodes())

    cg = pc(windowed_df.values, indep_test='d_separation', true_dag=GT_graph,
            background_knowledge=background_knowlage)
