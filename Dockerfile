FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      make \
      python3 \
      texlive-latex-base \
      texlive-latex-extra \
      texlive-fonts-recommended \
      texlive-fonts-extra \
      texlive-xetex \
      latexmk \
      fonts-lato \
      fonts-roboto-slab \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
