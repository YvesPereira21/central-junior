

---
O **Central Junior** é uma plataforma desenvolvida com o objetivo de centralizar e democratizar o conhecimento para desenvolvedores estagiários e juniores. O projeto funciona como um ecossistema onde devs podem encontrar artigos técnicos detalhados sobre implementações, funções específicas e bibliotecas, além de interagir em um sistema de Perguntas e Respostas.

A plataforma possui um sistema de **gamificação e reputação**. Usuários ganham pontos ao contribuir com a comunidade (escrevendo artigos ou tendo respostas aceitas), evoluindo de nível e conquistando credibilidade técnica. Além de que, se o usuário for um profissional e assim comprovar através do envio do currículo, ele será classificado como profissional
em seu perfil e ganhará pontos de acordo com seu nível de experiência a cada empresa por qual passou, trazendo mais credibilidade sobre o conteúdo e resposta apresentados.

## Funcionalidades Principais

- **Artigos Técnicos**: Espaço para publicação de tutoriais e explicações de código e funções, com suporte a **markdown** e tags de tecnologias.
- **Q&A (Perguntas e Respostas)**: 
    - Usuários podem postar dúvidas vinculadas a tecnologias.
    - Sistema de "Resposta Aceita" (Solutioned): O autor da pergunta pode marcar uma resposta como a solução definitiva.
    - Upvotes em respostas úteis.

- **Sistema de Gamificação**: 
    - **Reputação**: Pontos são atribuídos por artigos criados, respostas aceitas e credenciais verificadas.
    - **Níveis**: Os usuários evoluem automaticamente de nível com base no score:
        - _Iniciante_ (0 pts)
        - _Intermediário_ (500 pts)
        - _Especialista_ (1000 pts)
        - _Elite_ (2000 pts)
            
- **Credenciais Profissionais**: Usuários podem cadastrar experiências profissionais e acadêmicas. Se validadas por um administrador, o usuário ganha o selo de "Profissional" e pontos extras.
    
- **Autenticação**: Sistema completo com JWT (JSON Web Token).
    

## Tecnologias utilizadas

- **Python 3.12** & **Django 5.2.7**
- **Django Rest Framework**
- **PostgreSQL** (Banco de dados)
- **Redis** (Cache para otimização de endpoints)
- **Docker** & **Docker Compose**


## Bibliotecas utilizadas para robustez do sistema

- **drf-spectacular** (Documentação Swagger/Redoc)
- **drf-standardized-errors** (Gerar respostas de erro padronizadas e condizente com o tipo)
- **django-filter** (Para filtros e pesquisas)
- **djangorestframework_simplejwt** (Para autenticação com token JWT)
- **pillow** (Para que as tags possuam imagem, além de apenas cores)

---

## Rotas da API

A API está organizada nos seguintes endpoints principais (prefixo `/api/v1/`):

### 🔐 Autenticação

- `POST /authentication/token/`: Login (Obter par de tokens access/refresh).
    
- `POST /authentication/token/refresh/`: Atualizar o token de acesso.
    
- `POST /authentication/logout/`: Logout (Blacklist do token).
    

### 👤 Perfis (Profiles)

- `POST /profiles/`: Criar uma conta de usuário.
    
- `GET /profiles/{id}/`: Detalhes do perfil (nível, bio, score).
    
- `PUT/PATCH /profiles/{id}/`: Atualizar dados do perfil.
    

### 📚 Artigos

- `GET /articles/`: Listar artigos publicados (com filtros por tecnologia, autor, etc).
    
- `POST /articles/`: Publicar novo artigo.
    
- `GET /articles/{id}/`: Ler artigo completo.
    
- `POST /articles/{id}/like/`: Dar/Remover like em um artigo.
    

### ❓ Perguntas e Respostas

- `GET /questions/`: Listar perguntas.
    
- `POST /questions/`: Criar nova pergunta.
    
- `POST /questions/{id}/like/`: Dar like em uma pergunta.
    
- `GET /questions/{id}/answers/`: Listar respostas de uma pergunta específica.
    
- `POST /answers/`: Enviar uma resposta.
    
- `PATCH /answers/{id}/accept/`: Marcar resposta como aceita (apenas dono da pergunta).
    

### 🏆 Credenciais e Tecnologias

- `POST /credentials/`: Adicionar experiência profissional/acadêmica.
    
- `PATCH /credentials/{id}/validate/`: Validar credencial (Apenas Admin).
    
- `GET /tags/`: Listar tecnologias disponíveis para vincular em posts.
    

---

## Permissões e Segurança

O projeto utiliza um sistema de permissões personalizado para garantir a integridade dos dados e a lógica da gamificação:

### Permissões Padrão

- **AllowAny (Público)**: Qualquer pessoa (mesmo não logada) pode visualizar listas de Artigos e Perguntas, bem como os detalhes de um post específico.
- **IsAuthenticated (Logado)**: Necessário para criar qualquer conteúdo (Artigos, Perguntas, Respostas, Credenciais) e interagir com likes.
- **IsAdminUser (Administrador)**: Apenas administradores podem criar/editar Tecnologias (Tags) e validar Credenciais de usuários.
    

### Permissões Personalizadas (`IsOwner`)

Para garantir que usuários só alterem seus próprios dados, foram implementadas as seguintes classes:

- **IsOwner**: Permite que apenas o criador do objeto possa editá-lo (`PATCH/PUT`) ou excluí-lo (`DELETE`). Aplicado em Artigos, Respostas, Credenciais e Perfis. 
- **IsOwnerQuestion**: Uma permissão especial para o endpoint de aceitar resposta (`/answers/{id}/accept/`). Garante que **apenas o autor da Pergunta** possa marcar uma Resposta como "Solucionada" (Accepted), disparando a pontuação para o autor da resposta.


---

## Como Rodar o Projeto

Este projeto utiliza **Docker** para facilitar a configuração do ambiente (Django, Postgres e Redis).

### Pré-requisitos

- Docker e Docker Compose instalados.
    
- Git.
    

### Passo a Passo

1. **Clone o repositório:**
    
    Bash
    
    ```
    git clone https://github.com/yvespereira21/central-junior.git
    cd central-junior
    ```
    
2. Configure as Variáveis de Ambiente:
    
    Crie um arquivo .env na raiz do projeto (baseado nas chaves usadas no settings.py):
    
    Snippet de código
    
    ```
    SECRET_KEY=sua_chave_secreta_aqui
    DEBUG=True
    
    # Configuração do Banco de Dados (deve bater com o docker-compose)
    DB_NAME=central_junior
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=central_junior_db
    DB_PORT=5432
    
    # Cache
    CACHE_TTL=300
    ```
    
3. Suba os containers:
    
    Execute o comando abaixo para construir e iniciar os serviços:
    
    Bash
    
    ```
    docker-compose up --build
    ```
    
4. Execute as Migrações:
    
    Com os containers rodando, abra um novo terminal e aplique as migrações no banco:
    
    Bash
    
    ```
    docker-compose exec central_junior_web python manage.py migrate
    ```
    
5. Crie um Superusuário (Opcional):
    
    Para acessar o admin do Django ou validar credenciais:
    
    Bash
    
    ```
    docker-compose exec central_junior_web python manage.py createsuperuser
    ```
    
6. **Acesse a Aplicação:**
    
    - API: `http://localhost:8000/api/v1/`
        
    - Swagger UI: `http://localhost:8000/documentation/api/schema/swagger-ui/`
        

---

## Testes

Para rodar a suíte de testes automatizados:

Bash

```
docker-compose exec central_junior_web python manage.py test
```