from base import buildNet, initializeCluster, authorityRank, simpleRank
from base import clusterReassign, EM, checkNull
import heapq
import numpy as np
T = 2
K = 15
rankT = 10
alpha = 0.95
EMT = 5
author_confer, confer_author, author_author = buildNet('../data/refined_info.txt')
cluster = initializeCluster(confer_author.keys(), K)
rankclus_iter = 0
while rankclus_iter < T:
    author_score_cluster = {}
    confer_score_cluster = {}
    confer_score_in_cluster = {}
    print('start ranking')
    for i in range(K):
        print('in ranking cluster ' + str(i))
        author_score_cluster[i], confer_score_cluster[
            i], confer_score_in_cluster[i] = authorityRank(
                author_confer, confer_author, author_author, cluster[i], rankT,
                alpha)
    print('start EM')
    Pro_confer_cluster = EM(confer_author, confer_score_cluster,
                            author_score_cluster, cluster, EMT, K)
    print('start clustering')
    newcluster = clusterReassign(cluster, Pro_confer_cluster, K=15)
    del cluster
    cluster = newcluster
    if checkNull(cluster, K):
        del cluster
        cluster = initializeCluster(confer_author.keys(), K)
        print('have to restart again!')
        rankclus_iter = 0
    else:
        rankclus_iter += 1
    print('having iters ' + str(rankclus_iter) + '  times')

for i in range(K):
    author_score, confer_score, confer_score_in = authorityRank(
        author_confer, confer_author, author_author, cluster[i], rankT, alpha)
    top_10_confer = heapq.nlargest(10, confer_score_in.items(), lambda x: x[1])
    print('cluster  '+str(i))
    for confer in top_10_confer:
        print(confer[0])
    top_10_author = heapq.nlargest(10, author_score.items(), lambda x: x[1])
    print('- - -')
    for author in top_10_author:
        print(author[0])
    print('- - - - - - - - - - - - - - - - - ')    


