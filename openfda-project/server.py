import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True
import requests


IP = "localhost"
PORT = 8000

def active_ingredient_url(active_ingredient,limit):
    url =  "https://api.fda.gov/drug/label.json?search=active_ingredient:" + active_ingredient + "&limit=" + str(limit)
    return url

def get_active_ingredient(url):
    data = requests.get(url).json()
    drug_list = []
    for results in data['results']:
        try:
            drug_list.append(results['openfda']['generic_name'])
        except KeyError:
            drug_list.append(' ')
    return drug_list

def company_url (company, limit):
    url = "https://api.fda.gov/drug/ndc.json?search=openfda.manufacturer_name:" + company + "&limit=" + str(limit)
    return url

def get_company(url):
    data = requests.get(url).json()
    company_list = []
    results = data['results']
    for result in results:
        try:
            company_list.append(result['openfda']['manufacturer_name'])
        except KeyError:
            company_list.append(' ')
    return company_list

def list_html(list):
    inicio = """
      <!DOCTYPE html>
      <html>
        <title>mariaferagui</title>
      <body>
      <h2>Result of your search</h2>
      """
    final = """
      </ul>
      </body>
      </html>"""
    cuerpo = ''
    for item in list:
        cuerpo += '  <li type="square">' + str(item) + '</li>' + '\n'
    message = inicio + '\n' + cuerpo + final
    return message

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        path = self.path

        if path.startswith("/searchDrug?active_ingredient="):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            active_ingredient = path.split('=')[1].split('&')[0]
            try:
                limit = path.split('=')[2]
                message = list_html(get_active_ingredient(active_ingredient_url(active_ingredient, str(limit))))
            except IndexError:
                message = list_html(get_active_ingredient(active_ingredient_url(active_ingredient, str(10))))

        elif path.startswith("/searchCompany?company="):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            company = path.split('=')[1].split('&')[0]
            try:
                limit = path.split('=')[2]
                message = list_html(get_company(company_url(company, limit)))
            except IndexError:
                message = list_html(get_company(company_url(company, str(10))))

        elif path.startswith("/listDrugs"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                limit = path.split('=')[1]
                url = "https://api.fda.gov/drug/ndc.json?count=generic_name.exact&limit=" + str(limit)
            except IndexError:
                url = "https://api.fda.gov/drug/ndc.json?count=generic_name.exact"
            data = requests.get(url).json()
            listdrugs = []
            for results in data['results']:
                try:
                    listdrugs.append(results['term'])
                except KeyError:
                    continue
            message = list_html(listdrugs)

        elif path.startswith("/listCompanies"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                limit = path.split('=')[1]
                url = "https://api.fda.gov/drug/ndc.json?count=openfda.manufacturer_name.exact&limit=" + str(limit)
            except IndexError:
                url = "https://api.fda.gov/drug/ndc.json?count=openfda.manufacturer_name.exact"
            data = requests.get(url).json()
            listcompanies = []
            for results in data['results']:
                try:
                    listcompanies.append(results['term'])
                except KeyError:
                    continue
            message = list_html(listcompanies)

        elif path.startswith('/listWarnings'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                limit = path.split('=')[1]
                url = "https://api.fda.gov/drug/label.json?search=openfda.product_type:vegetal compounded drug label&limit=" + str(limit)
            except IndexError:
                url = "https://api.fda.gov/drug/label.json?search=openfda.product_type:vegetal compounded drug label&limit=20"
            data = requests.get(url).json()
            listwarnings = []
            for results in data['results']:
                try:
                    listwarnings.append(results['warnings'])
                except KeyError:
                    listwarnings.append(results['warnings_and_cautions'])
            message = list_html(listwarnings)

        elif path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("form.html","r") as f:
                message = f.read()

        elif path == '/secret':
            self.send_response(401)
            self.send_header('WWW-Authenticate:Basic', 'realm="nmrs_m7VKmomQ2YM3"')
            self.end_headers()
            message = list_html(['UNAUTHORIZED'])

        elif path == '/redirect':
            location = 'http://' + 'localhost' + ':' + str(PORT)
            self.send_response(302)
            self.send_header('Location', location)
            self.end_headers()
            message = ''

        else:
            self.send_response(404)
            self.send_header('WWW-Authenticate:Basic', 'realm="nmrs_m7VKmomQ2YM3"')
            self.end_headers()
            message = list_html(['ERROR 404, NOT FOUND'])

        self.wfile.write(bytes(message, "utf8"))
        print("File served!")
        return

Handler = testHTTPRequestHandler

httpd = socketserver.TCPServer((IP, PORT), Handler)
print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
        pass

httpd.server_close()
print("")
print("Server stopped!")
