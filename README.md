# Elasticsearch cluster for practising
-----------
Basic Elasticsearch setup for practising (Docker, Python, elasticsearch-py)

For this demo I am using free API https://fabian7593.github.io/CountryAPI/ kindly provided by Fabian Rosales (https://github.com/fabian7593)

This repository created purely for demo pruposes. Please do not use it in production.

I have used Docker and official elasticsearch image to create a quick setup for anyone who would like to play around
with elasticsearch and try/learn the basics. Note that you will need to have docker preinstalled and official elasticsearch docker image pulled:

```console
docker pull docker.elastic.co/elasticsearch/elasticsearch:5.5.0
```
      
This is basic one node setup and you will not need docker-compose ordocker-machine

To be able to use this setup please clone the repo and follow the below guide.

**1. Make sure that Java virtual memory is set up to the minimum level on your host machine:**

```console
sudo sysctl -w vm.max_map_count=262144
```
the above is just a nicer way of:

```console
echo 262144 > /proc/sys/vm/max_map_count
```
**2. Now in separate terminal type this, note that you should be in the project root folder (i.e. where your Dockerfile is):**
```console
docker build --tag=elastic_test_img .
```
above command will craete custom docker image with `elastic_test_img` tag
   
**3. Create container now:**
```console
docker run -p 8771:8771 -ti -v /usr/share/elasticsearch/data elastic_test_img
```
**4. In different terminal type below command to make sure that elasticsearch node (server) can be accessed from host:**
```console
curl http://127.0.0.1:8771/_cat/health
```
**5. Now you need to craete a virtualenv on host machine and install elasticsearch-py package and requests module:**
```console
pip install elasticsearch
pip install requests
```
