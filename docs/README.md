# FastAPI Workshop

Criando uma aplicação web com API usando FastAPI

## Requisitos

- Computador com Python 3.10
- Docker & docker-compose
- Ou gitpod.io para um ambiente online
- Um editor de códigos como VSCode, Sublime, Vim, Micro
  (Nota: Eu usarei o Micro-Editor)

> **importante**: Os comandos apresentados serão executados em um terminal Linux, se estiver no Windows recomendo usar o WSL, uma máquina virtual ou um container Linux, ou por conta própria adaptar os comandos necessários.

## Ambiente

Primeiro precisamos de um ambiente virtual para instalar
as dependencias do projeto.

```
python -m venv .venv
```

E ativaremos a virtualenv

```
# Linux
source .venv/bin/activate
# Windows Power Shell
.\venv\Scripts\activate.ps1
```

Vamos instalar ferramentas de produtividade neste ambiente e para isso vamos criar um arquivo chamado
requirements-dev.txt


```
ipython   # terminal
ipdb      # debugger
sdb       # debugger remoto
pip-tools # lock de dependencias
pytest    # execução de testes
black     # auto formatação
flake8    # linter
```

Instalamos as dependencias iniciais.

```
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## O Projeto

Nosso projeto será um microblog estilo twitter, é
um projeto simples porém com funcionalidade suficientes
para exercitar as principais features de uma API.

Vamos focar no backend, ou seja, na API apenas,
o nome do projeto é "PAMPS" um nome aleatório que
encontrei para uma rede social ficticia.

## Funcionalidades

### Usuários

- Registro de novos usuários
- Autenticação de usuários
- Seguir outros usuários
- Perfil com bio e listagem de posts, seguidores e seguidos

### Postagens

- Criação de novo post
- Edição de post
- Remoção de post
- Listagem de posts geral (home)
- Listagem de posts seguidos (timeline)
- Likes em postagens
- Postagem pode ser resposta a outra postagem


## Estrutura de pastas e arquivos

Script para criar os arquivos do projeto.

```bash
# Arquivos na raiz
touch setup.py
touch {settings,.secrets}.toml
touch {requirements,MANIFEST}.in
touch Dockerfile.dev docker-compose.yaml

# Imagem do banco de dados
mkdir postgres
touch postgres/{Dockerfile,create-databases.sh}

# Aplicação
mkdir -p pamps/{models,routes}
touch pamps/default.toml
touch pamps/{__init__,cli,app,auth,db,security,config}.py
touch pamps/models/{__init__,post,user}.py
touch pamps/routes/{__init__,auth,post,user,home}.py

# Testes
mkdir tests
touch tests/{__init__,conftest,test_api}.py
```

Esta será a estrutura final (se preferir criar manualmente)

```
❯ tree --filesfirst -L 3 -I docs
.
├── docker-compose.yaml        # Orquestração de containers
├── Dockerfile.dev             # Imagem principal
├── MANIFEST.in                # Arquivos incluidos na aplicação
├── requirements-dev.txt       # Dependencias de ambiente dev
├── requirements.in            # Dependencias de produção
├── .secrets.toml              # Senhas locais
├── settings.toml              # Configurações locais
├── setup.py                   # Instalação do projeto
├── pamps
│   ├── app.py                 # FastAPI app
│   ├── auth.py                # Autenticação
│   ├── cli.py                 # Aplicação CLI `$ pamps adduser` etc
│   ├── config.py              # Inicialização da config
│   ├── db.py                  # Conexão com o banco de dados
│   ├── default.toml           # Config default
│   ├── __init__.py
│   ├── security.py            # Autenticação
│   ├── models
│   │   ├── __init__.py
│   │   ├── post.py            # ORM e Serializers de posts
│   │   └── user.py            # ORM e Serialziers de users
│   └── routes
│       ├── home.py            # Rota principal da timeline
│       ├── auth.py            # Rotas de autenticação via JWT
│       ├── __init__.py
│       ├── post.py            # CRUD de posts e likes
│       └── user.py            # CRUD de user e follows
├── postgres
│   ├── create-databases.sh    # Script de criação do DB
│   └── Dockerfile             # Imagem do SGBD
└── tests
    ├── conftest.py            # Config do Pytest
    ├── __init__.py
    └── test_api.py            # Tests da API
