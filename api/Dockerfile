FROM ubuntu:20.04
USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

# update and install first dependencies
RUN apt-get update
RUN apt-get install sudo
RUN apt-get install git libopenjp2-7-dev libcairo2-dev -y
# RUN sudo apt-get update
RUN sudo apt-get install build-essential make cmake wget libfreetype6-dev libfontconfig1-dev pkg-config libnss3-dev -y
RUN sudo sudo apt install build-essential libboost-system-dev libboost-thread-dev libboost-program-options-dev libboost-test-dev -y


#RUN mkdir libjpeg && cd libjpeg && git clone https://github.com/LuaDist/libjpeg.git
#RUN cd libjpeg ./configure
#RUN cd libjpeg /make 
#RUN cd libjpeg make install

RUN sudo apt-get install libjpeg62 -y
RUN wget https://poppler.freedesktop.org/poppler-data-0.4.11.tar.gz
RUN tar -xf poppler-data-0.4.11.tar.gz
RUN cd poppler-data-0.4.11 && make install
RUN wget https://poppler.freedesktop.org/poppler-22.03.0.tar.xz
RUN tar -xf poppler-22.03.0.tar.xz
RUN cd poppler-22.03.0 && mkdir build
RUN cd poppler-22.03.0/build && cmake .. -DENABLE_DCTDECODER=none
RUN cd poppler-22.03.0/build && make
RUN cd poppler-22.03.0/build && make install
RUN ldconfig
RUN rm poppler-data-0.4.11.tar.gz
RUN rm -rf poppler-data-0.4.11
RUN rm poppler-22.03.0.tar.xz
RUN rm -rf poppler-22.03.0


# install image dependencies
RUN apt-get update
RUN apt-get install -y libjpeg-dev zlib1g-dev

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# install python and requirements
RUN sudo apt update
RUN sudo apt install software-properties-common -y
RUN sudo add-apt-repository ppa:deadsnakes/ppa
RUN sudo apt update

RUN sudo apt install python3.9 python3-pip python3-bs4 -y
COPY ./requirements.txt requirements.txt
RUN python3.9 -m pip install --no-cache-dir --upgrade -r requirements.txt

RUN pdftotext -v
RUN python3.9 -m pip list
# run scripts
COPY . .
EXPOSE 80
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]