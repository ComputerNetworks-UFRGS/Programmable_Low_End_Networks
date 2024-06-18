# Welcome to the PLEN-UFRGS wiki!
Eu reuni, nessa Wiki, algumas dicas e exercícios para entender um pouco mais sobre o funcionamento do sistema P4Pi, incluindo a configuração básica do protótipo do projeto, via rede cabeada.
<br/>

# Instalação do P4Pi
Recomendo seguir a [documentação oficial](https://github.com/p4lang/p4pi/wiki/Installing-P4Pi) do P4Pi para realizar a instalação do sistema no cartão SD.

# Configuração Inicial da rede virtual
![basic-setup drawio (3)](https://github.com/marcelobasso/PLEN-UFRGS/assets/103913045/4c314ccc-1e91-4e13-bf1c-7247e511056c)

Ao iniciar o sistema P4Pi, essa é a configuração inicial da rede virtual. O switch se comunica na porta 0 com a bridge br0, e a bridge faz a comunicação entre o switch e o hotspot wifi, por onde é possível estabelecer uma conexão com o rasp e realizar comunicação ssh.
