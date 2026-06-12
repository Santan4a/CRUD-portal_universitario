# CRUD - Portal Universitario

Projeto academico desenvolvido em **Django** para gerenciamento universitario. O sistema centraliza login, perfis de acesso, cadastro de usuarios, alunos, disciplinas, notas, faltas, cronograma academico e area individual do aluno.

A aplicacao utiliza a identidade visual **Portal Tech** e foi criada como projeto de faculdade, com foco em organizar rotinas administrativas e academicas de uma instituicao de ensino.

## Integrantes do projeto

| Integrante | Matricula |
| --- | --- |
| Guilherme Silva Marinho | 01822298 |
| Erlon Matheus de Andrade Oliveira | 01797598 |
| Cauã Vitor | 01794895 |
| João Vitor de Santana Pereira | 01808325 |
| Silvio Matheus da Silva Teixeira | 01831909 |

## Objetivo

O objetivo do projeto e oferecer um portal universitario simples e funcional, permitindo que diferentes perfis de usuario acessem apenas as funcionalidades relacionadas ao seu papel.

O sistema atende principalmente tres publicos:

- **Alunos**, que podem acompanhar notas, faltas, disciplinas, cronograma e acessar o Tutor IA.
- **Professores**, que podem consultar alunos vinculados as suas disciplinas, lancar notas e registrar faltas.
- **Gestao**, que pode administrar usuarios, alunos, professores, disciplinas, notas e faltas.

## Principais recursos

- Login com redirecionamento automatico por perfil.
- Perfis de acesso: aluno, professor, gestao e superusuario.
- Permissoes por tela: gestao, alunos, disciplinas, notas e faltas.
- Dashboard de gestao com busca, filtros e resumo de alunos, professores e usuarios de gestao.
- Cadastro unificado de usuarios pela gestao.
- Edicao e exclusao de alunos, professores e usuarios de gestao.
- Bloqueio para impedir que um usuario de gestao exclua a propria conta.
- Protecao para evitar a remocao do ultimo usuario de gestao.
- Geracao automatica de matriculas e logins no formato `ALU20260001`, `PROF20260001` e `GEST20260001`.
- Geracao de senha inicial aleatoria para novos usuarios.
- Envio de credenciais por e-mail para alunos e professores.
- E-mail institucional automatico para professores no dominio `portaltech.com`.
- Matriz curricular por curso em JSON.
- Vinculo automatico de disciplinas ao aluno conforme o curso.
- Vinculo de disciplinas a professores.
- Lancamento e edicao de notas com media calculada.
- Exportacao de notas em PDF e Excel.
- Exportacao do boletim do aluno em PDF.
- Registro individual de faltas.
- Registro de chamada em massa por disciplina.
- Controle de faltas justificadas.
- Configuracao de limite de faltas por disciplina.
- Area do aluno com notas, faltas, disciplinas e cronograma semanal.
- Cronograma de aulas por disciplina, dia da semana, turno, horario e sala.
- Paginas institucionais de suporte, contato e politicas do portal.
- Tutor IA para alunos com configuracao por chave de API.

## Tecnologias utilizadas

- Python 3.12+
- Django 6.0.5
- SQLite para desenvolvimento local
- PostgreSQL/Supabase como opcao de banco remoto
- `psycopg` para conexao PostgreSQL
- `openpyxl` para exportacao Excel
- `reportlab` para geracao de PDF
- `openai` para integracao com Tutor IA
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
- Git, caso o repositorio seja clonado
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

Para usar Supabase/PostgreSQL, crie um arquivo `.env` na raiz do projeto. O arquivo `.env` e carregado automaticamente por `CRUD/settings.py` e esta listado no `.gitignore`, pois pode conter senhas e chaves privadas.

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

Variaveis extras de seguranca aceitas pelo projeto:

