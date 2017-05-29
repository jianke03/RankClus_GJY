'''
author: Gaojingyue
mail: gaojingyue1997@pku.edu.cn
date: 2017.05.18
function: provide some basic functions needed in rankclus algorithm,
including building the bi-type network,Simple Ranking,Authority Ranking
'''
import csv
from collections import defaultdict
import random
import numpy as np
'''
build the bi-type according to refined_info file extracted from the xml file
provided by website of dblp
'''


def buildNet(filename):
    authorSet = set()
    conferSet = set()
    file0 = open(filename, 'r')
    reader0 = csv.reader(file0)
    for line in reader0:
        conferSet.add(line[0])
        for i in range(2, len(line)):
            authorSet.add(line[i])
    file0.close()

    confer_author = {}
    author_confer = {}
    author_author = {}
    for confer in conferSet:
        confer_author[confer] = defaultdict(int)
    for author in authorSet:
        author_confer[author] = defaultdict(int)
        author_author[author] = defaultdict(int)

    file0 = open(filename, 'r')
    reader0 = csv.reader(file0)
    for line in reader0:
        temp_confer = line[0]
        length = len(line)
        for i in range(2, length):
            confer_author[temp_confer][line[i]] += 1
            author_confer[line[i]][temp_confer] += 1
            for j in range(i + 1, length):
                author_author[line[i]][line[j]] += 1
                author_author[line[j]][line[i]] += 1
    file0.close()
    return author_confer, confer_author, author_author


'''
initializeCluster
initialize K clusters of conferences and make sure that every conference
is not null
'''


def initializeCluster(allConferList, K=15):
    allConferList = list(allConferList)
    random.shuffle(allConferList)
    meetRequire = False
    while not meetRequire:
        meetRequire = True
        cluster = defaultdict(list)
        for confer in allConferList:
            randid = random.randint(0, K - 1)
            cluster[randid].append(confer)
        for i in range(K):
            if len(cluster[i]) == 0:
                meetRequire = False
                print('initialize error and try again!')
                break
    return cluster


'''
specificInitialize
Combining some domain knowledge, we can specify a conference for some clusters 
to help obtain a better result in less iterations
'''


def specificInitialize(allConferList, K=15):
    allConferList = list(allConferList)
    random.shuffle(allConferList)
    meetRequire = False
    while not meetRequire:
        meetRequire = True
        cluster = defaultdict(list)
        domainHead = [
            'FAST', 'MobiCom', 'CRYPTO', 'OSDI', 'VLDB', 'SIGIR', 'STOC',
            'ACM Multimedia', 'AAAI', 'UbiComp', 'RTSS'
        ]
        for i in range(len(domainHead)):
            cluster[i].append(domainHead[i])
        for confer in allConferList:
            if confer in domainHead:
                continue
            randid = random.randint(0, K - 1)
            cluster[randid].append(confer)
        for i in range(K):
            if len(cluster[i]) == 0:
                meetRequire = False
                print('initialize error and try again!')
                break
    return cluster


'''
Simple Rank
compute the conditional score of authors and conferences in specific conference 
cluster and within-cluster rank of each conference in the cluster
'''


def simpleRank(author_confer, confer_author, author_author, clusterList):
    numSub = 0
    confer_score_in = defaultdict(float)
    author_score = defaultdict(float)
    confer_score = defaultdict(float)
    for confer in clusterList:
        for author in confer_author[confer]:
            temp = confer_author[confer][author]
            confer_score_in[confer] += temp
            author_score[author] += temp
            numSub += temp
    for confer in confer_author_in:
        confer_score_in[confer] = float(
            confer_score_in[confer]) / float(numSub)
    for author in author_confer:
        author_score[author] = float(author_score[author]) / float(numSub)

    sumConferScore = 0
    for confer in confer_author:
        conferScore = 0
        for author in confer_author[confer]:
            conferScore += (
                confer_author[confer][author] * author_score[author])
        confer_score[confer] = conferScore
        sumConferScore += conferScore
    for confer in confer_score:
        confer_score[confer] = confer_score[confer] / float(sumConferScore)

    return author_score, confer_score, confer_score_in


'''
Authority Rank
Another way to compute the conditional score of authors and conferences over specific
research area. This ranking function is more specific than Simple Rank
'''


