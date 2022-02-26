FROM centos:7.7.1908

RUN yum -y install epel-release
RUN yum -y install initscripts passwd openssl openssh-server gcc make zip unzip bzip2 git wget screen gcc && yum clean all
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/miniconda3 && \
    rm ~/anaconda.sh && \
    echo "export PATH=/opt/miniconda3/bin:$PATH" >> ~/.bashrc
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ENV LANG C.UTF-8 LC_ALL=C.UTF-8

COPY requirements.txt requirements.txt
RUN /opt/miniconda3/bin/pip install -r requirements.txt -i https://pypi.doubanio.com/simple
COPY dao_quote/util/exchange_api/ctp/*.so /usr/lib/
