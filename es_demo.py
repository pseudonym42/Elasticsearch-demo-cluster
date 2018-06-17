import argparse
import json
import logging
import requests
import sys
from elasticsearch import Elasticsearch as ES


# create global logging object
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log_h = logging.StreamHandler()
log_f = logging.Formatter("%(levelname)s %(lineno)d %(message)s")
log_h.setFormatter(log_f)
log.addHandler(log_h)


class ElasticNodeNotAvailable(Exception):
    """
    Custom exception raised when elasticsearch node not available
    """

    def __init__(self, status):
        """
        """
        super(ElasticNodeNotAvailable, self).__init__(self, message)
        self.status = status


class Es_demo(object):
    """
    Provides methods for creation/deletion/modification of elasticsearch
    indices and for running queries

    For more details about elasticsearch bacic concepts refer to:
    elastic.co/guide/en/elasticsearch/reference/current/_basic_concepts.html
    """

    countries_url = "http://countryapi.gear.host/v1/Country/getCountries"

    def __init__(self, args):
        """
        Sets up  initial configuration

        :param args: argparse.Namespace object
        """
        # setup node
        self.es_node = ES([{"host": args.host, "port": args.port}])
        self.es_node_url = "http://%s:%d" % (args.host, args.port)

        # connect to node
        connected_to_node = self.check_node_connection(self.es_node_url)
        if not connected_to_node:
            sys.exit(1)

        # setup default configuration
        self.region = args.region
        self.region_url = self.countries_url + "?pRegion=%s" % args.region
        self.index_name = "countries_index"
        self.doc_type = '%s_countries' % self.region

    def check_node_connection(self, url):
        """
        Establishes/checks elasticsearch node connection
        """
        try:
            es_node_response = requests.get(url)
        except requests.exceptions.ConnectionError as con_error:
            log.debug("Elasticsearch node not running")
            log.error(con_error)
            return False
        except Exception as _error:
            log.error(_error)
            return False
        else:
            if es_node_response.status_code == 200:
                log.info("Connected to node")
                return True
            else:
                log.info("Failed to connect to node")
                try:
                    raise ElasticNodeNotAvailable(status)
                except ElasticNodeNotAvailable as error:
                    log.debug("Node returned status: %d" % error.status)
                    return False

    def create_region_index(self):
        """
        Creates elasticsearch countries index based on region, e.g.:

        http://countryapi.gear.host/v1/Country/getCountries?pRegion=Americas
        """

        api_response = requests.get(self.region_url)
        countries_dict = json.loads(api_response.content)
        countries_total_count = countries_dict["TotalCount"]
        log.info("Total number of countries: %d" % countries_total_count)

        # if status ok create index
        connected_to_node = self.check_node_connection(self.es_node_url)
        if not connected_to_node:
            sys.exit(1)

        for _id in xrange(countries_total_count):
            self.es_node.index(index=self.index_name,
                               doc_type=self.doc_type,
                               id=_id,
                               body=countries_dict['Response'][_id])

        log.info("Index for region %s created successfully" % self.region)
    
    def search_by_id(self, country_id):
        """
        Gets specific country by id
        """
        country = self.es_node.get(
            index=self.index_name, doc_type=self.doc_type, id=country_id)
        log.info(country)

    def search_by_name(self, name):
        """
        Searches by country name
        """
        result = self.es_node.search(
            index=self.index_name,
            body=
            {
                "query": {
                    "match": {
                        "Name": name
                    }
                }
            })
        log.info(result)

    def list_all_indices(self):
        """
        Lists all indices
        """
        for index in self.es_node.indices.get('*'):
            log.info(index)

    def delete_region_index(self):
        """
        Deletes elasticsearch countries index
        """
        self.es_node.indices.delete(index=self.index_name, ignore=[400, 404])

    def custom_query(self):
        """
        Practice various queries here
        """
        # this search would NOT match documents where "Area" is null
        result_1 = self.es_node.search(
            index=self.index_name,
            body=
            {
                "query": {
                    "exists": {
                        "field" : "Area"
                    }
                }
            })

        # this search find matches within range
        # note "boost" allows to boost the field i.e. matches on the
        # "Latitude" field will have twice the weight as matches on the
        # "Longitude" field, which has the default boost of 1.0
        # note how sort is used
        result_2 = self.es_node.search(
            index=self.index_name,
            body=
            {
                "query": {
                    "range": {
                        "Latitude": {
                            "gte": 10,
                            "lte": 50,
                            "boost": 2
                        }
                    }
                },
                
                "sort": {
                    "NumericCode": "asc"
                }
            })

        # this search will find results where "CurrencyCode" are either
        # GIP or UAH
        result_3 = self.es_node.search(
            index=self.index_name,
            body=
            {
                "query": {
                    "match" : {
                        "CurrencyCode" : "GIP UAH"
                    }
                }
            })

        # this search is similar to the above match query but searches on
        # multiple fields, so it will search for query data in any of the
        # fields, note ^3 will boost field score 3 times
        result_4 = self.es_node.search(
            index=self.index_name,
            body=
            {
                "query": {
                    "multi_match" : {
                        "query" : "Pound", # not case sensitive
                        "fields" : [ "CurrencyName^3", "CurrencyCode" ]
                    }
                }
            })

        # for item in result_4.get("hits").get("hits"):
        #     print item.get("_score"),
        #     print item.get("_source").get("Name"),
        #     print item.get("_source").get("CurrencyName"),
        #     print item.get("_source").get("CurrencyCode")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    # optional args with default values
    parser.add_argument("--host", help="ES IP address", default="localhost")
    parser.add_argument("--port", help="ES port number", default=8771)
    parser.add_argument("--region", help="ES index region param", default="Europe")
    args = parser.parse_args()

    es_demo = Es_demo(args)

    # create index
    es_demo.create_region_index()

    # get country by id
    # es_demo.search_by_id(5)

    # search by name
    # es_demo.search_by_name("Germany")

    # list all indices
    # es_demo.list_all_indices()

    # custom query
    es_demo.custom_query()

    # delete index
    # es_demo.delete_region_index()
