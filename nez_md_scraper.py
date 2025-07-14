import requests
from bs4 import BeautifulSoup
import html2text
from datetime import datetime

# Keep ALL your original classes exactly as they are:
class ExtractorNezBistro:
    """Classe responsável por extrair informações do site do Nez Bistrô"""
    
    def __init__(self, url):
        self.url = url
        self.soup = None
        self._carregar_pagina()
    
    def _carregar_pagina(self):
        """Carrega e parseia a página HTML"""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise Exception(f"Erro ao carregar a página: {e}")
    
    def extrair_introducao_restaurante(self):
        """Extrai a introdução/descrição do restaurante"""
        introducao = ""
        
        # Procurar no primeiro container
        primeiro_container = self.soup.find('div', class_='container')
        if primeiro_container:
            div_intro = primeiro_container.find('div', class_='introtext')
            if div_intro:
                introducao = self._processar_paragrafos(div_intro)
                if introducao:
                    return introducao
        
        # Buscar em containers que não sejam de menu
        containers = self.soup.find_all('div', class_='container')
        for container in containers:
            intro_divs = container.find_all('div', class_='introtext')
            for intro_div in intro_divs:
                if not intro_div.find_parent('table'):
                    introducao = self._processar_paragrafos(intro_div, min_length=50)
                    if introducao:
                        return introducao
        
        return introducao
    
    def extrair_menu_completo(self):
        """Extrai todas as seções do menu do restaurante"""
        menu_markdown = ""
        containers = self.soup.find_all('div', class_='container')
        
        for container in containers:
            linhas_menu = container.find_all('tr')
            
            for linha in linhas_menu:
                classes = linha.get('class', [])
                
                if 'linha-grupo' in classes:
                    menu_markdown += self._extrair_secao_menu(linha)
                elif 'linha-prato' in classes:
                    menu_markdown += self._extrair_item_menu(linha)
        
        return menu_markdown
    
    def extrair_informacoes_contato(self):
        """Extrai informações de contato e funcionamento"""
        info_markdown = ""
        
        secao_info = self.soup.find('div', id='info')
        if not secao_info:
            return info_markdown
        
        info_markdown += "## Informações do Restaurante\n\n"
        
        detalhes_contato = self.soup.find_all('div', class_='contactDetails')
        
        for contato in detalhes_contato:
            info_markdown += self._extrair_endereco(contato)
            info_markdown += self._extrair_telefones(contato)
            info_markdown += self._extrair_email(contato)
            info_markdown += self._extrair_horarios_pagamento(contato)
        
        return info_markdown
    
    def extrair_redes_sociais(self):
        """Extrai links das redes sociais"""
        redes_markdown = ""
        
        links_sociais = self.soup.find('ul', class_='socialLinks')
        if links_sociais:
            redes_markdown += "**Redes Sociais:**\n"
            links = links_sociais.find_all('a')
            
            for link in links:
                href = link.get('href')
                titulo = link.get('title')
                if href and titulo:
                    redes_markdown += f"- [{titulo}]({href})\n"
            redes_markdown += "\n"
        
        return redes_markdown
    
    def _processar_paragrafos(self, elemento, min_length=0):
        """Processa parágrafos de um elemento HTML"""
        paragrafos = elemento.find_all('p')
        texto = ""
        
        for p in paragrafos:
            texto_paragrafo = p.get_text().strip()
            if texto_paragrafo and len(texto_paragrafo) > min_length:
                texto += f"{texto_paragrafo}\n\n"
        
        return texto
    
    def _extrair_secao_menu(self, linha):
        """Extrai cabeçalho de seção do menu"""
        secao_markdown = ""
        
        titulo_secao = linha.find('h1')
        if titulo_secao:
            nome_secao = titulo_secao.get_text().strip()
            secao_markdown += f"\n## {nome_secao}\n\n"
            
            # Verificar descrição da seção
            intro_secao = linha.find('div', class_='introtext')
            if intro_secao:
                desc_secao = intro_secao.find('h3')
                if desc_secao:
                    texto_desc = desc_secao.get_text().strip()
                    if texto_desc:
                        secao_markdown += f"*{texto_desc}*\n\n"
        
        return secao_markdown
    
    def _extrair_item_menu(self, linha):
        """Extrai item individual do menu"""
        item_markdown = ""
        
        celula_item = linha.find('td')
        if not celula_item:
            return item_markdown
        
        # Nome do item
        nome_item = celula_item.find('h4')
        if nome_item:
            texto_nome = nome_item.get_text().strip()
            item_markdown += f"### {texto_nome}\n"
        
        # Descrição
        descricao = celula_item.find('h5')
        if descricao:
            texto_desc = descricao.get_text().strip()
            if texto_desc:
                item_markdown += f"{texto_desc}\n"
        
        # Preço
        preco = celula_item.find('h9')
        if preco:
            texto_preco = preco.get_text().strip()
            if texto_preco:
                item_markdown += f"**Preço:** {texto_preco}\n"
        
        item_markdown += "\n"
        return item_markdown
    
    def _extrair_endereco(self, contato):
        """Extrai endereço do restaurante"""
        endereco_markdown = ""
        
        endereco = contato.find('p', class_='contactAddress')
        if endereco:
            texto_endereco = endereco.get_text().strip()
            if texto_endereco and 'Praça' in texto_endereco:
                endereco_markdown += f"**Endereço:**\n{texto_endereco}\n\n"
        
        return endereco_markdown
    
    def _extrair_telefones(self, contato):
        """Extrai números de telefone"""
        telefone_markdown = ""
        
        telefones = contato.find_all('p', class_='contactPhone')
        if telefones:
            telefone_markdown += "**Contato:**\n"
            for telefone in telefones:
                texto_telefone = telefone.get_text().strip()
                if texto_telefone:
                    telefone_markdown += f"{texto_telefone}\n"
            telefone_markdown += "\n"
        
        return telefone_markdown
    
    def _extrair_email(self, contato):
        """Extrai email do restaurante"""
        email_markdown = ""
        
        email = contato.find('p', class_='contactEmail')
        if email:
            texto_email = email.get_text().strip()
            if texto_email:
                email_markdown += f"**Email:** {texto_email}\n\n"
        
        return email_markdown
    
    def _extrair_horarios_pagamento(self, contato):
        """Extrai horários de funcionamento e formas de pagamento"""
        info_markdown = ""
        
        info_horario = contato.find('p', class_='contactTime')
        if info_horario:
            pai_horario = info_horario.parent
            conteudo_horario = pai_horario.get_text().strip()
            
            if 'Funcionamento' in conteudo_horario:
                info_markdown += f"**Horário de Funcionamento:**\n{conteudo_horario}\n\n"
            elif 'Formas de pagamento' in conteudo_horario:
                info_markdown += f"**Formas de Pagamento:**\n{conteudo_horario}\n\n"
        
        return info_markdown


