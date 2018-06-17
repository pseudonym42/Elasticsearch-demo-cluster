# here we build custom docker image for elasticsearch

# this is official elasticsearch image
FROM docker.elastic.co/elasticsearch/elasticsearch:5.5.0

# add custom setups
ADD elasticsearch.yml /usr/share/elasticsearch/config/

USER root
RUN chown elasticsearch:elasticsearch config/elasticsearch.yml
USER elasticsearch

# remove x-pack plugin to get rid of authentication, which is required
# when accessing elasticsearch node
RUN rm -rf plugins/x-pack
EXPOSE 8771