```

## Adicionando as dependencias

Editaremos o arquivo `requirements.in` e adicionaremos

```
fastapi
uvicorn
sqlmodel
typer
dynaconf
jinja2
python-jose[cryptography]
passlib[bcrypt]
python-multipart
psycopg2-binary
alembic
rich
```

A partir deste arquivo vamos gerar um `requirements.txt` com os locks das
versões.

```bash
pip-compile requirements.in
```

E este comando irá gerar o arquivo `requirements.txt` organizado e com as versões
pinadas.

## Criando a API base

Vamos editar o arquico `pamps/app.py`

```python
from fastapi import FastAPI

app = FastAPI(
    title="Pamps",
    version="0.1.0",
    description="Pamps is a posting app",
)

```

## Tornando a aplicação instalável

`MANIFEST.in`
```
graft pamps
```

`setup.py`
```python
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="pamps",
    version="0.1.0",
    description="Pamps is a social posting app",
    url="pamps.io",
    python_requires=">=3.8",
    long_description="Pamps is a social posting app",
    long_description_content_type="text/markdown",
    author="Melon Husky",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["pamps = pamps.cli:main"]
    }
)
```

## Instalação

O nosso objetivo é instalar a aplicação dentro do container, porém
é recomendável que instale também no ambiente local pois
desta maneira auto complete do editor irá funcionar.

```bash
pip install -e .
```

## Containers

Vamos agora escrever o Dockerfile.dev responsável por executar nossa api

`Dockerfile.dev`

```docker
# Build the app image
FROM python:3.10

# Create directory for the app user
RUN mkdir -p /home/app

# Create the app user
RUN groupadd app && useradd -g app app

# Create the home directory
ENV APP_HOME=/home/app/api
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# install
COPY . $APP_HOME
RUN pip install -r requirements-dev.txt
RUN pip install -e .

RUN chown -R app:app $APP_HOME
USER app

CMD ["uvicorn","pamps.app:app","--host=0.0.0.0","--port=8000","--reload"]

```

Build the container

```bash
docker build -f Dockerfile.dev -t pamps:latest .
```

Execute o container para testar

```console
$ docker run --rm -it -v $(pwd):/home/app/api -p 8000:8000 pamps
INFO:     Will watch for changes in these directories: ['/home/app/api']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using StatReload
INFO:     Started server process [8]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Acesse: http://0.0.0.0:8000/docs

![API](api_first.png)

A API vai ser atualizada automaticamente quando detectar mudanças no código,
somente para teste edite `pamps/app.py` e adicione

```python
@app.get("/")
async def index():
    return {"hello": "world"}
```

Agora acesse novamente http://0.0.0.0:8000/docs

![API](api_first.png)


## Rodando um banco de dados em container

Agora precisaremos de um banco de dados e vamos usar o PostgreSQL dentro de
um container.

Edite `postgres/create-databases.sh`
```bash
#!/bin/bash

set -e
set -u

function create_user_and_database() {
	local database=$1
	echo "Creating user and database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $database PASSWORD '$database';
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

if [ -n "$POSTGRES_DBS" ]; then
	echo "Creating DB(s): $POSTGRES_DBS"
	for db in $(echo $POSTGRES_DBS | tr ',' ' '); do
		create_user_and_database $db
	done
	echo "Multiple databases created"
fi
```

O script acima vai ser executado no inicio da execução do Postgres de forma
que quando a aplicação iniciar teremos certeza de que o banco de dados está criado.

Agora precisamos do Sistema de BD rodando e vamos criar uma imagem com Postgres.

Edite `postres/Dockerfile`
```docker
FROM postgres:alpine3.14
COPY create-databases.sh /docker-entrypoint-initdb.d/
```

