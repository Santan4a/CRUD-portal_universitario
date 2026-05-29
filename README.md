# CRUD - Portal Universitario

Projeto academico desenvolvido em **Django** para gerenciamento universitario. O sistema centraliza login, perfis de acesso, cadastro de usuarios, alunos, disciplinas, notas, faltas, cronograma academico e area individual do aluno.

O projeto tambem usa a identidade visual **Portal Tech** nas telas da aplicacao.

## Principais recursos

- Login com redirecionamento automatico por perfil.
- Perfis de acesso: aluno, professor, gestao e superusuario.
- Permissoes por tela: gestao, alunos, disciplinas, notas e faltas.
- Dashboard de gestao com busca, filtros e resumo de alunos, professores e usuarios de gestao.
- Cadastro unificado de usuarios pela gestao.
- Geracao automatica de matriculas e logins no formato `ALU20260001`, `PROF20260001` e `GEST20260001`.
- Geracao de senha inicial aleatoria para novos usuarios.
- Envio de credenciais por e-mail para alunos e professores.
- E-mail institucional automatico para professores no dominio `portaltech.com`.
- Matriz curricular por curso em JSON.
- Vinculo automatico de disciplinas ao aluno conforme o curso.
- Lancamento e edicao de notas com media calculada.
- Registro de faltas com status de justificativa.
- Area do aluno com notas, faltas, disciplinas e cronograma semanal.
- Cronograma de aulas por disciplina, dia, horario e sala.
- Paginas de suporte, contato e politicas do portal.
- Tutor IA para alunos, com configuracao opcional de API.

## Tecnologias

- Python 3.12+
- Django 6.0.5
- SQLite para desenvolvimento local
- PostgreSQL/Supabase opcional
- `psycopg` para conexao PostgreSQL
- HTML, CSS e JavaScript
- Shell scripts para setup e execucao

As dependencias Python ficam em:

```text
requirements.txt
```

## Requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.12 ou superior
- pip
- Git, se for clonar o repositorio
- Bash, caso queira usar `setup.sh` e `run.sh`

## Execucao rapida

Na primeira execucao:

```bash
bash setup.sh
bash run.sh
```

Depois disso, para subir o servidor novamente:

```bash
bash run.sh
```

O servidor ficara disponivel em:

```text
http://127.0.0.1:8000/
```

### O que os scripts fazem

`setup.sh`:

- Detecta `python` ou `python3`.
- Cria a `.venv` se ela ainda nao existir.
- Instala as dependencias de `requirements.txt` usando o Python da `.venv`.

`run.sh`:

- Usa o Python da `.venv`.
- Executa `manage.py migrate`.
- Inicia o servidor com `manage.py runserver`.

## Execucao manual

### Linux, macOS ou Git Bash

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Se o sistema nao tiver suporte a `venv` instalado:

```bash
sudo apt install python3-venv
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Se o PowerShell bloquear a ativacao do ambiente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Banco de dados

Por padrao, o projeto usa SQLite local em `db.sqlite3`.

Para usar Supabase/PostgreSQL, crie um arquivo `.env` na raiz do projeto. O arquivo `.env` e carregado automaticamente por `CRUD/settings.py` e ja esta ignorado pelo Git.

Voce pode usar `.env.example` como base:

```bash
cp .env.example .env
```

### Opcao recomendada: URL do Supabase

No painel do Supabase, copie a connection string em **Connect** e configure:

```env
SUPABASE_DATABASE_URL=postgres://postgres.PROJECT_REF:SENHA@aws-0-REGIAO.pooler.supabase.com:5432/postgres
```

Quando usar `SUPABASE_DATABASE_URL`, o projeto aplica `sslmode=require` automaticamente.

Tambem e possivel usar `DATABASE_URL`:

```env
DATABASE_URL=postgres://postgres.PROJECT_REF:SENHA@aws-0-REGIAO.pooler.supabase.com:5432/postgres?sslmode=require
```

### Alternativa: campos separados

```env
USE_SUPABASE=True
SUPABASE_DB_HOST=aws-0-REGIAO.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.PROJECT_REF
SUPABASE_DB_PASSWORD=sua-senha-do-banco
SUPABASE_DB_SSLMODE=require
SUPABASE_DB_CONN_MAX_AGE=60
SUPABASE_DB_CONN_HEALTH_CHECKS=True
SUPABASE_DB_DISABLE_SERVER_SIDE_CURSORS=False
```

Depois de configurar o banco remoto:

```bash
python manage.py migrate
```

## Variaveis de ambiente

### Django em producao

Obrigatorias quando `DJANGO_PRODUCTION=True`:

```env
DJANGO_PRODUCTION=True
DJANGO_SECRET_KEY=troque-por-uma-chave-forte
DJANGO_ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

O `DEBUG` fica desligado automaticamente em producao, mas pode ser controlado com:

```env
DJANGO_DEBUG=False
```

### E-mail

O envio de credenciais usa SMTP quando as variaveis abaixo estao configuradas. Sem SMTP em ambiente local, o Django usa o backend de console e imprime o e-mail no terminal.

