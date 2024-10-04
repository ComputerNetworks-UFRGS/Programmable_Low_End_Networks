# Compressão e remoção do cabeçalho Ethernet no P4Pi

Na pasta /compression-files coloquei os arquivos atualizados do BMV2 e do P4c, juntamente com um script (_cpfiles.sh_) para fazer as seguintes tarefas:

   1. Clonar o BMV2 e o P4C
   2. Mudar a versão do BMV2 e P4c
   3. Substituir os arquivos pelos arquivos atualizados

<br/>

## commits utilizados para configurar a compressão no P4Pi:
   
    BMV2: f745e1db5e281d1e30483496c3c0960a8d23c852 (version 1.15.0, Feb 10, 2022)
    P4C: 1576090b74b610e979a3afeafec79d0a2f81a598 (version 1.2.3.0, Aug 2, 2022)

<br/>

## setup necessário para configuração de compressão no P4Pi 
similar aos passos em p4-compression/readme.txt
   
### configuracoes iniciais
copiar a pasta _compression-files/_ para _/root_.

discussão sobre [erros do Perl](https://forums.raspberrypi.com/viewtopic.php?t=355095) com locales.

```bash
$ sudo -i
$ cp compression-files/cpfiles.sh .
$ chmod +x cpfiles.sh
$ raspi-config _necessario por conta de erros do Perl_ 
    - first "5 Localisation Options"
    - followed by "L1 Locale"
    - hit SPACE to put an asterisk next to the listing

# configuracao do BMV2
$ cd behavioral-model/ 
$ ./autogen.sh
$ ./configure --with-thrift --with-pi
$ vim targets/simple_switch/Makefile (adiciona -lz em LIBS, linha ~381)
$ make -j4
$ make install

$ cd targets/simple_switch_grpc/
$ ./autogen.sh
$ ./configure --with-thrift
$ make
$ make install

# configuracao do P4c
$ cd p4c/build (caso nao funcionar: mkdir p4c/build/ && cd p4c/build/)
$ cmake ..
$ make -j4
$ make install 

$ cd && mkdir bmv2/example/remove-and-compress/
# Copie o arquivos remove-and-compress.p4 (p4-compression/remove-and-compress/remove-and-compress.p4)
$ vim bmv2/examples/remove-and-compress
```

<br/>

## configuracao das regras estáticas nas tabelas

### Tabela *gzip* (iguais em ambos os hosts)

```c
table gzip {
    // ...
    const entries = {
        0: gzip_inflate();
        1: gzip_deflate();
    }
    // ...
}
```

<br/>

#### Tabela eth_forward

1. p4pi-end

```c
table eth_forward {
    // ...
    const entries = {
        0: eth_destroy(1); // to lorasend
        1: drop();
        2: eth_build(0x9a627874fe65, 0xea89b7c2bb35, 0); // to lorarecv
    }
    // ...
}
```

<br/>

2. p4pi-middle

```c
table eth_forward {
    // ...
    const entries = {
        0: eth_destroy(1); // to lorasend
        1: drop();
        2: eth_build(0xea89b7c2bb35, 0x9a627874fe65, 0); // to lorarecv
    }
    // ...
}
```

Após esses passos, reinicie o serviço do bmv2

```bash
systemctl restart bmv2.service

# para checar se a compilação e a interpretação funcionaram
systemctl status bmv2.service
```

Caso não funcionar, pode ser necessário rodar os seguintes comandos novamente

```bash
cd /root/behavioral-model
make install
cd targets/simple_switch_grps
make install
cd ../../../p4c/build
make install
```
    