## Docker compose

Agora para iniciar a nossa API + o Banco de dados vamos precisar de um
orquestrador de containers, em produção isso será feito com Kubernetes
mas no ambiente de desenvolvimento podemos usar o docker-compose.

Edite o arquivo `docker-compose.yaml`

- Definimos 2 serviços `api` e `db`
- Informamos os parametros de build com os dockerfiles
- Na `api` abrimos a porta `8000`
- Na `api` passamos 2 variáveis de ambiente `PAMPS_DB__uri` e `PAMPS_DB_connect_args` para usarmos na conexão com o DB
- Marcamos que a `api` depende do `db` para iniciar.
- No `db` informamos o setup básico do postgres e pedimos para criar 2 bancos de dados, um para a app e um para testes.

```yaml
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - PAMPS_DB__uri=postgresql://postgres:postgres@db:5432/pamps
      - PAMPS_DB__connect_args={}
    volumes:
      - .:/home/app/api
    depends_on:
      - db
    stdin_open: true
    tty: true
  db:
    build: postgres
    image: pamps_postgres-13-alpine-multi-user
    volumes:
      - $HOME/.postgres/pamps_db/data/postgresql:/var/lib/postgresql/data
    ports:
      - "5435:5432"
    environment:
      - POSTGRES_DBS=pamps, pamps_test
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
```

O próximo passo é executar com

```bash
docker-compose up
```

## Definindo os models com Pydantic

![database](database.png)

https://dbdesigner.page.link/qQHdqeYRTqKUfmrt7

Vamos modelar o banco de dados definido acima usando o SQLModel, que é
uma biblioteca que integra o SQLAlchemy e o Pydantic e funciona muito bem
com o FastAPI.

Vamos começar a estruturar os model principal para armazenar os usuários

edite o arquivo `pamps/models/user.py`
```python
"""User related data models"""
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Represents the User Model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: str = Field(nullable=False)
```

No arquivo `pamps/models/__init__.py` adicione

```python
from sqlmodel import SQLModel
from .user import User

__all__ = ["User", "SQLModel"]
```

## Settings

Agora que temos pelo menos uma tabela mapeada para uma classe precisamos
estabelecer conexão com o banco de dados e para isso precisamos carregar
configurações

Edite o arquivo `pamps/default.toml`
```toml
[default]

[default.db]
uri = ""
connect_args = {check_same_thread=false}
echo = false
```

Lembra que no `docker-compose.yaml` passamos as variáveis `PAMPS_DB...`
aquelas variáveis vão sobrescrever os valores definidos no default
settings.

Vamos agora inicializar a biblioteca de configurações:

Edite `pamps/config.py`
```python
"""Settings module"""
import os

from dynaconf import Dynaconf

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="pamps",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="pamps_env",
    load_dotenv=False,
)
```

No arquivo acima estamos definindo que o objeto `settings` irá
carregar variáveis do arquivo `default.toml` e em seguida dos arquivos
`settings.toml` e `.secrets.toml` e que será possivel usar `PAMPS_` como
prefixo nas variáveis de ambiente para sobrescrever os valores.


## Conexão com o banco de dados

Edite `pamps/db.py`

```python
"""Database connection"""
from sqlmodel import create_engine
from .config import settings

engine = create_engine(
    settings.db.uri,
    echo=settings.db.echo,
    connect_args=settings.db.connect_args,
)
```

Criamos um objeto `engine` que aponta para uma conexão com o banco de
dados e para isso usamos as variáveis que lemos do `settings`.

## Database Migrations

Portanto agora já temos uma tabela mapeada e um conexão com o banco de dados
precisamos agora garantir que a estrutura da tabela existe dentro do banco
de dados.

Para isso vamos usar a bilbioteca `alembic` que gerencia migrações, ou seja,
alterações na estrutura das tabelas.

Começamos indo na raiz do repositório e rodando:

```bash
alembic init migrations
```