class GeradorMarkdown:
    """Classe responsável por gerar o arquivo markdown final"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def gerar_markdown_completo(self):
        """Gera o markdown completo do restaurante"""
        markdown = "# Nez Bistrô\n\n"
        
        # Adicionar introdução
        introducao = self.extractor.extrair_introducao_restaurante()
        if introducao:
            markdown += "## Sobre o Restaurante\n\n"
            markdown += introducao
        
        # Adicionar menu
        menu = self.extractor.extrair_menu_completo()
        markdown += menu
        
        # Adicionar informações de contato
        contato = self.extractor.extrair_informacoes_contato()
        markdown += contato
        
        # Adicionar redes sociais
        redes = self.extractor.extrair_redes_sociais()
        markdown += redes
        
        return markdown


def main():
    """Função principal - versão para n8n que outputa conteúdo diretamente"""
    url = 'https://www.menudigital.app.br/nez/'
    
    try:
        # Usar toda sua lógica original completa
        extractor = ExtractorNezBistro(url)
        gerador = GeradorMarkdown(extractor)
        
        # Gerar markdown completo com TODA a informação
        markdown_completo = gerador.gerar_markdown_completo()
        
        # Print markdown to stdout
        print(markdown_completo)
        
    except Exception as e:
        print(f"ERRO na extração: {e}")


if __name__ == "__main__":
    main()
