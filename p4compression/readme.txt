01. coloquei somente os arquivos que alterei dentro das pastas.

02. em cada arquivo há um comentário "CHANGED" onde foram feitas alterações.

03. commits utilizados (script do tutorial no p4lang):

    p4c:  69e132d0d663e3408d740aaf8ed534ecefc88810
    bmv2: b447ac4c0cfd83e5e72a3cc6120251c1e91128ab

    Commit do tutorial do P4 com a VM corrigida para Ubuntu16:
    d964079ef8381316d32a19307509dd4a97edd070
    
04. setup extra necessário por causa dos arquivos alterados:

    $ cd p4c/build/
    $ make
    $ sudo make install

    $ cd behavioral-model/
    $ ./autogen.sh
    $ ./configure --with-pi --with-thrift
    $ nano targets/simple_switch/Makefile (adiciona -lz em LIBS, provavelmente na linha 381)
    $ make
    $ sudo make install

    $ cd targets/simple_switch_grpc/
    $ ./autogen.sh
    $ ./configure --with-thrift
    $ make
    $ sudo make install

05. necessário recompilar se alterar o "primitives.cpp":

    $ cd behavioral-model/
    $ make
    $ sudo make install

    $ cd targets/simple_switch_grpc/
    $ make
    $ sudo make install

