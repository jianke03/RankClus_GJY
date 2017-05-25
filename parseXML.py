'''
author : Gaojingyue 1400012965
mail: gaojingyue1997@pku.edu.cn
date: 2017.05.15
function : parse the xml contains the dataset from the website of dblp and transform it into the raw_data
needed by the RankClus Algorithm
the form of each record in raw_data are:

'''
import csv
import os
from collections import defaultdict


def parse(filename, tofile):
    file1 = open(filename, 'r')
    file2 = open(tofile, 'w')
    writer2 = csv.writer(file2)
    inConfer = False
    conferSet = set()
    for l in file1:
        l = l.strip()
        if '<inproceedings ' in l:
            inConfer = True
            author = []
            year = 2000
            conferName = ""
            continue
        if '</inproceedings>' in l:
            if year >= 1998 and year <= 2007:
                author.insert(0, year)
                author.insert(0, conferName)
                writer2.writerow(author)
                conferSet.add(conferName)
                inConfer = False
            continue
        if inConfer:
            if '<year>' in l:
                year = int(l.split('<year>')[1].split('</year>')[0])
                continue
            if '<author>' in l:
                author.append(l.split('<author>')[1].split('</author>')[0])
                continue
            if '<booktitle>' in l:
                conferName = l.split('<booktitle>')[1].split('</booktitle>')[0]
    file1.close()
    file2.close()
    print(len(conferSet))


'''
This function aims at filtering the authors whose publications > 13 
to get 20690 with most publications
'''


def filterAuthorByPubs(filename, tofile):
    file1 = open(filename, 'r')
    reader1 = csv.reader(file1)
    authorPubs = defaultdict(int)
    for line in reader1:
        for i in range(2, len(line)):
            authorPubs[line[i]] += 1
    file1.close()

    authorNum = 0
    for i in authorPubs:
        if authorPubs[i] > 13:
            authorNum += 1

    file1 = open(filename, 'r')
    file2 = open(tofile, 'w')
    writer2 = csv.writer(file2)
    reader1 = csv.reader(file1)
    conferSet = set()
    for line in reader1:
        newLine = []
        for i in range(2, len(line)):
            if authorPubs[line[i]] > 13:
                newLine.append(line[i])
        if len(newLine) > 0:
            newLine.insert(0, line[1])
            newLine.insert(0, line[0])
            conferSet.add(line[0])
            writer2.writerow(newLine)
    file1.close()
    file2.close()
    os.system('rm ' + filename)
    print(authorNum)
    print(len(conferSet))


parse('data/dblp.xml', 'data/raw_info.txt')
filterAuthorByPubs('data/raw_info.txt', 'data/refined_info.txt')
