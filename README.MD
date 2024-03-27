# Flask-restx-flash-decorator
API com o objetivo de que sejam cadastradas palavras e suas traduções para que os usuários consigam aprender e
decorar conforme a repetição.


## Features
- Cadastro de palavras e suas traduções, tags e grupo de palavras
- Cadastro de usuários
- Registro de acertos e erros de tradução
- Endpoints para acompanhar resumo dos resultados, como total de acertas, erros,
palavras com mais erros, taxa de acerto nos últimos 90 dias anteriores, etc .

## Tecnologias
- API feita usando flask-restx
- Modelos e operações SQL usando flask_sqlalchemy como ORM
- Para versionamento de migrações o uso do flask_migrate
- Para schemas de validação o uso do flask_marshmallow
- Autenticação e renovação de chave JWT usando flask_jwt_extended
- Cache para endpoints de interesse usando flask_caching
- Limite de requests para endpoints específicos usando flask_limiter
- Para controle de CORS o uso do flask_cors


### Instalação
#### Clona repositório
```git clone https://github.com/AyrtonMoises/flask-restx-flash-decorator```

### Criação de ambiente virtual
```python -m venv venv```

### Ativar ambiente virtual
##### Linux
```source venv/bin/activate```

##### Windows
```venv/scripts/activate```

#### Instalação de pacotes
```pip install -r requirements.txt```

#### Defina as variaveis de ambiente
Criar arquivo .env baseado no arquivo de exemplo '.env.sample'

#### Aplica migrações
```flask db upgrade``` 

#### Cria roles para apps do aplicativo 
```python fixture_app_roles.py```

##### Criar usuário administrativo
```flask create-user-admin NAME EMAIL PASSWORD```

#### Executa modo desenvolvimento
``` flask run --debug```

#### Acesso da API
[http://localhost:5000/doc]

##### Configurações adicionais do flask-migrate
###### Cria configuração de migração inicial
```flask db init``` 
###### Cria migrações baseado nos modelos do projeto
```flask db migrate -m "Descrição da migração"``` 
###### Aplica migrações no banco de dados
```flask db upgrade``` 
