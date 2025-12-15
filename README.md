# Fronteira-Eficiente

# 📈 Simulação de Portfólios – Fronteira Eficiente (Monte Carlo)

Este projeto foi desenvolvido como **atividade complementar ao curso de Finanças II**, do curso de **Economia da PUC-Rio**, durante o **primeiro período letivo de 2025**.

O trabalho tem como objetivo aplicar, de forma prática, os conceitos estudados na disciplina relacionados à **Teoria Moderna do Portfólio**, em especial a análise da relação entre **risco, retorno e diversificação**, conforme proposto por Harry Markowitz.

---

## 🎯 Objetivo do Projeto

A aplicação permite simular carteiras de ativos financeiros a partir de dados históricos e visualizar a **fronteira eficiente**, identificando portfólios ótimos segundo diferentes critérios econômicos.

Em particular, o projeto possibilita:
- A construção de múltiplas carteiras por meio de **simulação de Monte Carlo**
- A visualização do trade-off risco-retorno
- A identificação de:
  - Portfólio de **Máximo Índice de Sharpe**
  - Portfólio de **Mínima Volatilidade**
  - Portfólio **1/N (alocação igualmente ponderada)**

---

## 🧠 Metodologia

- Os dados de preços históricos são obtidos a partir do **Yahoo Finance**
- Os retornos e a matriz de covariância são anualizados considerando 252 pregões por ano
- São geradas milhares de combinações aleatórias de pesos, respeitando a restrição de alocação total do capital
- Cada carteira é avaliada com base em retorno esperado, volatilidade e Índice de Sharpe
- Os resultados são apresentados graficamente por meio da fronteira eficiente

O modelo considera:
- Pesos não negativos (ausência de short selling)
- Soma dos pesos igual a 1

---

## 🛠️ Tecnologias Utilizadas

- **Python**
- **Streamlit** (interface interativa)
- **Pandas** e **NumPy** (manipulação de dados e cálculos estatísticos)
- **Plotly** (visualização gráfica)
- **yFinance** (obtenção de dados financeiros)

---

## ▶️ Execução do Projeto

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🤖 Uso de Inteligência Artificial como Ferramenta de Apoio

O desenvolvimento deste projeto contou com o uso de ferramentas de Inteligência Artificial (ChatGPT) como apoio ao processo de aprendizado e implementação, especialmente nas etapas de:

- Estruturação do código
- Organização das funções
- Esclarecimento de dúvidas técnicas e conceituais

A definição do escopo do projeto, a escolha da metodologia econômica, a interpretação dos resultados e a adequação do modelo aos conteúdos abordados na disciplina de Finanças II foram realizadas pelo autor, em consonância com os objetivos acadêmicos do curso.