O alembic irá criar um arquivo chamado `alembic.ini` e uma pasta chamada `migrations` que servirá para armazenar o histórico de alterações do banco de dados.

Começaremos editando o arquivo `migrations/env.py`

```py
# No topo do arquivo adicionamos
from pamps import models
from pamps.db import engine
from pamps.config import settings


# Perto da linha 23 mudamos de
# target_metadata = None
# para
target_metadata = models.SQLModel.metadata

# Na função `run_migrations_offline()` mudamos
#  url = config.get_main_option("sqlalchemy.url")
# para
url = settings.db.uri

# Na função `run_migration_online` mudamos
# connectable = engine_from_config...
#para
connectable = engine
```

Agora precisamos fazer só mais um ajuste
edite `migrations/script.py.mako` e em torno da linha 10
adicione

```mako
#from alembic import op
#import sqlalchemy as sa
import sqlmodel  # linha NOVA
```

Agora sim podemos começar a usar o **alembic** para gerenciar as
migrations, precisamos executar este comando dentro do container
portando execute

```console
$ docker-compose exec api /bin/bash
```

> NOTA: todos os comandos serão executados no shell dentro do container!!!

E dentro do prompt do container rode:

```console
$ alembic revision --autogenerate -m "initial"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
  Generating /home/app/api/migrations/versions/ee59b23815d3_initial.py ...  done
```

Repare que o alembic identificou o nosso model `User` e gerou uma migration
inicial que fará a criação desta tabela no banco de dados.

Podemos aplicar a migration rodando dentro do container:

```console
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ee59b23815d3, initial
```

E neste momento a tabela será criada no Postgres, podemos verificar se
está funcionando ainda dentro do container:

```console
$ ipython
>>>
```

Digite

```python
from sqlmodel import Session, select
from pamps.db import engine
from pamps.models import User

with Session(engine) as session:
    print(list(session.exec(select(User))))
```

O resultado será uma lista vazia `[]` indicando que ainda não temos nenhum
usuário no banco de dados.

Foi preciso muito **boilerplate** para conseguir se conectar ao banco de dados
para facilitar a nossa vida vamos adicionar uma aplicação `cli` onde vamos poder
executar tarefas administrativas no shell.

## Criando a CLI base

Edite `pamps/cli.py`

```python
import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from .config import settings
from .db import engine
from .models import User

main = typer.Typer(name="Pamps CLI")


@main.command()
def shell():
    """Opens interactive shell"""
    _vars = {
        "settings": settings,
        "engine": engine,
        "select": select,
        "session": Session(engine),
        "User": User,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(
            argv=["--ipython-dir=/tmp", "--no-banner"], user_ns=_vars
        )
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@main.command()
def user_list():
    """Lists all users"""
    table = Table(title="Pamps users")
    fields = ["username", "email"]
    for header in fields:
        table.add_column(header, style="magenta")

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(user.username, user.email)

    Console().print(table)
```

E agora no shell do container podemos executar

```console
$ pamps --help

 Usage: pamps [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the      │
│                                                              specified shell.                │
│                                                              [default: None]                 │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the         │
│                                                              specified shell, to copy it or  │
│                                                              customize the installation.     │
│                                                              [default: None]                 │
│ --help                                                       Show this message and exit.     │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────╮
│ shell                        Opens interactive shell                                         │
│ user-list                    Lists all users                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

E cada um dos comandos:

```console
$ pamps user-list
    Pamps users
┏━━━━━━━━━━┳━━━━━━━┓
┃ username ┃ email ┃
┡━━━━━━━━━━╇━━━━━━━┩
└──────────┴───────┘

```

e

```console
$ pamps shell
Auto imports: ['settings', 'engine', 'select', 'session', 'User']

In [1]: session.exec(select(User))
Out[1]: <sqlalchemy.engine.result.ScalarResult at 0x7fb1aa275ea0>

