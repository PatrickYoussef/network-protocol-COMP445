# network-protocol-COMP445
This is the lab assignment for our COMP 445 course which requires us to develop an HTTP server/client network protocol using TCP. The client can be used by itself to send requests to the web by changing the port number connection to 80 and the host to "parsedUrl.netloc". If the server and client are started together, the client is used to send requests to ther server to read and write files in the root directory in the project.

# Requirements
1. Python 3+

# Run httpfs.py (Server)

python httpfs.py [-v] [-p] [-d]

-v (verbose): outputs socket connections and requests status

-p (port): Specifies the port number that the server will listen and serve at

-d (directory): Specifies the directory the server will read/write files at.

# Examples

1- 
  python httpfs.py -v -p 8080 OR python httpfs.py -v -p 8080 -d /foo

  WITH

  python httpc.py GET https://locahost:8080/ -v
  python httpc.py GET https://locahost:8080/foo -v -h Content-Type:application/json
  python httpc.py POST https://locahost:8080/bar -v -h Content-Type:application/json


# Run httpc.py (Client)

python httpc.py (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL

-v (verbose): outputs requests status, headers and contents

-h (headers): key-value pairs of HTTP request headers, ex: Content-Type:application/json, Connection:close\

-d (data): JSON to be sent when doing a POST request

-f (file): file containing JSON that will be sent in a POST request

-URL: URL (including path)

# Examples

1- python httpc.py post -v -h "Content-Type:application/json" "Cache-Control: max-age=0" "Connection: close" -f "body_request.json" "http://httpbin.org/post?coure=networking&assignment=1&ID=48343483W8734W439T73W89T738T73W9T"

2- python httpc.py post -v -h "Content-Type:application/json" "Cache-Control: max-age=0" "Connection: close" -d "{\"Assignemnt\": 1, \"Course\": \"Networking\"}" "http://httpbin.org/post"

3- python httpc.py get https://httpbin.org/get -v -h "Content-Type:application/json" "Cache-Control: max-age=0" "Connection: close" 
