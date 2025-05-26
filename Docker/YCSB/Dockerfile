FROM maven:3.9.3-eclipse-temurin-17

COPY /YCSB/YCSB-compile /YCSB-compile
COPY /YCSB/YCSB-decompile /YCSB-decompile
COPY /YCSB/script.sh /script.sh

WORKDIR /YCSB-compile/lib

RUN javac -cp ./core-0.17.0.jar -d custom_classes ../../YCSB-decompile/core/src/main/java/site/ycsb/workloads/CustomWorkload.java && \
    jar uf ./core-0.17.0.jar -C custom_classes site/ycsb/workloads/CustomWorkload.class

RUN chmod +x /script.sh

CMD ["/bin/bash", "/script.sh"]