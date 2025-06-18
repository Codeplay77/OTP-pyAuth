# Python Authenticator

**Aplicativo de autenticação de dois fatores (2FA) desenvolvido em Python com interface gráfica moderna, similar ao Google Authenticator.**

```
Python Authenticator
┌─────────────────────────────────────┐
│  Google - usuario@gmail.com         │
│     123 456     📋                  │
│  ████████████████░░░░░░░░  15s      │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  Microsoft - trabalho@company       │
│     789 012     📋                  │
│  ██████████████████████░░░  5s      │
└─────────────────────────────────────┘
```

## Características

- **Geração de códigos TOTP** compatível com Google Authenticator.
- **Interface moderna** com design Material Design.
- **Armazenamento seguro** com criptografia AES das chaves secretas.
- **Atualização automática** dos códigos a cada 30 segundos.
- **Copiar com um clique** - token copiado para área de transferência.
- **Cross-platform** - Windows, Linux e macOS.
- **Interface responsiva** com barra de progresso visual.
- **Múltiplas contas** com organização por emissor.
- **Sincronização de tempo** precisa para códigos válidos.
- **Banco local SQLite** para persistência dos dados.

## Instalação Rápida

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório
```bash
git clone https://github.com/Codeplay77/OTP-pyAuth.git
cd OTP-pyAuth
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Execute o aplicativo
```bash
python main.py
```

## 📦 Compilação para Executável

### Windows
```bash
# Compilar para .exe
build.bat
```

### Linux/macOS
```bash
# Dar permissão e compilar
chmod +x build.sh
./build.sh
```

O executável será criado em `dist/PythonAuthenticator.exe` (~15-25 MB).

## Como Usar

### Adicionar uma nova conta

1. **Clique em "Adicionar conta"**
2. **Preencha os dados:**
   - **Nome da conta:** `usuario@gmail.com`
   - **Emissor:** `Google` (opcional)
   - **Chave secreta:** `JBSWY3DPEHPK3PXP...`
3. **Clique em "Adicionar conta"**

### Obter códigos 2FA

- Os códigos são **atualizados automaticamente** a cada 30 segundos
- **Clique no código** ou no ícone 📋 para copiar
- A **barra de progresso** mostra o tempo restante
- Códigos ficam **vermelhos** quando estão prestes a expirar

### Gerenciar contas

- **Remover conta:** Clique no ✖ e confirme
- **Copiar código:** Clique no número ou no ícone 📋
- **Visualizar tempo:** Barra de progresso e contador

## Configuração Avançada

### Estrutura de arquivos

```
python-authenticator/
├── main.py                # Arquivo principal
├── authenticator_app.py   # Interface principal
├── database.py            # Gerenciamento de dados
├── totp_generator.py      # Geração de códigos TOTP
├── token_widget.py        # Widget de cada token
├── add_account_dialog.py  # Diálogo de adição
├── build.bat              # Script de compilação Windows
├── build.sh               # Script de compilação Linux/Mac
├── requirements.txt       # Dependências
├── authenticator.db       # Banco de dados (criado automaticamente)
├── key.key                # Chave de criptografia (criado automaticamente)
└── icon.ico               # Ícone do aplicativo
```

### Arquivos importantes

- **`authenticator.db`** - Banco SQLite com as contas (criptografadas)
- **`key.key`** - Chave mestra para criptografia AES
- **Faça backup** destes arquivos para não perder suas contas!

## Segurança

### Criptografia
- **AES-256** para criptografia das chaves secretas
- **Chave mestra** gerada aleatoriamente e armazenada localmente
- **Banco SQLite** protegido com dados criptografados

### Boas práticas
- Chaves secretas **nunca** armazenadas em texto plano
- Algoritmo **TOTP padrão** (RFC 6238)
- Sincronização de tempo **automática**
- Validação de entrada para **chaves inválidas**

### Limitações de segurança
- Chave mestra armazenada no mesmo local do banco
- Sem proteção por senha mestre
- Sem sincronização na nuvem

## Desenvolvimento

### Tecnologias utilizadas

- **Python 3.7+** - Linguagem principal
- **Tkinter** - Interface gráfica nativa
- **PyOTP** - Geração de códigos TOTP
- **Cryptography** - Criptografia AES
- **SQLite3** - Banco de dados local
- **Pillow** - Manipulação de imagens (ícone)

### Contribuindo

1. **Fork** o repositório
2. **Crie uma branch** para sua feature (`git checkout -b feature/nova-feature`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/nova-feature`)
5. **Abra um Pull Request**

### Reportar bugs

Use as [Issues do GitHub](../../issues) para reportar bugs ou sugerir melhorias.

### Plataformas
- **Windows** 10/11 (executável .exe)
- **Linux** (Ubuntu, Debian, Fedora, etc.)
- **macOS** (Intel e Apple Silicon)

## Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](license) para detalhes.

## 🙏 Agradecimentos

- **PyOTP** - Biblioteca para geração de códigos TOTP
- **Google Material Design** - Inspiração para o design
- **Google Authenticator** - Referência de funcionalidades
- **Comunidade Python** - Suporte e bibliotecas

<div align="center">

**Se este projeto foi útil para você, considere dar uma estrela!**
</div>