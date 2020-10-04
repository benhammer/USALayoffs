# Read all of the warn notices CSV files. Add geolocation
# information to each record. Then divide the notices into
# clusters so that client browsers can easily download
# subsets of the data near the user's latitude/longitude
# coordinate, and save those clusters to JSON files that
# the client browser can find easily.

import csv
import glob
import json

import numpy
import scipy.cluster.vq

warn_notices = []

# Read in all of the warn notices.
for wnf in glob.glob("warn-notices/*.csv"):
  for rec in csv.DictReader(open(wnf, encoding="latin-1")): # encoding necessary because I'm running this script on Linux but the files were created in Windows where the default encoding is latin1
    warn_notices.append(rec)

# Geolocate all of the warn notices.
for wn in warn_notices:
  # assign a random lat/lng
  import random
  lat = 35 + 15 * random.random()
  lng = -100 + 50 * random.random()
  wn["latitude"] = lat
  wn["longitude"] = lng

# Assign warn notices to automatically generated clusters.
# Although states are natural clusters that we already have,
# they don't divide up the data evenly. We'll use k-means
# clustering to identify groups of nearby warn notices.
# See https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.vq.kmeans.html
CLUSTER_COUNT = 5
warn_notice_locations = [(wn["latitude"], wn["longitude"]) for wn in warn_notices]
warn_notice_locations = scipy.cluster.vq.whiten(warn_notice_locations) # see scipy link
cluster_centers, _ = scipy.cluster.vq.kmeans(warn_notice_locations, CLUSTER_COUNT)
cluster_numbers, _ = scipy.cluster.vq.vq(warn_notice_locations, cluster_centers)

# Write out each cluster to a separate JSON file. Make
# the output format compact to minimize network usage
# and speed up loading.
cluster_centers = []
for ci in range(CLUSTER_COUNT):
  with open("../www/warn-notices-shards/{}.json".format(ci), "w") as f:
    cluster = []
    for i in range(len(warn_notices)):
      if cluster_numbers[i] == ci:
        wn = warn_notices[i]
        cluster.append([
          wn["company"],
          wn["effective_date"],
          wn["number_of_workers"],
          wn["location"],
          round(wn["latitude"], 4),
          round(wn["longitude"], 4),
        ])
    json.dump(cluster, f)

# Write an index file that that client browser will load
# initially to know how many clusters there are and where
# their centerpoints are.
with open("../www/warn-notices-shards/index.js", "w") as f:
  # Recompute the cluster centers because scipy.cluster.vq.whiten
  # mangled our coordinates so cluster_centers is not meaningful.
  cluster_centers = [
    {
      "cluster": ci,
      "center": (numpy.mean([wn["latitude"] for i, wn in enumerate(warn_notices) if cluster_numbers[i] == ci]),
                numpy.mean([wn["longitude"] for i, wn in enumerate(warn_notices) if cluster_numbers[i] == ci]))
    }
    for ci in range(CLUSTER_COUNT)
  ]

  print(
    "warn_notice_clusters="
    + json.dumps(cluster_centers)
    + ";",
    file=f)
