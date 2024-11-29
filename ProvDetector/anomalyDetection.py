import pandas as pd
import numpy as np
import plotly.express as px
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
from sklearn.neighbors import LocalOutlierFactor


def LOF(train_vec, vec_ans, doc_train, doc_ans):
    data_train = train_vec
    data = vec_ans
    clf = LocalOutlierFactor(n_neighbors=3, algorithm='brute', leaf_size=30, metric='minkowski', p=2, metric_params=None,
                             n_jobs=4, novelty=True)
    clf = clf.fit(data_train)
    predict = clf.predict(data)
    negative_outlier_factor = clf.negative_outlier_factor_

    x = np.array(train_vec + vec_ans)
    train_and_predict = np.concatenate((np.zeros(shape=(len(train_vec))), predict), axis=None)
    tsne = TSNE(n_components=2, perplexity=30)
    x_tsne = tsne.fit_transform(x)

    # print(x_tsne.shape)
    # print(len(doc_ans))
    # print()
    data = pd.DataFrame({
        'x': x_tsne[:, 0],
        'y': x_tsne[:, 1],
        'predict': train_and_predict,
        'text': doc_train + doc_ans
    })

    print(data)

    return predict
