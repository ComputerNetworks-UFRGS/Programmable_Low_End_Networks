# Programmable Layer

1.  coloquei somente os arquivos que alterei dentro das pastas.

2.  em cada arquivo há um comentário "CHANGED" onde foram feitas alterações.

3.  commits utilizados (script do tutorial no p4lang):

    ```
    p4c: 69e132d0d663e3408d740aaf8ed534ecefc88810
    bmv2: b447ac4c0cfd83e5e72a3cc6120251c1e91128ab
    Commit p4lang/tutorials com VM corrigida para Ubuntu 16:
    d964079ef8381316d32a19307509dd4a97edd070
    ```

4.  setup extra necessário por causa dos arquivos alterados:

    ```bash
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
    ```

5.  necessário recompilar se alterar o "primitives.cpp":

    ```shell
    $ cd behavioral-model/
    $ make
    $ sudo make install

    $ cd targets/simple_switch_grpc/
    $ make
    $ sudo make install
    ```

6.  OBSERVAÇÕES
    Recomendo copiar os trechos de código marcados com "// CHANGED" e apenas adicionar esses trechos nos arquivos existentes na instalação desejada. Isso pois, caso a versão do bmv2 ou do p4c seja diferente daquela na qual os testes iniciais foram realizados, nenhuma parte do código é "reescrita" com a substituição dos arquivos.

    Rodei os testes de compressão no Ubuntu 20 com versões mais novas do BMV2 e do P4C e a compressão funcionou como esperado.
