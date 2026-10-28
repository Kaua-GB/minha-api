# Passo a passo – LAB8 Cloud (CI/CD: GitHub → Docker Hub → AWS EC2)

Este guia é para iniciantes. Siga na ordem. Onde estiver **[VOCÊ]**, é algo que só você pode fazer (porque depende das suas contas). Onde estiver **[JÁ FEITO]**, eu já preparei para você.

---

## O que o projeto faz (resumo em 4 linhas)

1. Você envia o código para o GitHub (`git push` na branch `main`).
2. O GitHub roda os testes automaticamente (pytest).
3. Se os testes passarem, ele cria uma imagem Docker e envia para o Docker Hub.
4. Depois ele entra na sua máquina da AWS (EC2) e troca o container antigo pelo novo.

---

## PARTE A – O que eu já fiz [JÁ FEITO]

Criei a pasta `minha-api/` com esta estrutura:

```
minha-api/
├── .github/workflows/docker-hub.yml   <- o pipeline (3 etapas)
├── app/main.py                        <- a API FastAPI
├── tests/test_main.py                 <- os testes
├── Dockerfile                         <- receita da imagem Docker
├── .dockerignore                      <- o que NÃO vai para a imagem
├── .gitignore                         <- o que NÃO vai para o GitHub
└── requirements.txt                   <- bibliotecas do Python
```

Também corrigi pequenos erros que existiam no guia do professor:

- As aspas curvas `“3.11”` viravam erro no YAML. Troquei por aspas normais `"3.11"`.
- Os 3 jobs (Build, Imagem, Deploy) precisam ficar **no mesmo arquivo**, senão o `needs:` não funciona. Por isso ficaram todos em `docker-hub.yml`.
- O usuário do Docker Hub estava fixo (`ngaloni`). Troquei por `${{ secrets.DOCKERHUB_USERNAME }}`, então funciona com a **sua** conta.
- O passo "Resumo do deploy" usava `steps.meta`, que não existe. Corrigi.

---

## PARTE B – Testar no seu computador [VOCÊ]

Abra o terminal dentro da pasta `minha-api/`.

**1. Criar o ambiente virtual e instalar as bibliotecas (Windows):**

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pytest httpx
```

**2. Rodar os testes:**

```
python -m pytest tests/ -v --tb=short
```

Deve aparecer `3 passed`.

**3. Rodar a API:**

```
python -m uvicorn app.main:app --reload --port 8080
```

Abra no navegador: http://127.0.0.1:8080 e http://127.0.0.1:8080/health

(Dica: `http://127.0.0.1:8080/docs` mostra a documentação automática.)

**4. Testar o Docker (Docker Desktop precisa estar aberto):**

```
docker build -t senai_fastapi .
docker run -p 8080:8080 senai_fastapi
```

---

## PARTE C – Contas e configurações [VOCÊ]

### C1. GitHub
1. Entre em github.com e clique em **New repository**.
2. Nome sugerido: `minha-api`. Pode ser público.
3. No terminal, dentro de `minha-api/`:

```
git init
git add .
git commit -m "primeiro commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/minha-api.git
git push -u origin main
```

(Não se preocupe se o primeiro push falhar no deploy: falta configurar os Secrets, veja C3.)

### C2. Docker Hub
1. Crie conta em hub.docker.com.
2. Vá em **Account Settings → Security → Access Tokens → New Access Token**.
3. Dê um nome (ex.: `github-actions`), permissão **Read & Write**, e **copie o token** (ele só aparece uma vez).

### C3. Secrets no GitHub
No repositório: **Settings → Secrets and variables → Actions → New repository secret**.
Crie estes 5 secrets (nomes exatamente iguais):

| Nome | Valor |
|---|---|
| `DOCKERHUB_USERNAME` | seu usuário do Docker Hub |
| `DOCKERHUB_TOKEN` | o token que você copiou no C2 |
| `EC2_HOST` | IP público (ou DNS) da sua EC2 |
| `EC2_USERNAME` | `ubuntu` (Ubuntu) ou `ec2-user` (Amazon Linux) |
| `EC2_SSH_KEY` | conteúdo COMPLETO do arquivo `.pem`, com as linhas BEGIN e END |

### C4. AWS EC2
1. Em aws.amazon.com, vá em **EC2 → Launch instance**.
2. Escolha **Ubuntu 22.04 LTS** (ou Amazon Linux 2) e o tipo `t2.micro`/`t3.micro`.
3. Crie um **key pair** (.pem) e guarde o arquivo.
4. No **Security Group**, libere as portas **22** (SSH) e **8080** (a API), origem `0.0.0.0/0`.
5. Conecte na máquina e instale o Docker (Ubuntu):

```
sudo apt update
sudo apt install -y docker.io curl
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

---

## PARTE D – Ver o pipeline funcionando [VOCÊ]

1. Faça qualquer mudança pequena (ex.: mude a mensagem em `app/main.py`).
2. Envie:

```
git add .
git commit -m "teste do pipeline"
git push
```

3. No GitHub, abra a aba **Actions**. Você verá 3 etapas: **Compilar Projeto → Construindo Imagem para Docker → Implantação AWS**. Todas devem ficar verdes ✅.
4. Abra no navegador: `http://IP_DA_EC2:8080` e `http://IP_DA_EC2:8080/health`.

---

## Problemas comuns

| Erro | Causa provável |
|---|---|
| Falha no login do Docker Hub | Secret `DOCKERHUB_TOKEN` ou `DOCKERHUB_USERNAME` errado |
| `ssh: handshake failed` | `EC2_SSH_KEY` sem as linhas BEGIN/END, ou usuário errado |
| API não abre no navegador | Porta 8080 não liberada no Security Group |
| `docker: permission denied` | Rode o `usermod` do C4 e reconecte na EC2 |
| Teste falha por falta de `httpx` | Faltou `pip install httpx` |

## Rollback (voltar versão)

Na EC2, use o SHA do commit anterior (aparece no Docker Hub, aba Tags):

```
sudo docker stop senai_fastapi && sudo docker rm senai_fastapi
sudo docker run -d --name senai_fastapi -p 8080:8080 SEU_USUARIO/senai_fastapi:SHA_DO_COMMIT_ANTERIOR
```
