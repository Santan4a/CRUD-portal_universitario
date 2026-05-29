# CRUD - Portal Universitário

Projeto desenvolvido em **Django** para gerenciamento acadêmico universitário, com controle de:

- Cadastro de alunos
- Disciplinas
- Notas
- Faltas
- Gestão acadêmica
- Perfis de acesso (Aluno, Professor e Gestão)

---

## Tecnologias utilizadas

- Python 3.12+
- Django
- SQLite (desenvolvimento local) / PostgreSQL Supabase
- HTML / CSS
- Shell Script (`.sh`)
- Virtual Environment (`venv`)

---

## Requisitos

Antes de executar o projeto, tenha instalado:

- Python 3.12 ou superior
- pip
- Git (caso vá clonar o projeto)

As dependências Python estão em:

```text
requirements.txt
```

---

# Instalação e execução rápida (Automatizada)

Agora o projeto possui scripts de automação para facilitar a instalação e execução.

---

## Script de setup

Arquivo:

```text
setup.sh
```

Esse script faz automaticamente:

- Detecta se o Python instalado é `python` ou `python3`
- Cria o ambiente virtual `.venv` caso ele não exista
- Ativa o ambiente virtual
- Atualiza o pip
- Instala todas as dependências de `requirements.txt`

### Rodar:

```bash
bash setup.sh
```

---

## Script de execução

Arquivo:

```text
run.sh
```

Esse script faz automaticamente:

- Detecta o Python correto (`python` ou `python3`)
- Ativa o ambiente virtual
- Executa as migrations
- Inicia o servidor Django

### Rodar:

```bash
bash run.sh
```

---

## Fluxo completo (mais simples)

Depois de clonar o projeto:

### Primeira vez:

```bash
bash setup.sh
```

### Depois para rodar:

```bash
bash run.sh
```

---

# Banco de dados com Supabase

O projeto usa SQLite automaticamente quando nenhuma variável de banco remoto está definida. Para usar o Supabase, crie um arquivo `.env` na raiz do projeto e informe a conexão PostgreSQL do seu projeto Supabase.

## Opção recomendada: URL do Supabase

No painel do Supabase, abra o projeto, clique em **Connect** e copie a connection string do **Session Pooler** ou da conexão direta. Em seguida, configure:

```env
SUPABASE_DATABASE_URL=postgres://postgres.PROJECT_REF:SENHA@aws-0-REGIAO.pooler.supabase.com:5432/postgres
```

Quando usar `DATABASE_URL` em vez de `SUPABASE_DATABASE_URL`, inclua SSL explicitamente:

```env
DATABASE_URL=postgres://postgres.PROJECT_REF:SENHA@aws-0-REGIAO.pooler.supabase.com:5432/postgres?sslmode=require
```

## Alternativa: campos separados

```env
USE_SUPABASE=True
SUPABASE_DB_HOST=aws-0-REGIAO.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.PROJECT_REF
SUPABASE_DB_PASSWORD=sua-senha-do-banco
SUPABASE_DB_SSLMODE=require
```

Depois de configurar o `.env`, rode as migrations no Supabase:

```bash
python manage.py migrate
```

As migrations criam as tabelas e os usuários de teste no banco remoto. O arquivo `.env` já fica ignorado pelo Git; não versionar a senha do banco é parte importante da brincadeira séria aqui.

---

# Execução manual (sem scripts)

Caso queira fazer tudo manualmente:

---

## Windows (PowerShell)

### 1. Entrar na pasta

```powershell
cd caminho\para\CRUD-portal_universitario
```

---

### 2. Criar ambiente virtual

```powershell
python -m venv .venv
```

---

### 3. Ativar ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Se der bloqueio:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

### 4. Instalar dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Rodar migrations

```powershell
python manage.py migrate
```

---

### 6. Rodar servidor

```powershell
python manage.py runserver
```

---

## Linux

### 1. Entrar na pasta

```bash
cd /caminho/para/CRUD-portal_universitario
```

---

### 2. Criar ambiente virtual

```bash
python3 -m venv .venv
```

Caso necessário:

```bash
sudo apt install python3-venv
```

---

### 3. Ativar ambiente virtual

```bash
source .venv/bin/activate
```

---

### 4. Instalar dependências

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Rodar migrations

```bash
python manage.py migrate
```

---

### 6. Rodar servidor

```bash
python manage.py runserver
```

---

# Acesso ao sistema

Abra no navegador:

```text
http://127.0.0.1:8000/
```

A rota inicial abre a tela de login.

Após autenticação, o usuário é redirecionado para sua área correspondente.

---

# Rotas principais

- `/` → Login
- `/alunos/`
- `/gestao/dashboard/`
- `/gestao/alunos/novo/`
- `/disciplinas/`
- `/notas/`
- `/logout/`
- `/admin/`

---

# Perfis de acesso

O sistema possui três tipos de usuários:

### Aluno

Visualiza:

- Área acadêmica
- Notas
- Faltas
- Disciplinas matriculadas
- Curso

---

### Professor

Gerencia:

- Alunos
- Disciplinas
- Notas
- Faltas

---

### Gestão

Acessa:

- Dashboard administrativo
- Cadastro de novos alunos
- Vinculação de curso

---

# Usuários de teste

Criados automaticamente pelas migrations:

```bash
python manage.py migrate
```

Se necessário:

```bash
python manage.py seed_portal_users
```

---

## Credenciais

### Aluno

```text
Usuário: aluno
Senha: aluno123
```

---

### Professor

```text
Usuário: professor
Senha: professor123
```

---

### Gestão

```text
Usuário: gestao
Senha: gestao123
```

---

# Criar superusuário

Para acessar o Django Admin:

```bash
python manage.py createsuperuser
```

---

# Matriz curricular (JSON)

Arquivo:

```text
disciplinas/data/cursos_disciplinas.json
```

Formato:

```json
{
  "Bacharelado em Sistemas de Informação e Transformação Digital": [
    {
      "codigo": "SI101",
      "nome": "Algoritmos e Programação"
    }
  ]
}
```

Ao cadastrar um aluno com um curso:

- O sistema verifica as disciplinas
- Cria as que não existem
- Vincula automaticamente ao aluno

---

# Testes

Rodar:

```bash
python manage.py test
```

---

# Verificação do projeto

Rodar:

```bash
python manage.py check
```

---

# Variáveis de ambiente para produção

Obrigatórias:

- `DJANGO_PRODUCTION=True`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`

---

## Linux

```bash
export DJANGO_PRODUCTION=True
export DJANGO_SECRET_KEY="troque-por-uma-chave-forte"
export DJANGO_ALLOWED_HOSTS="seudominio.com,www.seudominio.com"
```

---

## PowerShell

```powershell
$env:DJANGO_PRODUCTION="True"
$env:DJANGO_SECRET_KEY="troque-por-uma-chave-forte"
$env:DJANGO_ALLOWED_HOSTS="seudominio.com,www.seudominio.com"
```

---

# Estrutura de automação adicionada

Scripts implementados:

```text
setup.sh
run.sh
```

### `setup.sh`

Responsável por:

- Detectar Python automaticamente
- Criar `.venv`
- Ativar ambiente virtual
- Atualizar pip
- Instalar dependências

---

### `run.sh`

Responsável por:

- Detectar Python automaticamente
- Ativar `.venv`
- Rodar migrations
- Iniciar servidor Django

---

Isso permite executar o projeto com apenas:

```bash
bash setup.sh
bash run.sh
```

Sem precisar repetir todos os comandos manualmente.

---

# Autor

Projeto acadêmico desenvolvido para gerenciamento universitário usando Django.