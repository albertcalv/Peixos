FROM continuumio/anaconda3:5.0.1

WORKDIR /usr/local/
COPY peixos-env.yml /tmp/peixos-env.yml
COPY ./peixos /usr/local/peixos

RUN conda env create -f /tmp/peixos-env.yml
RUN conda activate peixos-env
RUN install .
RUN install PyQt5

RUN python peixos/ui_validation.py




