FROM openjdk:11-jre-slim
RUN mkdir -p /src
WORKDIR /src 
COPY ./start/hermes-v0.7.5.jar ./hermes.jar
COPY ./start/api-key.txt ./api-key.txt
RUN java -jar hermes.jar --db snomed.db download uk.nhs/sct-clinical api-key api-key.txt cache-dir ./tmp/trud
RUN java -jar hermes.jar --db snomed.db download uk.nhs/sct-drug-ext api-key api-key.txt cache-dir ./tmp/trud
RUN java -Xmx8g -jar hermes.jar --db snomed.db compact
RUN java -jar hermes.jar --db snomed.db index /hermes
EXPOSE 8080
CMD [ "java", "-jar", "hermes.jar", "--db", "snomed.db", "--port", "8080", "serve"]