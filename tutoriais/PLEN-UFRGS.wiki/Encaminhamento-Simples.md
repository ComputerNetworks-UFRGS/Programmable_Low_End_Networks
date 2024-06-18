Neste exercício vamos:

1. **Configurar a rede (virtual e física) detalhada abaixo:**

    | Diagrama simples da rede | Diagrama completo da rede (incluindo bridges e interfaces) |
    | ----- | ----- |
    | ![simple_forwrard drawio (4)](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/02329d86-ee38-4e95-8708-e06611eb2fab) | ![simple_forward_complete drawio (2)](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/7888299a-1aa1-4786-bf24-6453ff54b9cb) |

    _As duas imagens acima representam a mesma rede, no entanto, a segunda exibe mais informações acerca de como essa rede está conectada virtualmente dentro do P4Pi. Recomendo dar uma breve estudada no conceito de [`bridges`](https://pt.wikipedia.org/wiki/Bridge_(redes_de_computadores)) para entender melhor como a troca de informações ocorre._

2. **Programar o switch para encaminhar os pacotes com regras estáticas**
    

3. **Testar a comunicação**
<br/>

Presume-se que você já possui um Raspberry Pi com o sistema P4Pi instalado e rodando. Caso contrário, recomendo seguir os [passos descritos na documentação do P4Pi](https://github.com/p4lang/p4pi/wiki/Installing-P4Pi) para baixar e instalar o sistema no cartão SD.

Abaixo, segue uma breve descrição das:
   1. [Regras estáticas](#inser%C3%A7%C3%A3o-das-regras-est%C3%A1ticas-no-p4)
   2. [Criação e configuração dos briges](#cria%C3%A7%C3%A3o-e-configura%C3%A7%C3%A3o-dos-bridges)

Após a introdução, segue o [passo a passo](#passo-a-passo-para-a-realiza%C3%A7%C3%A3o-do-encaminhamento-simples-de-pacotes) do exercício.

<br/>

## Rede virtual e switch

### Inserção das regras estáticas no P4

Inserir regras estáticas diretamente no código P4 permite descartar, nesse exemplo, a necessidade do plano de controle. Deixei, abaixo, um recorte do código usado nesse exercício, no qual incluímos as regras da tabela `dmac` de forma estática, diretamente no código P4. 

_Para esse exercício, será necessário editar essas regras estáticas e substituir as `keys` pelos endereços MAC dos dispositivos utilizados no exemplo._

```p4
table dmac {
    actions = {
        forward;
        forward_one;
        drop;
    }
        
    key = {
        hdr.ethernet.dstAddr: exact;
    }

    // ------------------------------------
    // INSERCAO DE REGRAS ESTATICAS
    // ------------------------------------
    // TODO: CORRIGIR ENDERECOS MAC

    const entries = {
        // key (mac address): action
        0x1cccd67636c0 : forward(0);     // celular
	0x047c16bfb9a1 : forward(1);     // computador
    }

    // ------------------------------------
    default_action = forward_one();
    size = 512;
}
```

O código P4 completo pode ser visualizado [clicando aqui](https://github.com/marcelobasso/PLEN-UFRGS/blob/main/tutoriais/encaminhamento-simples/encaminhamento-simples.p4).

### Criação e configuração dos `bridges`

Para montarmos a rede virtual descrita pela segunda imagem acima, será necessário rodar um [_script_ que cria e configura as bridges](https://github.com/marcelobasso/PLEN-UFRGS/blob/main/tutoriais/encaminhamento-simples/configure-bridges.sh) da rede, as interfaces do P4Pi e os endereços IP. Deixei o _script_ pronto no diretório do tutorial. Recomendo dar uma breve lida e tentar compreender um pouco do que está acontecendo, no entanto, os detalhes mais técnicos não são tão importantes para compreender o exercício. 

<br/>

## Passo a passo para a realização do encaminhamento simples de pacotes

### No computador

1. Clonar repositório:

Abra um terminal e clone o repositório do projeto.

```console
git clone https://github.com/marcelobasso/PLEN-UFRGS.git
```

2. Conectar no Wi-Fi e realizar conexão SSH com o P4Pi:

Conecte-se no hotspot Wi-Fi chamado `p4pi` (senha `raspberry`). Pelo terminal, estabeleça uma conexão SSH (mesma senha do Wi-Fi).

```console
ssh pi@192.168.4.1
```

3. Editar P4 e corrigir endereços MAC

Abra o arquivo /tutoriais/encaminhamento-simples.p4 e procure pela linha `// TODO: CORRIGIR ENDERECOS MAC`. Edite as regras estáticas da tabela, substituindo os MACs pelos endereços corretos. Lembre-se de salvar o arquivo.

Para saber qual seu endereço MAC, execute o comando `ifconfig`. O endereço MAC aparecerá como no exemplo abaixo:
![image](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/f7fcbb15-9c9d-4a18-804b-db862181d9ba)

ATENCAO: O MAC utilizado deve ser o da interface Ethernet (cabo de rede) do seu computador, ela pode ter diferentes nomes, como eth0, eth1, etc.

Para ver o endereço MAC do celular, basta entrar nas configurações do WI-FI e descer até encontrar o endereço (talvez esteja em uma aba como "configurações adicionais" ou similar).

![Endereço MAC celular](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/7960c4b0-1d43-4152-8ccd-499324e35fc6)

No exemplo acima, o endereço IP está errado, pois eu estava conectado em outra rede quando fiz a captura de tela.

<br/>

### No P4Pi (terminal conectado por SSH)

1. Copiar arquivos para P4Pi:

```console
# entra no bash como root
sudo -i
# diretorio de codigos p4
cd /bmv2/examples
# ATENCAO: o nome da pasta deve ser exatamento igual ao nome do codigo p4 que sera salvo dentro dela
mkdir encaminhamento-simples && cd encaminhamento-simples
# ATENCAO: mudar usuario e IP pelo seu usuario e pelo IP recebido
scp marcelo@192.168.4.6:~/PLEN-UFRGS/tutoriais/encaminhamento-simples/* .
```

2. Rodar código P4 no switch virtual

```console
echo encaminhamento-simples > ~/t4p4s-switch
systemctl restart bmv2.service
```

3. Verificar se o BMV2 (switch virtual) esta rodando corretamente:

```console
systemctl status bmv2.service
```
![print-bmv2-status](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/8448814e-38e6-4900-ad32-c36f2fbbc93a)
Se o cabeçalho do output for similar ao da imagem acima, então o código foi compilado e está rodando no switch virtual com sucesso.
Para sair do comando, digite `q`.

4. Dar permissão de execução (`x`) para o _script_ e rodar

```console
chmod +x configure-bridges.sh
./configure-bridges.sh
```

5. Configurar IP no smartphone

No smartphone, você terá que procurar as configurações da rede Wi-Fi, mudar opção "Configuração de IP" (ou similar) para `Estático`, e colocar o endereço IP `192.168.155.23`. As outras informações não precisam ser mudadas, mesmo que difiram da imagem abaixo.

![IP estático](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/ef6ca355-972e-49f8-8be8-2b9f318f1495)

<br/>

### No computador

1. Configurar IP no computador

```console
# sudo ip addr add 192.168.15.25/20 dev <interface ethernet>
sudo ip addr add 192.168.15.25/20 dev enp4s0
```

2. Conectar computador ao switch
    Conecte seu computador ao P4Pi (Raspberry Pi) com um cabo Ethernet.

3. Adicionar registro na tabela ARP no computador

Seu computador só consegue se comunicar com dispositivos que ele conhece (cujo endereço ele possui em sua [tabela ARP](https://www.fortinet.com/br/resources/cyberglossary/what-is-arp), por isso, é necessário adicionar um registro na tabela para que os dispositivos possam se comunicar, caso contrário, o output do ping será `Destination Host Unreachable`)

```console
# sudo arp -i <interface ethernet> -s 192.168.15.23 <MAC do smartphone>
sudo arp -i enp4s0 -s 192.168.15.23 1c:cc:d6:76:36:c0
```

4. Pingar celular

O ping é um programa que manda pacotes ICMP "Internet Control Message Protocol" para uma interface e aguarda sua resposta. É basicamente uma forma de dizer "Alô?" e aguardar outro "Alô" como resposta. Caso a resposta seja recebida, o ping exibirá na tela algumas informações sobre a troca de dados, algo como: `64 bytes from 182.171.12.1: icmp_seq=2 ttl=231 time=366 ms`.

```console
# ping 192.168.15.23 -I <interface ethernet>
ping 192.168.15.23 -I enp4s0
```

Caso o output do comando ping seja similar ao exemplo dado acima, isso significa que os dispositivos estão se comunicando, e o encaminhamento simples de pacotes pelo switch programável <u>foi feito corretamente</u>.

<br/>

## Passo opcional

Sniff (ouvir os pacotes que passam) interface de rede (conexão Ethernet) para ver pacotes indo e voltando.

```console
# sudo tcpdump -i <interface ethernet> icmp
sudo tcpdump -i enp4s0 icmp
```

Abra um novo terminal (no seu computador) e execute o comando acima para observar os pacotes indo e voltando. Lembre-se de *trocar o nome da interface* pelo nome da sua interface de rede. 

