import subprocess
from jinja2 import Template
import requests

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def get_subdomains(domain):
    subfinder_output = run_command(f"subfinder -d {domain} -silent")
    assetfinder_output = run_command(f"assetfinder --subs-only {domain}")

    subdomains = set(subfinder_output.splitlines()) | set(assetfinder_output.splitlines())
    return subdomains

def get_http_status(subdomain):
    try:
        response = requests.get(f"http://{subdomain}", timeout=5)
        return response.status_code
    except requests.exceptions.RequestException:
        return "N/A"

def run_wafw00f(subdomains):
    waf_results = []
    for subdomain in subdomains:
        output = run_command(f"wafw00f {subdomain}")
        waf_results.append({"subdomain": subdomain, "waf_output": output})
    return waf_results

def generate_html_report(template_str, data, output_file):
    template = Template(template_str)
    report = template.render(data)
    with open(output_file, "w") as f:
        f.write(report)

def main():
    domain = input("Digite o domínio: ")
    subdomains = get_subdomains(domain)
    print(f"Subdomínios encontrados para {domain}:")
    for subdomain in subdomains:
        print(subdomain)

    waf_results = run_wafw00f(subdomains)

    http_status_results = []
    for subdomain in subdomains:
        status_code = get_http_status(subdomain)
        http_status_results.append({"subdomain": subdomain, "http_status": status_code})

    waf_template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Relatório WAF</title>
</head>
<body>
    <h1>Relatório WAF</h1>
    <table>
        <tr>
            <th>Subdomínio</th>
            <th>WAF</th>
        </tr>
        {% for result in waf_results %}
        <tr>
            <td>{{ result.subdomain }}</td>
            <td>{{ result.waf_output | replace("\n", "<br>") }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

    http_status_template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Status HTTP</title>
</head>
<body>
    <h1>Relatório de Status HTTP</h1>
    <table>
        <tr>
            <th>Subdomínio</th>
            <th>Status HTTP</th>
        </tr>
        {% for result in http_status_results %}
        <tr>
            <td>{{ result.subdomain }}</td>
            <td>{{ result.http_status }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

    generate_html_report(waf_template_str, {"waf_results": waf_results}, "waf_report.html")
    generate_html_report(http_status_template_str, {"http_status_results": http_status_results}, "http_status_report.html")
    print("\nRelatórios gerados como waf_report.html e http_status_report.html")

if __name__ == "__main__":
    main()
