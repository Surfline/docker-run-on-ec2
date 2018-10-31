FROM continuumio/miniconda:4.5.4

SHELL ["/bin/bash", "-c"]
WORKDIR /opt/app

COPY environment.yml .
RUN conda env create --file environment.yml

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
