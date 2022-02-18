# network-protocol-COMP445
This is the 1st lab for our COMP 445 course which requires us to develop a network protocol

# Requirements
1. Python 3+

# Run httpc.py

python httpc.py (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL

-v (verbose): outputs requests status, headers and contents

-h (headers): key-value pairs of HTTP request headers, ex: Content-Type:application/json, Connection:close\

-d (data): JSON to be sent when doing a POST request

-f (file): file containing JSON that will be sent in a POST request

-URL: URL (including path)