```env
DJANGO_EMAIL_HOST=smtp.gmail.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_HOST_USER=seu-email@gmail.com
DJANGO_EMAIL_HOST_PASSWORD=sua-senha-de-app
DJANGO_DEFAULT_FROM_EMAIL=Portal Tech <seu-email@gmail.com>
```

### Tutor IA

A rota de Tutor IA usa `OPENAI_API_KEY`:

```env
OPENAI_API_KEY=sua-chave
```

Essa funcionalidade importa os pacotes `openai` e `python-dotenv` quando acionada. Se for usa-la, instale essas dependencias opcionais no ambiente virtual.

## Usuarios de teste

As migrations criam usuarios iniciais. Se precisar recriar ou resetar os usuarios padrao, rode:

```bash
python manage.py seed_portal_users
```

Credenciais padrao:

| Perfil | Usuario | Senha |
| --- | --- | --- |
| Aluno | `aluno` | `aluno123` |
| Professor | `professor` | `professor123` |
| Gestao | `gestao` | `gestao123` |

Para acessar o Django Admin, crie um superusuario:

```bash
python manage.py createsuperuser
```

## Perfis e acesso

### Aluno

O aluno acessa sua propria area academica, com:

- Curso e matricula.
- Disciplinas vinculadas.
- Notas e media.
- Faltas.
- Cronograma semanal.
- Tutor IA.

### Professor

Por padrao, o professor pode acessar:

- Alunos.
- Notas.
- Faltas.

Professores recebem matricula/login automatico, e-mail institucional e uma disciplina vinculada ao curso informado.

### Gestao

A gestao tem acesso administrativo as telas do portal:

- Dashboard de gestao.
- Cadastro de alunos, professores e usuarios de gestao.
- Edicao e exclusao de alunos, professores e gestores.
- Disciplinas.
- Notas.
- Faltas.

O sistema impede que um usuario de gestao exclua a propria conta e evita a remocao do ultimo usuario de gestao.

## Rotas principais

| Rota | Descricao |
| --- | --- |
| `/` | Login |
| `/login/` | Login |
| `/logout/` | Logout |
| `/portal/` | Redirecionamento por perfil |
| `/alunos/minha-area/` | Area do aluno |
| `/alunos/` | Lista de alunos |
| `/alunos/dashboard/<id>/` | Dashboard de um aluno |
| `/alunos/tutor-ia-page/` | Tela do Tutor IA |
| `/disciplinas/` | Lista de disciplinas |
| `/notas/` | Lista de notas |
| `/faltas/` | Lista de faltas |
| `/cronograma/grade/` | Grade de horarios |
| `/gestao/dashboard/` | Dashboard de gestao |
| `/gestao/usuarios/novo/` | Cadastro de usuario pela gestao |
| `/contato/` | Contato |
| `/suporte/` | Suporte |
| `/politicas/` | Politicas do portal |
| `/admin/` | Django Admin |

## Matriz curricular

A matriz curricular fica em:

```text
disciplinas/data/cursos_disciplinas.json
```

Formato:

```json
{
  "Bacharelado em Sistemas de Informacao e Transformacao Digital": [
    {
      "codigo": "SI101",
      "nome": "Algoritmos e Programacao"
    }
  ]
}
```

Ao cadastrar ou editar um aluno com curso:

- O sistema le o JSON da matriz curricular.
- Cria as disciplinas que ainda nao existirem.
- Vincula as disciplinas ao aluno.
- Remove notas e faltas antigas que nao pertencem mais ao curso atual do aluno.

## Cronograma

O cronograma usa o app `cronograma` e o modelo `Cronograma`, com disciplina, dia da semana, horario de inicio, horario de fim e sala.

Para popular uma grade de exemplo com base nas disciplinas cadastradas:

```bash
python manage.py popular_cronograma
```

## Testes e verificacao

Rodar a suite de testes:

```bash
python manage.py test
```

Verificar a configuracao do Django:

```bash
python manage.py check
```

## Estrutura do projeto

```text
CRUD/                Configuracao principal do Django
alunos/              Area do aluno, dashboards e Tutor IA
cronograma/          Grade de horarios
disciplinas/         Cadastro e catalogo de disciplinas
faltas/              Registro de faltas
notas/               Lancamento de notas
users/               Perfis, permissoes, usuarios e e-mails
templates/           Templates globais
static/              CSS, JavaScript e assets visuais
setup.sh             Instalacao automatizada
run.sh               Execucao automatizada
requirements.txt     Dependencias Python
.env.example         Exemplo de variaveis de ambiente
```

## Observacoes importantes

- Nao versione o arquivo `.env`, pois ele pode conter senhas e chaves de API.
- `db.sqlite3` e ignorado pelo Git e deve ser tratado como banco local.
- Em producao, configure `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` e um banco persistente.
- O backend de e-mail local por padrao imprime mensagens no terminal, o que ajuda a testar cadastro sem SMTP real.

## Autor

Projeto academico desenvolvido para gerenciamento universitario usando Django.
