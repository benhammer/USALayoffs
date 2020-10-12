# Pull ZIP code latitude/longitude coordinates from Geonames.org
# and write them out to a sharded flat-file database that makes
# it easy to efficiently query the database from the browser without
# any backend server. The Geonames database has a CC-BY license so
# credit must be given in the application.
#
# There are about 41,000 ZIP codes in the database, and with their
# lat/lng coordinate it's about 1MB of data, which a browser could
# load but it's kind of a lot of data for a browser to download and
# process. With state and place names, which might make for a nicer
# user experience, it's closer to 2MB of data.
#
# To make it efficient for a serverless query, this script break up
# the database into small files (shards) that the browser can load
# depending on the ZIP code actually entered by the user. To balance
# the ZIP codes across shards, we'll compute a fast hash of the ZIP
# code (implemented here and in the browser). At 200 shards, each shard
# is about 12k.
#
# This method was designed with the assumption that users will either
# not be making multiple queries and the queries are not likely to be
# geographically nearby, so that there's no reason to keep nearby
# ZIP codes in the same shard or to reduce the number of shards to
# reduce latency. The more shards the better. Each query is likely to
# lead to a different shard and therefore a new HTTP request.
#
# To generate the sharded database, run this script. It will download
# the ZIP code database from Geonames and write shard files in the
# zipcode-shards directory as ###.txt files.
#
# Here's an example client-side script for querying the database. The
# shard files must exist in the same HTTP path ("zipcode-shards/" relative
# to the location of the page), and since AJAX is used, this won't work
# if you browse to the file on your local hard drive --- it must be
# served over HTTP.
#
# lookup_zipcode("put a zip code here", function(info) {
#   if (info === undefined)
#     alert("Sorry, the ZIP code was not found in our database.")
#   else
#     alert("I got: " + JSON.stringify(info))
# })
#
# function lookup_zipcode(zipcode, cb) {
#   // The ZIP code database exists as sharded, flat files that we can
#   // access via AJAX. To find the shard, hash the ZIP code using the
#   // same method used to generate the database.
#   var SHARD_COUNT = 200;
#
#   // https://stackoverflow.com/a/7616484
#   var hash = 0, i, chr;
#   for (i = 0; i < zipcode.length; i++) {
#     chr   = zipcode.charCodeAt(i);
#     hash  = ((hash << 5) - hash) + chr;
#     hash |= 0; // Convert to 32bit integer
#   }
#   hash = hash % SHARD_COUNT;
#
#   var file = "zipcode-shards/" + hash + ".txt"
#   var ajax = new XMLHttpRequest();
#   ajax.addEventListener("load", function() {
#     // Successfully got the shard.
#     var shard = this.responseText;
#
#     // Parse the shard for the ZIP code.
#     var found = false;
#     shard.split("\n").forEach(function(record) {
#       var pipe = record.indexOf("|");
#       if (record.substr(0, pipe) != zipcode) return;
#       record = JSON.parse("[" + record.substr(pipe+1) + "]");
#       found = true;
#       cb({
#         latitude: record[0],
#         longitude: record[1],
#         state_code : record[2],
#         state_name: record[3],
#         county_name: record[4],
#         place_name: record[5]
#       })
#     })
#
#     // Not found.
#     if (!found)
#       cb();
#   });
#   ajax.addEventListener("error", function() {
#     // On error, just give a generic not-found response to the caller.
#     cb();
#   });
#   ajax.open("GET", file);
#   ajax.overrideMimeType("text/plain; charset=utf-8");
#   ajax.send();
# }

import csv
import io
import os
import urllib.request
import zipfile
from struct import pack
from collections import defaultdict
import json

SHARD_COUNT = 200

# Download the .zip (i.e. compressed) file.
req = urllib.request.urlopen("http://download.geonames.org/export/zip/US.zip")
zipf = zipfile.ZipFile(io.BytesIO(req.read()))

# Open the US.txt database inside it, decode it from UTF-8,
# and parse it as a tab-separated database.
zipd = zipf.open("US.txt")
stream = io.TextIOWrapper(zipd, encoding="utf8")
reader = csv.reader(stream, delimiter="\t")
shards = defaultdict(lambda : {})
for row in reader:
  zipcode = row[1]
  place_name = row[2]
  state_name = row[3]
  state_code = row[4]
  county_name = row[5]
  latitude = float(row[9])
  longitude = float(row[10])

  # Compute a simple hash in the range 0 to SHARD_COUNT-1.
  # Based on https://stackoverflow.com/a/7616484 plus modulo.
  h = 0
  for c in zipcode:
    h = ((h << 5) - h) + ord(c)
    h |= 0 # Convert to 32bit integer
    assert pack("i", h) # sanity check that it is a 32-bit integer
  shard = h % SHARD_COUNT

  # Add the record to a shard (in memory first).
  shards[shard][zipcode] = [latitude, longitude, state_code, state_name, county_name, place_name]

# Make a directory for the generated shard files.
os.makedirs("../www/zipcode-shards", exist_ok=True)

# Write out each shard.
for shard, data in shards.items():
  with open("../www/zipcode-shards/{}.txt".format(shard), "w") as f:
    # Write out each ZIP code as a record.
    for zipcode, record in sorted(data.items()):
      # Write the ZIP code plus a pipe.
      assert "|" not in zipcode
      f.write(zipcode + "|")

      # Write the other data as a JSON array without spaces
      # to make it as small as possible. And since we know
      # it's an array drop the brackets on the ends too.
      record = json.dumps(record, separators=(',', ':'))
      record = record[1:-1]
      f.write(record)

      # And end the record with a newline.
      f.write("\n")
