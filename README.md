# Mini App de Fila de Atendimento

Aplicação web desenvolvida em **Python + Flask + SQLite** para gerenciamento de uma fila de atendimento.

## Funcionalidades

- Cadastro de clientes;
- Fila de espera;
- Atendimento seguindo ordem de chegada (FIFO);
- Status: Aguardando, Em Atendimento e Concluído;
- Cancelamento de atendimento;
- Prioridade Normal ou Preferencial;
- Histórico de atendimentos;
- Atualização automática da página;
- API simples para consultar a fila.

## Tecnologias

- Python 3
- Flask
- SQLite
- HTML5
- CSS3
- Jinja2

## Como executar

### 1. Instale o Python

Baixe o Python pelo site oficial:
https://www.python.org/downloads/

### 2. Abra o terminal na pasta do projeto

No Windows, você pode abrir a pasta e usar o botão direito + "Abrir no Terminal".

### 3. Crie um ambiente virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute o projeto

```bash
python app.py
```

### 6. Abra no navegador

Acesse:

http://127.0.0.1:5000

O banco `fila.db` será criado automaticamente na primeira execução.

## Como funciona a fila

Clientes são armazenados no SQLite com um ID crescente.

A chamada do próximo cliente considera:

1. Clientes preferenciais primeiro;
2. Dentro da mesma prioridade, quem entrou primeiro é atendido primeiro.

Assim, a fila normal segue o conceito **FIFO (First In, First Out)**.

## Estrutura

```text
fila_atendimento/
├── app.py
├── requirements.txt
├── README.md
├── fila.db              # criado automaticamente após executar
├── templates/
│   ├── index.html
│   └── historico.html
└── static/
    └── style.css
```

## Rotas principais

- `/` — página principal;
- `/cadastrar` — cadastro de cliente;
- `/chamar` — chama o próximo;
- `/status/<id>` — altera o status;
- `/cancelar/<id>` — cancela um atendimento;
- `/historico` — mostra o histórico;
- `/api/fila` — retorna a fila em JSON.

## Bônus implementados

### Prioridade
O cliente pode entrar como Normal ou Preferencial.

### Histórico
Atendimentos concluídos e cancelados ficam registrados na página de histórico.

### Atualização automática
A página principal é atualizada automaticamente a cada 15 segundos.

## GitHub

Depois de testar o projeto, crie um repositório no GitHub e envie os arquivos:

```bash
git init
git add .
git commit -m "Projeto inicial - fila de atendimento"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/fila-atendimento.git
git push -u origin main
```

Depois, envie o link do seu repositório para o professor.

## Autor

Projeto acadêmico — Mini App de Fila de Atendimento.