In [2]: settings.db
Out[2]: <Box: {'uri': 'postgresql://postgres:postgres@db:5432/pamps', 'connect_args': {}, 'echo': False}>
```

Ainda não temos usuários cadastrados pois ainda está faltando uma parte importante
**criptografar as senhas** para os usuários.

## Hash passwords


Precisamos ser capazes de encryptar as senhas dos usuários e para isso tem alguns
requisitos, primeiro precisamos de uma chave em nosso arquivo de settings:

Edite `pamps/default.toml` e adicione ao final

```toml
[default.security]
# Set secret key in .secrets.toml
# SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 600
```

Como o próprio comentário acima indica, vamos colocar uma secret key no
arquivo `.secrets.toml` na raiz do repositório.

```toml
[development]
dynaconf_merge = true

[development.security]
# openssl rand -hex 32
SECRET_KEY = "ONLYFORDEVELOPMENT"
```

> NOTA: repare que estamos agora usando a seção `environment` e isso tem a ver
> com o modo como o dynaconf gerencia os settings, esses valores serão
> carregados apenas durante a execução em desenvolvimento.

Você pode gerar uma secret key mais segura se quiser usando
```console
$ python -c "print(__import__('secrets').token_hex(16))"
cc3541946aa624be51ab2f518b47e29c
```

Agora vamos editar `pamps/security.py` e adicionar alguns elementos

```python
"""Security utilities"""
from passlib.context import CryptContext

from pamps.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm


def verify_password(plain_password, hashed_password) -> bool:
    """Verifies a hash against a password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Generates a hash from plain text"""
    return pwd_context.hash(password)


