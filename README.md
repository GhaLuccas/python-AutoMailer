##Envio de Fechamento Fiscal
Este projeto tem como objetivo automatizar o envio de arquivos fiscais por e-mail, facilitando o processo de fechamento mensal 
para empresas e seus escritórios contábeis. A aplicação compacta os arquivos necessários e os envia para o e-mail especificado, 
além de notificar se não houver arquivos disponíveis.

Funcionalidades
- Carregamento de Configurações: Carrega o nome da empresa e o e-mail do escritório contábil a partir de um arquivo de configuração, 
evitando a necessidade de inserção manual a cada uso.
- Compactação de Arquivos: Compacta pastas de NFe e SAT em arquivos ZIP para envio.
- Envio de E-mails: Envia os arquivos compactados por e-mail, utilizando SMTP com autenticação.
- Notificações: Notifica o usuário sobre o sucesso do envio ou a ausência de arquivos, através de mensagens de alerta na interface gráfica.
- Interface Gráfica Simples: Desenvolvida com Tkinter, a interface permite fácil interação para inserção dos dados necessários.

Instalação:
Somente de deplay na pasta dist da versão desejada

Configuração:
Altere o arquivo config.txt para adicionar o nome da empresa e o e-mail do escritório contábil, caso deseje.

Execução:
Execute o script principal. A interface gráfica será aberta.
Preencha os campos solicitados e clique em "Enviar" para iniciar o processo de envio.

Observações
A aplicação lida com erros, criando um arquivo de log caso ocorra alguma falha durante a execução.
É necessário ter acesso às pastas de NFe e SAT para que a compactação e envio sejam realizados corretamente.

