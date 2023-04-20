import requests
from bs4 import BeautifulSoup

# Defina o caminho para o arquivo da wordlist, o domínio e os arquivos robots.txt e sitemap.xml
wordlist_file = 'wordlist.txt'
domain = input("Digite o domínio que deseja testar (exemplo: https://www.example.com/): ").strip()
robots_txt = f'{domain}robots.txt'
sitemap = f'{domain}sitemap.xml'

# Função para verificar o HTTP Status
def check_http_status(url, verbose=False):
    if verbose:
        print(f"Testando: {url}")

    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException as e:
        return f"Erro: {e}"

# Função para extrair links do sitemap.xml
def extract_links_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, 'lxml-xml')
    links = [loc.text for loc in soup.find_all('loc')]
    return links

# Função para extrair links do robots.txt
def extract_links_from_robots_txt(robots_txt_url):
    response = requests.get(robots_txt_url)
    lines = response.text.split('\n')
    links = [line.split(':')[1].strip() for line in lines if line.startswith('Disallow')]
    return links

# Função para gerar o relatório HTML
def generate_html_report(wordlist, robots_txt_links, sitemap_links, output_file='report.html'):
    with open(output_file, 'w') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en">\n')
        f.write('<head>\n')
        f.write('<meta charset="UTF-8">\n')
        f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        f.write('<title>Relatório de Crawler</title>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('<h1>Relatório de Crawler</h1>\n')

        f.write('<h2>Links da Wordlist</h2>\n')
        f.write('<ul>\n')
        for word in wordlist:
            url = f'{domain}{word}'
            status = check_http_status(url)
            f.write(f'<li><a href="{url}">{url}</a> - HTTP Status: {status}</li>\n')
        f.write('</ul>\n')

        f.write('<h2>Links do Robots.txt</h2>\n')
        f.write('<ul>\n')
        for link in robots_txt_links:
            url = f'{domain}{link}'
            status = check_http_status(url)
            f.write(f'<li><a href="{url}">{url}</a> - HTTP Status: {status}</li>\n')
        f.write('</ul>\n')

        f.write('<h2>Links do Sitemap.xml</h2>\n')
        f.write('<ul>\n')
        for link in sitemap_links:
            status = check_http_status(link)
            f.write(f'<li><a href="{link}">{link}</a> - HTTP Status: {status}</li>\n')
        f.write('</ul>\n')

        f.write('</body>\n')
        f.write('</html>\n')

# Carrega a wordlist do arquivo
with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
    wordlist = [line.strip() for line in f.readlines()]

# Extrai os links do sitemap.xml e robots.txt
sitemap_links = extract_links_from_sitemap(sitemap)
robots_txt_links = extract_links_from_robots_txt(robots_txt)

# Gera o relatório HTML
generate_html_report(wordlist, robots_txt_links, sitemap_links, output_file='report.html')