```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://seudominio.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_USE_X_FORWARDED_PROTO=True
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

Sem essa variavel, a funcionalidade informa que a chave da API nao foi configurada. A dependencia `openai` ja esta listada em `requirements.txt`.

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

## Perfis e permissoes

### Aluno

O aluno acessa sua propria area academica, com:

- Curso e matricula.
- Disciplinas vinculadas.
- Notas e media.
- Faltas.
- Cronograma semanal.
- Exportacao de boletim em PDF.
- Tutor IA.

### Professor

Por padrao, o professor pode acessar:

- Alunos vinculados as disciplinas que leciona.
- Notas das disciplinas sob sua responsabilidade.
- Faltas e chamadas das disciplinas sob sua responsabilidade.

Professores recebem matricula/login automatico, e-mail institucional e disciplinas vinculadas ao curso informado.

### Gestao

A gestao tem acesso administrativo as telas do portal:

- Dashboard de gestao.
- Cadastro de alunos, professores e usuarios de gestao.
- Edicao e exclusao de alunos, professores e gestores.
- Disciplinas.
- Notas.
- Faltas.
- Permissoes por tela para usuarios de gestao.

### Superusuario

O superusuario do Django tem acesso completo as telas do portal e ao Django Admin.

## Rotas principais

| Rota | Descricao |
| --- | --- |
| `/` | Login |
| `/login/` | Login |
| `/logout/` | Logout |
| `/portal/` | Redirecionamento por perfil |
| `/admin/` | Django Admin |
| `/alunos/` | Lista de alunos |
| `/alunos/minha-area/` | Area do aluno |
| `/alunos/minha-area/exportar-notas/` | Exportacao do boletim do aluno em PDF |
| `/alunos/dashboard/<id>/` | Dashboard de um aluno |
| `/alunos/tutor-ia-page/` | Tela do Tutor IA |
| `/alunos/tutor-ia/` | Endpoint de resposta do Tutor IA |
| `/disciplinas/` | Lista de disciplinas |
| `/disciplinas/criar/` | Cadastro de disciplina |
| `/disciplinas/editar/<id>/` | Edicao de disciplina |
| `/disciplinas/excluir/<id>/` | Exclusao de disciplina |
| `/notas/` | Lista de notas |
| `/notas/nova/` | Cadastro de nota |
| `/notas/editar/<id>/` | Edicao de nota |
| `/notas/deletar/<id>/` | Exclusao de nota |
| `/notas/exportar/` | Tela de exportacao de notas |
| `/notas/exportar/pdf/` | Exportacao de notas em PDF |
| `/notas/exportar/excel/` | Exportacao de notas em Excel |
| `/faltas/` | Lista de faltas |
| `/faltas/nova/` | Cadastro de falta |
| `/faltas/chamada/` | Registro de chamada em massa |
| `/faltas/limites/` | Configuracao de limites de faltas |
| `/faltas/editar/<id>/` | Edicao de falta |
| `/faltas/excluir/<id>/` | Exclusao de falta |
| `/cronograma/grade/` | Grade de horarios |
| `/gestao/dashboard/` | Dashboard de gestao |
| `/gestao/usuarios/novo/` | Cadastro de usuario pela gestao |
| `/gestao/alunos/novo/` | Cadastro de aluno pela gestao |
| `/gestao/alunos/<id>/editar/` | Edicao de aluno pela gestao |
| `/gestao/alunos/<id>/excluir/` | Exclusao de aluno pela gestao |
| `/gestao/professores/<id>/editar/` | Edicao de professor pela gestao |
| `/gestao/professores/<id>/excluir/` | Exclusao de professor pela gestao |
| `/gestao/gestores/<id>/editar/` | Edicao de usuario de gestao |
| `/gestao/gestores/<id>/excluir/` | Exclusao de usuario de gestao |
| `/contato/` | Contato |
| `/suporte/` | Suporte |
| `/politicas/` | Politicas do portal |

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

O cronograma usa o app `cronograma` e o modelo `Cronograma`, com disciplina, dia da semana, turno, horario de inicio, horario de fim e sala.

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
alunos/              Area do aluno, dashboards, boletim e Tutor IA
cronograma/          Grade de horarios
disciplinas/         Cadastro, catalogo e matriz curricular
faltas/              Registro de faltas, chamadas e limites
notas/               Lancamento, calculo e exportacao de notas
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
- `db.sqlite3` esta listado no `.gitignore` e deve ser tratado como banco local.
- Em producao, configure `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` e um banco persistente.
- O backend de e-mail local por padrao imprime mensagens no terminal, o que ajuda a testar cadastro sem SMTP real.
- Antes de apresentar ou entregar o projeto, rode `python manage.py check` e `python manage.py test`.

## Status do projeto

Projeto academico funcional para demonstracao de um portal universitario com controle de usuarios, alunos, disciplinas, notas, faltas, cronograma e area do aluno.
