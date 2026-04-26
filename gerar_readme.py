import os
import json
import re
from pathlib import Path

def slugify(text):
    """
    Cria um slug (identificador amigável) a partir do texto.
    Útil para links âncora.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def carregar_conteudos_json(caminho_pasta):
    """
    Carrega o arquivo conteudos.json da pasta, se existir.
    Retorna uma lista de conteúdos ou None se não existir.
    """
    json_path = os.path.join(caminho_pasta, 'conteudos.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                conteudos = json.load(f)
                # Garantir que é uma lista
                if isinstance(conteudos, list):
                    return conteudos
                else:
                    print(f"  Aviso: {json_path} não é uma lista. Ignorando.")
                    return None
        except json.JSONDecodeError as e:
            print(f"  Erro ao ler {json_path}: {e}. Ignorando.")
            return None
    return None

def obter_conteudos_ordenados(caminho_pasta):
    """
    Obtém a lista de conteúdos de uma pasta, priorizando o arquivo JSON.
    Se o JSON existir, usa order do JSON.
    Se não, usa a ordem alfabética dos arquivos .md.
    """
    # Tentar carregar do JSON primeiro
    conteudos_json = carregar_conteudos_json(caminho_pasta)
    
    if conteudos_json:
        # Filtrar apenas conteúdos que têm arquivo .md correspondente
        arquivos_md = set([f.replace('.md', '') for f in os.listdir(caminho_pasta) if f.endswith('.md')])
        
        conteudos_validos = []
        for item in conteudos_json:
            # Verificar se existe arquivo .md correspondente (pelo slug ou id)
            slug_arquivo = item.get('slug', item.get('id', ''))
            if slug_arquivo in arquivos_md or item.get('id') in arquivos_md:
                conteudos_validos.append(item)
            else:
                print(f"  Aviso: Conteúdo '{item.get('title', 'sem título')}' não tem arquivo .md correspondente. Ignorando.")
        
        # Ordenar pelo campo 'order'
        conteudos_validos.sort(key=lambda x: x.get('order', 999999))
        return conteudos_validos
    
    # Fallback: usar arquivos .md diretamente (ordem alfabética)
    arquivos_md = sorted([f for f in os.listdir(caminho_pasta) if f.endswith('.md')])
    conteudos_fallback = []
    for arquivo in arquivos_md:
        nome_sem_extensao = os.path.splitext(arquivo)[0]
        conteudos_fallback.append({
            'id': nome_sem_extensao,
            'title': nome_sem_extensao.replace('-', ' ').title(),
            'slug': nome_sem_extensao,
            'order': 999999  # ordem alta para ficar no final
        })
    return conteudos_fallback

def gerar_readme(diretorio_base='.'):
    """
    Gera o README.md com base na estrutura de pastas do repositório
    e nos arquivos conteudos.json.
    """
    linhas_readme = [
        "# 📚 Conteúdos do Projeto IF Prática Ativa\n\n",
        "Bem-vindo ao repositório de conteúdos! Aqui você encontrará materiais organizados por disciplina/tema.\n\n",
        "## 📑 Tabela de Conteúdos\n\n"
    ]

    items_toc = []
    
    # Ordena as pastas alfabeticamente
    pastas = sorted([pasta for pasta in os.listdir(diretorio_base) 
                     if os.path.isdir(os.path.join(diretorio_base, pasta)) 
                     and pasta not in ['.git', '.github', '__pycache__']])

    for pasta in pastas:
        caminho_pasta = os.path.join(diretorio_base, pasta)
        
        # Obter conteúdos ordenados
        conteudos = obter_conteudos_ordenados(caminho_pasta)
        
        if not conteudos:
            print(f"Aviso: Nenhum conteúdo encontrado na pasta '{pasta}'. Ela não aparecerá no README.")
            continue

        # Adiciona o item da disciplina ao TOC principal
        slug_pasta = slugify(pasta)
        linhas_readme.append(f"- [{pasta}](#{slug_pasta})\n")
        items_toc.append((pasta, slug_pasta))

        # Adiciona o cabeçalho da disciplina no corpo do README
        linhas_readme.append(f"## <a id='{slug_pasta}'></a> {pasta}\n\n")

        # Adiciona a tabela de conteúdos da disciplina
        linhas_readme.append("| Conteúdo | Descrição |\n")
        linhas_readme.append("|----------|-----------|\n")
        
        for conteudo in conteudos:
            titulo = conteudo.get('title', 'Sem título')
            slug = conteudo.get('slug', conteudo.get('id', ''))
            arquivo_md = f"{slug}.md"
            
            # Verificar se o arquivo realmente existe
            if not os.path.exists(os.path.join(caminho_pasta, arquivo_md)):
                # Tentar com id
                arquivo_md = f"{conteudo.get('id', '')}.md"
                if not os.path.exists(os.path.join(caminho_pasta, arquivo_md)):
                    print(f"  Aviso: Arquivo {arquivo_md} não encontrado para '{titulo}'")
                    continue
            
            # Criar link para o arquivo
            link = f"{pasta}/{arquivo_md}"
            descricao = conteudo.get('description', f'Conteúdo sobre {titulo.lower()}')
            
            # Adicionar linha da tabela
            linhas_readme.append(f"| [{titulo}]({link}) | {descricao} |\n")
        
        linhas_readme.append("\n---\n\n")  # Separador entre disciplinas

    # Adicionar rodapé
    linhas_readme.append("\n---\n\n")
    linhas_readme.append("## 📝 Como usar este repositório\n\n")
    linhas_readme.append("1. Navegue pelos links da tabela acima para acessar os conteúdos\n")
    linhas_readme.append("2. Cada arquivo `.md` contém o material de estudo\n")
    linhas_readme.append("3. Os conteúdos estão organizados por ordem de estudo recomendada\n")
    linhas_readme.append("\n---\n\n")
    linhas_readme.append("*Este README é gerado automaticamente. Para atualizá-lo, execute o script `gerar_readme.py`.*\n")

    # Escreve o arquivo README.md
    readme_path = os.path.join(diretorio_base, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.writelines(linhas_readme)

    print(f"✅ README.md gerado com sucesso em: {readme_path}")

def criar_exemplo_conteudos_json(caminho_pasta):
    """
    Função auxiliar para criar um arquivo conteudos.json de exemplo.
    """
    json_path = os.path.join(caminho_pasta, 'conteudos.json')
    if not os.path.exists(json_path):
        exemplo = [
            {
                "id": "exemplo-1",
                "title": "Exemplo de Conteúdo 1",
                "slug": "exemplo-1",
                "order": 1,
                "description": "Descrição do primeiro conteúdo"
            },
            {
                "id": "exemplo-2", 
                "title": "Exemplo de Conteúdo 2",
                "slug": "exemplo-2",
                "order": 2,
                "description": "Descrição do segundo conteúdo"
            }
        ]
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(exemplo, f, indent=2, ensure_ascii=False)
        print(f"✅ Exemplo de conteudos.json criado em: {json_path}")

if __name__ == "__main__":
    # Opcional: criar exemplos de arquivos JSON para ajudar
    # criar_exemplo_conteudos_json('python')
    
    # Gerar o README
    gerar_readme('.')