class HashedPassword(str):
    """Takes a plain text password and hashes it.
    use this as a field in your SQLModel
    class User(SQLModel, table=True):
        username: str
        password: HashedPassword
    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Accepts a plain text password and returns a hashed password."""
        if not isinstance(v, str):
            raise TypeError("string required")

        hashed_password = get_password_hash(v)
        # you could also return a string here which would mean model.password
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return cls(hashed_password)
```

E agora editaremos o arquivo `pamps/models/user.py`

No topo
```python
from pamps.security import HashedPassword
```

E no model mudamos o campo `password` para

```python
password: HashedPassword
```

## Adicionando usuários pelo cli

Agora sim podemos criar usuários via CLI, edite `pamps/cli.py`

No final adicione
```python
@main.command()
def create_user(email: str, username: str, password: str):
    """Create user"""
    with Session(engine) as session:
        user = User(email=email, username=username, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {username} user")
        return user

```

E no terminal do container execute

```console
$ pamps create-user --help

 Usage: pamps create-user [OPTIONS] EMAIL USERNAME PASSWORD

 Create user

╭─ Arguments ────────────────────────────────────────────────────╮
│ *    email         TEXT  [default: None] [required]            │
│ *    username      TEXT  [default: None] [required]            │
│ *    password      TEXT  [default: None] [required]            │
╰────────────────────────────────────────────────────────────────╯
```

E então

```console
$ pamps create-user admin@admin.com admin 1234
created admin user

$ pamps user-list
         Pamps users
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ username ┃ email           ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ admin    │ admin@admin.com │
└──────────┴─────────────────┘
```

Agora vamos para a API

## Adicionando rotas de usuários


Agora vamos criar endpoints na API para efetuar as operações que fizemos
através da CLI, teremos as seguintes rotas:

- `GET /user/` - Lista todos os usuários
- `GET /user/username/` - Detalhe de um usuário
- `POST /user/` - Cadastro de novo usuário

> **TODO:** A exclusão de usuários por enquanto não será permitida
> mas no futuro você pode implementar um comando no CLI para fazer isso
> e também um endpoint privado para um admin fazer isso.

### Serializers

A primeira coisa que precisamos é definir serializers, que são models
intermediários usados para serializar e de-serializar dados de entrada e saída
da API e eles são necessários pois não queremos export o model do
banco de dados diretamente na API.

Em `pamps/models/user.py`

No topo
```python
from pydantic import BaseModel
```

No final
```python
class UserResponse(BaseModel):
    """Serializer for User Response"""
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserRequest(BaseModel):
    """Serializer for User request payload"""
    email: str
    username: str
    password: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
```


E agora criaremos as URLS para expor esses serializers com os usuários
edite `pamps/routes/user.py`

```python
from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from pamps.db import ActiveSession
from pamps.models.user import User, UserRequest, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users."""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

```

Agora repare que estamos importando `ActiveSession` mas este objeto não existe
em `pamps/db.py` então vamos criar


No topo de `pamps/db.py`
```python
from fastapi import Depends
from sqlmodel import Session, create_engine
```

No final de `pamps/db.py`
```python
def get_session():
    with Session(engine) as session:
        yield session


ActiveSession = Depends(get_session)
```

Agora podemos mapear as rotas na aplicação principal primeiro criarmos um
router principal que serve para agregar todas as rotas:

em `pamps/router/__init__.py`

```python
from fastapi import APIRouter

from .user import router as user_router

main_router = APIRouter()

main_router.include_router(user_router, prefix="/user", tags=["user"])
```

E agora em `pamps/app.py`

NO topo
```python
from .routes import main_router
```

Logo depois de `app = FastAPI(...`
```python
app.include_router(main_router)
```

E agora sim pode acessar a API e verá as novas rotas prontas para serem usadas.

![user routes](user_routes1.png)


Pode tentar pela web interface ou via curl

Criar um usuário

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/user/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "rochacbruno@gmail.com",
  "username": "rochacbruno",
  "password": "lalala",
  "avatar": "https://github.com/rochacbruno.png",
  "bio": "Programador"
}'
```

Pegar um usuário pelo ID
```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/user/rochacbruno/' \
  -H 'accept: application/json'
```
```json
{
  "username": "rochacbruno",
  "avatar": "https://github.com/rochacbruno.png",
  "bio": "Programador"
}
```

Listar todos

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/user/' \
  -H 'accept: application/json'
```
```json
[
  {
    "username": "admin",
    "avatar": null,
    "bio": null
  },
  {
    "username": "rochacbruno",
    "avatar": "https://github.com/rochacbruno.png",
    "bio": "Programador"
  }
]
```

## Autenticação

Agora que já podemos criar usuários é importante conseguirmos autenticar
os usuários pois desta forma podemos começar a criar postagens via API

Esse será arquivo com a maior quantidade de código **boilerplate**.

`pamps/auth.py`
```python

```

`pamps/routes/auth.py`
```python

```

`pamps/rotues/__init__.py`
```python

```

Vamos testar a aquisição de um token

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=admin&password=1234&scope=&client_id=&client_secret='
```
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImZyZXNoIjp0cnVlLCJleHAiOjE2Njg2Mjg0NjgsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.P-F3onD2vFFIld_ls1irE9rOgLNk17SNDASls31lgkU",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY2ODY2MjY2OCwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIn0.AWV8QtySYmcukxTgTa9GedLK00o6wrbyMt9opW42eyQ",
  "token_type": "bearer"
}
```

## Adicionando Models de conteúdo

Agora vamos criar as rotas de conteúdo e exigir o token para postar

`pamps/models/post.py`
```python

```

`pamps/models/user.py`
```python

```

`pamps/models/__init__.py`
```python

```

## Database Migration

Agora precisamos chamar o **alambic** para gerar a database migration relativa
a  nova tabela `post`.

Dentro do container shell

```console
$ alembic revision --autogenerate -m "post"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'post'
INFO  [alembic.ddl.postgresql] Detected sequence named 'user_id_seq' as owned by integer column 'user(id)', assuming SERIAL and omitting
  Generating /home/app/api/migrations/versions/f9b269f8d5f8_post.py ...  done
```
e aplicamos com

```console
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 4634e842ac70 -> f9b269f8d5f8, post
```

## Adicionando rotas de conteúdo

Agora os endpoints

`pamps/routes/post.py`
```python

```

`pamps/routes/__init__.py`
```python

```

## Testando
