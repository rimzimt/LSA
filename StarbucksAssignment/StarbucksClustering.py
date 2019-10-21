#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 18:08:23 2019

@author: rimzimthube
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram,linkage
from sklearn.cluster import AgglomerativeClustering

#Load the points in array
X= np.array([[1,5],
         [1,7],
         [2,6],
         [2,9],
         [3,6],
         [3,8],
         [3,8],
         [3,9],
         [4,8],
         [4,8],
         [3,3],
         [5,4],
         [7,2],
         [5,7],
         [4,5],
         [6,9],
         [7,3],
         [7,9],
         [8,1],
         [8,7]])

# Plot the points 
plt.scatter(X[:,0],X[:,1], label='True Position')
plt.title('Plotted points')
plt.show()

#Single Link Cluster
singleLinkCluster=AgglomerativeClustering(n_clusters=3,linkage='single').fit(X)
plt.title('Single Link Cluster')
plt.scatter(X[:,0],X[:,1], c=singleLinkCluster.labels_, cmap='rainbow')
plt.savefig('/Users/rimzimthube/MS/SingleLink.png')
plt.show()

#Complete Link Cluster
completeLinkCluster=AgglomerativeClustering(n_clusters=3,linkage='complete').fit(X)
plt.title('Complete Link Cluster')
plt.scatter(X[:,0],X[:,1], c=completeLinkCluster.labels_, cmap='rainbow')
plt.savefig('/Users/rimzimthube/MS/CompleteLink.png')
plt.show()

#Average Link Cluster
avgLinkCluster=AgglomerativeClustering(n_clusters=3,linkage='average').fit(X)
plt.title('Average Link Cluster')
plt.scatter(X[:,0],X[:,1], c=avgLinkCluster.labels_, cmap='rainbow')
plt.savefig('/Users/rimzimthube/MS/AverageLink.png')
plt.show()

#Single link cluster
print('Single Link Cluster \n')

singleLinked=linkage(X,method='single')
dendrogram(singleLinked,orientation='top',distance_sort='descending',show_leaf_counts='True')
#plt.show()
plt.title('Single Link Cluster')
plt.savefig('/Users/rimzimthube/MS/SingleLinkDendrogram.png')
plt.show()

#Complete link cluster
print('Complete Link Cluster \n')
completeLinked=linkage(X,method='complete')
dendrogram(completeLinked,orientation='top',distance_sort='descending',show_leaf_counts='True')
#plt.show()
plt.title('Complete Link Cluster')
plt.savefig('/Users/rimzimthube/MS/CompleteLinkDendrogram.png')
plt.show()


print('Average Link Cluster \n')
averageLinked=linkage(X,method='average')
dendrogram(averageLinked,orientation='top',distance_sort='descending',show_leaf_counts='True')
#plt.show()
plt.title('Average Link Cluster')
plt.savefig('/Users/rimzimthube/MS/AverageLinkDendrogram.png')
plt.show()
