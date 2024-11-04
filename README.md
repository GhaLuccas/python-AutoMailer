# Work in progresses wip 

System Flow

Localização dos Arquivos:
O script vai buscar arquivos em duas pastas específicas. As pastas são baseadas no ano e mês atuais, que são determinados automaticamente.
Verificação:

Ele verifica se as pastas e os arquivos existem. Se tudo estiver lá, o processo continua.
Compactação:

Se os arquivos forem encontrados, eles serão compactados em arquivos .zip separados, um para cada tipo de documento.
Envio de E-mail:

O script envia os arquivos compactados por e-mail, com uma mensagem informativa que inclui o período dos documentos. O endereço de e-mail é pré-definido, mas o destinatário é especificado pelo usuário.

Tratamento de Erros:
Se algo der errado, um arquivo de log é criado para registrar a falha, e o usuário é notificado. O log é aberto no Notepad para facilitar a visualização.

Interface Simples:
O script tem uma interface gráfica que pede ao usuário o nome da empresa e o e-mail do escritório contábil. Essas informações são salvas para uso futuro, evitando ter que digitar novamente.

  