def authorityRank(author_confer,
                  confer_author,
                  author_author,
                  clusterList,
                  T=10,
                  alpha=0.95):
    confer_score_in = defaultdict(float)
    author_score = defaultdict(float)
    confer_score = defaultdict(float)
    iniPercent = 1.0 / float(len(author_confer))
    for author in author_confer:
        author_score[
            author] = iniPercent  # the initial score for each author in this research area
    for i in range(T):
        sumConferScore = 0.0
        for confer in clusterList:
            conferScore = 0.0
            for author in confer_author[confer]:
                conferScore += (
                    confer_author[confer][author] * author_score[author])
            confer_score_in[confer] = conferScore
            sumConferScore += conferScore
        for confer in confer_score_in:
            confer_score_in[confer] = confer_score_in[confer] / float(
                sumConferScore)  # normalization
        #up to now, the score of conference within the clsuter has been computed
        last_author_score = author_score.copy()
        for author in author_score:
            author_score[author] = 0.0
        for confer in clusterList:
            for author in confer_author[confer]:
                author_score[author] += (
                    confer_author[confer][author] * confer_score_in[confer] *
                    (alpha))
        for author in author_score:
            for co_author in author_author[author]:
                author_score[author] += (
                    last_author_score[co_author] *
                    (1 - alpha) * author_author[author][co_author])
        sumAuthorScore = 0.0
        for author in author_score:
            sumAuthorScore += author_score[author]
        for author in author_score:
            author_score[author] /= float(sumAuthorScore)
        #up to now, the score of author has been computed

    sumConferScore = 0
    for confer in confer_author:
        conferScore = 0
        for author in confer_author[confer]:
            conferScore += (
                confer_author[confer][author] * author_score[author])
        confer_score[confer] = conferScore
        sumConferScore += conferScore
    for confer in confer_score:
        confer_score[confer] = confer_score[confer] / float(sumConferScore)
    # up to now, the score of all conferences has been computed in this cluster		

    return author_score, confer_score, confer_score_in


'''
EM Algorithm
each iteration consists of esimation and modification of P(z=k|x_i,y_j,theta)
finally we get theta, which represents each conference's distribution over each 
research cluster to help us do better clustering next
'''


def EM(confer_author, confer_score_list, author_score_list, cluster, t=5,
       K=15):
    Pro_k = {}
    sumPapers = 0
    for i in range(K):
        Pro_k[i] = 0
        for confer in cluster[i]:
            for author in confer_author[confer]:
                Pro_k[i] += confer_author[confer][author]
                sumPapers += confer_author[confer][author]
    for i in range(K):
        Pro_k[i] /= float(sumPapers)
        # the initial probalibity for p(z=k)
    sumLinkWeights = 0.0
    for confer in confer_author:
        for author in confer_author[confer]:
            sumLinkWeights += confer_author[confer][author]
    for iters in range(
            t):  # t is the iteration number of EM algorithm            
        Pro_confer_author_k = {}
        for confer in confer_author:
            Pro_confer_author_k[confer] = {}
            for author in confer_author[confer]:
                Pro_confer_author_k[confer][author] = {}
                sumLinkWeights += confer_author[confer][author]
                sumPro = 0.0
                for k in range(K):
                    temp = confer_score_list[k][confer] * author_score_list[k][
                        author] * Pro_k[k]
                    sumPro += temp
                    Pro_confer_author_k[confer][author][k] = temp
                for k in range(K):
                    Pro_confer_author_k[confer][author][k] /= float(sumPro)
        # up to now, the Estimation step has completed
        for k in range(K):
            Pro_k[k] = 0.0
            for confer in confer_author:
                for author in confer_author[confer]:
                    Pro_k[k] += Pro_confer_author_k[confer][author][
                        k] * confer_author[confer][author]
            Pro_k[k] /= sumLinkWeights
    Pro_confer_cluster = {}
    for confer in confer_author.keys():
        sumPro = 0.0
        Pro_confer_cluster[confer] = []
        for k in range(K):
            temp = confer_score_list[k][confer] * Pro_k[k]
            sumPro += temp
            Pro_confer_cluster[confer].append(temp)
        Pro_confer_cluster[confer] = np.array(
            Pro_confer_cluster[confer]) / float(sumPro)

    # using the p(z=k), we get the distribution of every conference over each cluster(research area)       
    return Pro_confer_cluster


'''
calSimi
This function aims at calculate the similarity between
one conference and the center of one cluster, to help us
re-assign the conference to its nearest cluster
'''


def calSimi(a, b):
    sumMul = np.sum(a * b)
    sumA = np.sqrt(np.sum(a * a))
    sumB = np.sqrt(np.sum(b * b))
    simi = float(sumMul) / (float(sumA * sumB))
    return simi


'''
clusterReassign
re-assign every conference to its nearest cluster center according to 
the similarity between the conference and the center of the cluster
'''


def clusterReassign(cluster, Pro_confer_cluster, K=15):
    center = {}
    for k in range(K):
        center[k] = np.zeros(15)
        conferNum = len(cluster[k])
        for confer in cluster[k]:
            center[k] += Pro_confer_cluster[confer]
        center[k] /= float(conferNum)
    # up tp now, we have computed the center of each cluster    
    newcluster = defaultdict(list)
    for confer in Pro_confer_cluster:
        maxSimi = -1
        maxid = -1
        for i in range(K):
            tempSimi = calSimi(Pro_confer_cluster[confer], center[i])
            if tempSimi > maxSimi:
                maxSimi = tempSimi
                maxid = i
        assert (maxid != -1)
        newcluster[maxid].append(confer)
    return newcluster


'''
checkNull
This function aims at check K clusters in clustering result are 
all not null
'''


def checkNull(cluster, K):
    result = False
    for i in range(K):
        if len(cluster[i]) == 0:
            result = True
            break
    return result
