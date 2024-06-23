import random
import time
from geopy.distance import geodesic
import folium
from datetime import datetime
import osmnx as ox
import networkx as nx
import warnings

cerca_eletronica = (-15.863270924011779, -48.02967536492849)
raio_cerca = 250

min_lat = -15.5
max_lat = -16.0
min_lon = -47.5
max_lon = -48.2

def gerar_coordenadas():
    latitude = round(random.uniform(min_lat, max_lat), 6)
    longitude = round(random.uniform(min_lon, max_lon), 6)
    return [latitude, longitude]

def dentro_cerca(coordenadas, cerca, raio):
    return geodesic(coordenadas, cerca).meters <= raio

def gerar_dados_sensor():
    return {
        "Velocidade (km/h)": random.randint(0, 90),
        "Temperatura do Motor (°C)": random.randint(60, 100),
        "Pressão do Óleo (bar)": random.randint(1, 5),
        "Nível de Combustível (%)": random.randint(1, 100),
        "Pressão dos Pneus (PSI)": random.randint(20, 40),
        "Nível de Fluidos (%)": random.randint(1, 100),
        "Emissões (%)": random.randint(1, 100),
        "Oxigênio (%)": random.randint(1, 100),
        "Nível de Carga (kg)": random.randint(1000, 10000),
        "Nome do Motorista": random.choice(["João", "Maria", "Pedro", "Ana"]),
        "Carga Carregada": random.choice(["Alimentos", "Produtos Químicos", "Materiais Perigosos"]),
        "Nível de Periculosidade da Carga": random.randint(1, 10),
    }

def plotar_mapa(caminhoes, cerca_eletronica, raio_cerca, graph, ponto_inicial, rotas, pontos_finais):
    mapa = folium.Map(location=cerca_eletronica, zoom_start=13)
    
    folium.Circle(
        location=cerca_eletronica,
        radius=raio_cerca,
        color='darkblue',
        fill=True, 
        fill_color='darkblue',
        fill_opacity=0.2
    ).add_to(mapa)

    folium.Marker(location=ponto_inicial, popup='Centro de Distribuição', tooltip='Centro de Distribuição', icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(mapa)

    for i, caminhao in enumerate(caminhoes):
        dados_sensor = caminhao["dados_sensor"]
        popup_html = f"<b>{caminhao['nome']}</b><br><br>"
        popup_html += "<b>Dados do Caminhão</b><br>"
        popup_html += f"<b>Data e Hora:</b> {caminhao['timestamp']}<br>"
        for sensor, valor in dados_sensor.items():
            popup_html += f"<b>{sensor}:</b> {valor}<br>"
        folium.Marker(caminhao["coordenadas"], popup=folium.Popup(popup_html, max_width=300), icon=folium.Icon(color='blue', icon='truck', prefix='fa')).add_to(mapa)
        
        rota = rotas[i]
        coordenadas_rota = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in rota]
        folium.PolyLine(locations=coordenadas_rota, color='darkblue').add_to(mapa)

        folium.Marker(location=pontos_finais[i], tooltip='Destino',icon=folium.Icon(color='blue', icon='building', prefix='fa')).add_to(mapa)

    nome_arquivo = 'Map.html'
    mapa.save(nome_arquivo)
    
    with open(nome_arquivo, 'r') as file:
        conteudo_html = file.read()
    
    conteudo_html += """
    <script>
    setTimeout(function() {
        location.reload();
    }, 5000);
    </script>
    """

    with open(nome_arquivo, 'w') as file:
        file.write(conteudo_html) 

# Main
if __name__ == "__main__":
    ponto_inicial = (-15.863270924011779, -48.02967536492849)
    rotas = []
    pontos_finais = [(-15.62403952236645, -47.65546522150698),
                    (-15.834889743434303, -47.91683189063775),  
                    (-15.869912308549146, -47.9090695366498),       
                    (-15.89518344555868, -48.14804940119952),        
                    (-15.663946353847557, -48.10916958102042)]        

    bbox = (min_lat, max_lat, min_lon, max_lon)
    warnings.filterwarnings("ignore", category=FutureWarning)
    graph = ox.graph_from_bbox(bbox=bbox, network_type='walk')

    for ponto_final in pontos_finais:
        no_inicial = ox.nearest_nodes(graph, ponto_inicial[1], ponto_inicial[0])
        no_final = ox.nearest_nodes(graph, ponto_final[1], ponto_final[0])
        rota = nx.shortest_path(graph, no_inicial, no_final, weight='length')
        rotas.append(rota)

    caminhoes = []
    for i, rota in enumerate(rotas):
        caminhao = {
            "nome": f"Caminhão {i+1}",
            "coordenadas": (graph.nodes[rota[0]]['y'], graph.nodes[rota[0]]['x']),
            "dados_sensor": gerar_dados_sensor(),
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "rota": rota,
        }
        caminhoes.append(caminhao)

    try:
        while True:
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print(f"Leitura realizada em: {timestamp}\n")

            print(f"Dados dos sensores dos caminhões:")
            for caminhao in caminhoes:
                caminhao["dados_sensor"]["Velocidade (km/h)"] = random.randint(0, 90)
                print(f"\n{caminhao['nome']}:")
                print(f"\nCoordenadas: {caminhao['coordenadas']}")
                print(f"Data e Hora: {caminhao['timestamp']}")
                for sensor, valor in caminhao["dados_sensor"].items():
                    print(f"{sensor}: {valor}")
                print()

            dentro_cerca_count = sum(1 for caminhao in caminhoes if dentro_cerca(caminhao["coordenadas"], cerca_eletronica, raio_cerca))
            if dentro_cerca_count == 1:
                print(f"\n 1 caminhão está dentro da cerca eletrônica.")
            else:
                print(f"\n{dentro_cerca_count} caminhões estão dentro da cerca eletrônica.")

            plotar_mapa(caminhoes, cerca_eletronica, raio_cerca, graph, ponto_inicial, rotas, pontos_finais)

            for caminhao in caminhoes:

                proximo_no = caminhao['rota'][1]

                caminhao["coordenadas"] = graph.nodes[proximo_no]['y'], graph.nodes[proximo_no]['x']

                caminhao["timestamp"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                if caminhao['coordenadas'] == (graph.nodes[proximo_no]['y'], graph.nodes[proximo_no]['x']):
                    caminhao['rota'] = caminhao['rota'][1:]

            time.sleep(5)
    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário.")
