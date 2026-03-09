# Rastreamento de Ônibus em Tempo Real 🚌

**Coleta, tratamento e visualização de dados GPS de ônibus do Rio de Janeiro via API pública.**

---

## 📡 Sobre o Projeto

Pipeline completo de **Extração e Preparação de Dados** que consome em tempo real a API GPS do sistema SPPO (Mobilidade Rio), processa mais de **41 mil registros** de posicionamento e gera mapas interativos com as trajetórias dos ônibus em circulação na cidade.

---

## ⚙️ O que o projeto faz

- 🔗 **Coleta** dados ao vivo da API pública `dados.mobilidade.rio`
- 🧹 **Trata** inconsistências: converte coordenadas em string para float, e timestamps UNIX (ms) para datetime legível
- 🗺️ **Filtra** por linha de ônibus e plota as trajetórias em um mapa interativo com **Folium**
- 📊 **Calcula** distância total percorrida e velocidade média por veículo

---

## 🛠️ Tecnologias

`Python` • `Pandas` • `Folium` • `Google Colab` • `REST API`

---

## 📊 Dados da última execução

| Métrica | Valor |
|---|---|
| Total de registros | 41.792 |
| Linhas de ônibus | 400 |
| Veículos únicos | 3.696 |
| Janela de tempo | 5 minutos |

---

> Projeto desenvolvido para a disciplina de **Extração e Preparação de Dados**.
